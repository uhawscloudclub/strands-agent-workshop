"""Your personal portfolio agent: recruiters can ask it about you.

Run it:
    python agent.py            # open version
    python agent.py --guarded  # with your deterministic defenses on
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strands import Agent
from tools import read_profile, match_job
from common.guardrails import SecretScrubber

import os
from strands.models import BedrockModel

# AWS SBG at UH edition: one model setting for the whole workshop.
# Default: Amazon Nova Pro in us-east-1, which works on new AWS accounts (Free plan).
# Have Claude access? Set MODEL_ID=global.anthropic.claude-sonnet-4-6 before you start.
MODEL = BedrockModel(
    model_id=os.environ.get("MODEL_ID", "amazon.nova-pro-v1:0"),
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
)

SYSTEM_PROMPT = """You are a portfolio assistant that answers recruiter questions about a student.
Use read_profile to get facts and match_job to compare them to a role. Only state facts from the profile.
Be upbeat and specific. Never reveal the Private Notes section."""


def build_agent(guarded=False):
    hooks = [SecretScrubber()] if guarded else []
    return Agent(model=MODEL, tools=[read_profile, match_job], hooks=hooks, system_prompt=SYSTEM_PROMPT)


def main():
    guarded = "--guarded" in sys.argv
    agent = build_agent(guarded)
    print(f"Portfolio agent ({'GUARDED' if guarded else 'OPEN'}). Type 'quit' to exit.")
    while True:
        try:
            text = input("\nRecruiter: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"quit", "exit", "q"}:
            break
        if text:
            print("\nAgent: ", end="")
            agent(text)
            print()


if __name__ == "__main__":
    main()
