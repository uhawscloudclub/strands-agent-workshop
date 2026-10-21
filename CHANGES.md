# Changes from the upstream workshop

Tested on Strands Agents v1.58.0 (Oct 2026). Every notebook cell and companion script was run with a stand-in model; the deploy step itself still needs a real AWS account.

| File | Change | Why |
|------|--------|-----|
| `samples/03-skills-steering/module-03-skills-steering.ipynb`, `samples/0{3,4,5}-*/steering_handlers.py` | `data.get("ledger", {})` became `data.get("ledger") or {}` | `JSONSerializableDict.get()` takes one argument. The TypeError was swallowed by the steering framework, so `process_refund` was never blocked (fail-open). |
| All notebooks and `chat.py` scripts | Added `# Workshop Studio: cd /workshop/samples/...` next to `cd samples/...` | In Workshop Studio the repo lives at `/workshop`. |
| `samples/03-skills-steering/module-03-skills-steering.ipynb`, `samples/0{3,4,5}-*/steering_handlers.py` | `ToneGuardrailHandler` now always lets tool calls proceed and grades only the final text reply (structured `ToneVerdict`), with at most one rewrite per reply | `LLMSteeringHandler` only judges tool calls, so the tone judge was cancelling `lookup_customer`/`process_refund` calls and the agent retried tool calls repeatedly (reported by Cougar AI, Oct 15). Its "Tone OK" message never reflected a real check. |
| `samples/01-agent-loop-tools/` (notebook + `chat.py`), `agent-arena/*/agent.py`, `requirements.txt` | One `MODEL` setting (`MODEL_ID` env var, default `amazon.nova-pro-v1:0` in us-east-1) passed to every `Agent(...)`; root requirements for a local VS Code setup | Oct 21 runs on students' own laptops with new AWS accounts, where Claude (sold through AWS Marketplace) may not be available on the Free plan. |
| `requirements.txt` (root and every `samples/*/`) | Added `botocore[crt]` and `awscrt>=0.30.0` | Credentials from `aws login` fail in Python with MissingDependencyException without them (found in the Oct 21 Windows dry run). |
| `samples/02-hooks/module-02-hooks.ipynb` | Added a solution cell (`TotalLimitHook`) after the Try It | Beginners had no answer to check against. |
| `samples/05-deploy/main.py` | Added `AgentSkills(skills=["./skills"])` to the plugins | The deploy steps copy `skills/` but the agent never loaded it. |
| `samples/07-evals/module-07-evals.ipynb` | Rubric scores 0.0 if `process_refund` runs before the lookups; closing line no longer credits steering handlers | The old rubric let a refund-first agent pass; the steered agent there is prompt-only. |
| `agent-arena/README.md` | Tool examples now do things the model can't do from text alone (math, dates, saving notes); timing updated for the Oct 21 plan | Cougar AI found the personal agent answered project questions without the suggested `get_project_details` tool. |
| `agent-arena/` | New: build it, then break it activity (company and personal tracks, guardrail hooks) | Second half of the AWS SBG x Cougar AI workshop. |

Note for the upstream Setup page (not in this repo): the local setup says `cd aws-demo-strands-agents-hands-on-workshop`, but the folder is `sample-strands-agents-hands-on-workshop`.
