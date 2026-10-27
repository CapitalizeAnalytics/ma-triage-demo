# ma-triage-demo

A training demo of **Claude Managed Agents** and the agent lifecycle, using a
realistic AppSec task: triaging SQL injection findings from a static analysis
scanner.

The agent reads a scanner report, opens the flagged source code, traces where
the input comes from, and decides whether each finding is really exploitable.
For each finding it files a **ticket draft** through a tool that our own code
checks before saving. A person reviews every draft. Nothing is filed
automatically.

The same task is built two ways, so you can compare them side by side:

| Script | Built on | Who runs the loop and the tools |
|---|---|---|
| `triage_demo.py` | Claude Managed Agents | Anthropic runs the agent loop and the read-only file tools in a cloud sandbox with no network access. Our code only handles the ticket tool. |
| `triage_loop.py` | Plain Messages API | Our code runs everything: the loop, the file tools, the stop condition, the file access rules, error handling and history. |

## What happens in `triage_demo.py`

The steps follow the order of the deck:

1. **Agent**: model, instructions (system prompt) and tools. All built-in
   tools are switched off except `read`, `glob` and `grep`, plus one custom
   tool, `create_ticket_draft`.
2. **Environment**: a cloud sandbox with no network access.
3. **Session**: the agent and environment together, with the sample repo and
   scan report uploaded and mounted read-only.
4. **Events**: we send the task, stream what the agent does, and answer its
   `create_ticket_draft` calls. Our code rejects any draft with an unknown
   finding ID, an invalid verdict or severity, or no `file:line` evidence.
5. **Result**: accepted ticket drafts, plus the session's token usage.

## Setup

You need Python 3.10 or newer and an Anthropic API key with access to Managed
Agents.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...  # Windows: set ANTHROPIC_API_KEY=sk-ant-...
```

Never commit your API key. `.env` is already in `.gitignore`.

## Running it

```bash
python triage_demo.py     # Managed Agents version
python triage_loop.py     # hand-written loop version
```

Each run creates a new timestamped folder under `runs/`:

- `runs/run-.../`: Managed Agents runs. `ids.json` (agent, environment,
  session and uploaded file IDs), `events.jsonl` (every streamed event),
  `session.json` (final session with usage) and `tickets/`.
- `runs/loop-.../`: hand-written loop runs. `summary.json` (turns, tool calls,
  tokens, estimated cost, per-turn breakdown), `messages.json` (full
  conversation history) and `tickets/`.

The `runs/` folder already has a few example runs, so you can see the output
without running anything.

**Reusing an agent:** `triage_demo.py` creates a new agent, environment and
uploaded files every time. To reuse them from an earlier run *in your own
account*, pass that run's `ids.json`:

```bash
python triage_demo.py runs/run-YYYYMMDD-HHMMSS/ids.json
```

The IDs in the committed example runs belong to the original author's
account, so they won't work with a different API key.

## The sample

> **The security bugs in `sample/` are intentional.** It's a fictional app
> with no real data, built only as triage material. Don't deploy it or "fix"
> it.

- `sample/demo-store-api/`: a tiny Flask order-lookup service.
- `sample/scan/findings.json`: a fictional scanner report with three
  SQL injection findings.

The three findings are designed to have different answers:

| Finding | Location | Expected verdict |
|---|---|---|
| F-001 | `app/main.py`, `/orders/search` | **Exploitable.** The `customer` query parameter from a public page goes straight into the SQL string. |
| F-002 | `app/main.py`, `/reports/status` | **Not exploitable.** The input only picks a value from a fixed allow-list, so the query only ever contains hard-coded strings. |
| F-003 | `tests/test_search.py` | **Not exploitable.** Test code that builds its query from hard-coded seed data, not user input. |

To run the sample app's own test:

```bash
cd sample/demo-store-api
python -m pytest
```

## Files

```
triage_demo.py        Managed Agents version
triage_loop.py        hand-written agent loop version
requirements.txt      Python packages
sample/               the fictional repo and scan report the agent triages
runs/                 output of each run (example runs included)
```
