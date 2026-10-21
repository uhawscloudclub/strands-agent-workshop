"""
Steering handlers for the customer service agent deployment.
"""

import re
from strands.vended_plugins.steering import (
    SteeringHandler, LLMSteeringHandler,
    Proceed, Guide, ToolSteeringAction,
    LedgerProvider,
)


class RefundWorkflowHandler(SteeringHandler):
    """Deterministic handler: enforce refund workflow ordering.

    Rules:
    1. Must look up the customer before processing a refund
    2. Must check order history before processing a refund
    """

    name = "refund-workflow"

    def __init__(self):
        super().__init__(context_providers=[LedgerProvider()])

    async def steer_before_tool(self, *, agent, tool_use, **kwargs) -> ToolSteeringAction:
        if tool_use.get("name") != "process_refund":
            return Proceed(reason="Not a refund operation")

        ledger = self.steering_context.data.get("ledger") or {}
        tool_calls = ledger.get("tool_calls", [])

        customer_verified = any(
            c["tool_name"] == "lookup_customer" and c["status"] == "success"
            for c in tool_calls
        )
        if not customer_verified:
            return Guide(
                reason="You must look up the customer with lookup_customer "
                "before processing a refund."
            )

        order_checked = any(
            c["tool_name"] == "get_order_history" and c["status"] == "success"
            for c in tool_calls
        )
        if not order_checked:
            return Guide(
                reason="You must check the order history with get_order_history "
                "before processing a refund."
            )

        return Proceed(reason="Refund workflow validated")


from typing import Literal

from pydantic import BaseModel, Field
from strands import Agent


class ToneVerdict(BaseModel):
    """Structured answer from the tone judge."""

    decision: Literal["proceed", "guide"] = Field(description="'proceed' if the reply follows the guidelines, 'guide' if it needs a fix")
    reason: str = Field(description="Short explanation, or what to fix")


class ToneGuardrailHandler(LLMSteeringHandler):
    """LLM-based handler: a second model call grades the TONE of the agent's final reply.

    Fix (AWS SBG at UH edition): LLMSteeringHandler only judges tool calls by default, so the
    original handler sent every lookup/refund call to a tone judge, which often cancelled them
    and made the agent retry tool calls over and over. Now tool calls always proceed and only
    the final text reply is graded, with at most one rewrite per reply.
    """

    name = "tone-guardrail"

    def __init__(self):
        super().__init__(
            system_prompt="""You are evaluating a customer service agent's reply to a customer.
Ensure the reply follows these communication guidelines:

- Don't overpromise or guarantee specific timelines beyond what the system confirms
- Don't blame the customer, other departments, or third parties
- Acknowledge the customer's frustration before jumping to solutions
- Don't offer discounts, credits, or compensation beyond what's in the workflow instructions
- Keep responses concise and actionable, no walls of text
- Never share internal system details, error codes, or technical jargon with the customer
- If the agent can't help, it should clearly explain why and offer an alternative

If the reply violates any of these, decide 'guide' and say specifically what to fix. Otherwise decide 'proceed'."""
        )
        self.just_guided = False

    async def steer_before_tool(self, *, agent, tool_use, **kwargs):
        # Tone is about what the customer reads, so never block a tool call here.
        return Proceed(reason="Tone guardrail only reviews final replies")

    async def steer_after_model(self, *, agent, message, stop_reason, **kwargs):
        reply = ""
        for block in message.get("content", []):
            if "text" in block:
                reply = reply + block["text"]
        if stop_reason != "end_turn" or not reply.strip():
            return Proceed(reason="Not a final reply")
        if self.just_guided:
            # Only one rewrite per reply, so the agent can't get stuck in a loop.
            self.just_guided = False
            return Proceed(reason="Already rewritten once")

        print("[TONE] 🔍 Evaluating agent response...")
        judge = Agent(system_prompt=self.system_prompt, model=self.model or agent.model, callback_handler=None)
        verdict = judge(
            "Grade this customer service reply:\n\n" + reply,
            structured_output_model=ToneVerdict,
        ).structured_output
        if verdict.decision == "guide":
            print("[TONE] ⚠️  Tone guided: " + verdict.reason)
            self.just_guided = True
            return Guide(reason="Rewrite your last reply to the customer. " + verdict.reason)
        print("[TONE] ✅ Tone OK")
        return Proceed(reason=verdict.reason)


tone_handler = ToneGuardrailHandler()
