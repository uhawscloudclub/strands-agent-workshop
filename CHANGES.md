# Changes from the upstream workshop

Tested on Strands Agents v1.58.0 (Oct 2026). Every notebook cell and companion script was run with a stand-in model; the deploy step itself still needs a real AWS account.

| File | Change | Why |
|------|--------|-----|
| `samples/03-skills-steering/module-03-skills-steering.ipynb`, `samples/0{3,4,5}-*/steering_handlers.py` | `data.get("ledger", {})` became `data.get("ledger") or {}` | `JSONSerializableDict.get()` takes one argument. The TypeError was swallowed by the steering framework, so `process_refund` was never blocked (fail-open). |
| All notebooks and `chat.py` scripts | Added `# Workshop Studio: cd /workshop/samples/...` next to `cd samples/...` | In Workshop Studio the repo lives at `/workshop`. |
| `samples/02-hooks/module-02-hooks.ipynb` | Added a solution cell (`TotalLimitHook`) after the Try It | Beginners had no answer to check against. |
| `samples/05-deploy/main.py` | Added `AgentSkills(skills=["./skills"])` to the plugins | The deploy steps copy `skills/` but the agent never loaded it. |
| `samples/07-evals/module-07-evals.ipynb` | Rubric scores 0.0 if `process_refund` runs before the lookups; closing line no longer credits steering handlers | The old rubric let a refund-first agent pass; the steered agent there is prompt-only. |
| `agent-arena/` | New: build it, then break it activity (company and personal tracks, guardrail hooks) | Second half of the AWS SBG x Cougar AI workshop. |

Note for the upstream Setup page (not in this repo): the local setup says `cd aws-demo-strands-agents-hands-on-workshop`, but the folder is `sample-strands-agents-hands-on-workshop`.
