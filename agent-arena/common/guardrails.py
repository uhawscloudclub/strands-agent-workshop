"""Deterministic defenses you can bolt onto ANY Strands agent.

These use the same hook system you learned in Module 2. The big idea of the
arena: a system prompt that says "don't reveal secrets" is a suggestion.
Code that runs in the agent loop is a rule.
"""

import re
from strands.hooks import HookProvider, HookRegistry, AfterToolCallEvent, BeforeToolCallEvent

SECRET_PATTERNS = [
    r"FLAG\{[^}]*\}",            # CTF flags
    r"\b[A-Z]{4,}\d{2}\b",       # discount-style codes like STAFF50
    r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",  # phone numbers
]


class SecretScrubber(HookProvider):
    """Defense 1: redact secrets from tool results BEFORE the model ever sees them.

    If the model never reads the secret, no prompt injection can make it leak it.
    """

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterToolCallEvent, self.scrub)

    def scrub(self, event: AfterToolCallEvent) -> None:
        changed = False
        for block in event.result.get("content", []):
            if "text" in block:
                cleaned = block["text"]
                for pattern in SECRET_PATTERNS:
                    cleaned = re.sub(pattern, "[REDACTED]", cleaned)
                if cleaned != block["text"]:
                    block["text"] = cleaned
                    changed = True
        if changed:
            print("[GUARD] 🧽 Secret scrubbed from tool result")


class RefundLimit(HookProvider):
    """Defense 2: no refund over max_amount, and never without checking the order first."""

    def __init__(self, max_amount: float = 25.0):
        self.max_amount = max_amount
        self.checked_orders = set()

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.check)

    def check(self, event: BeforeToolCallEvent) -> None:
        name = event.tool_use["name"]
        args = event.tool_use.get("input", {})
        if name == "check_order":
            self.checked_orders.add(str(args.get("order_id", "")).upper())
        if name == "issue_refund":
            order_id = str(args.get("order_id", "")).upper()
            amount = float(args.get("amount", 0))
            if order_id not in self.checked_orders:
                event.cancel_tool = "Refund blocked: look up the order with check_order first."
                print("[GUARD] 🚫 Refund blocked: order not checked")
            elif amount > self.max_amount:
                event.cancel_tool = f"Refund blocked: amounts over ${self.max_amount:.2f} need a human manager."
                print(f"[GUARD] 🚫 Refund blocked: ${amount:.2f} is over the limit")
