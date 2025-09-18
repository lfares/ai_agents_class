# Learnings — HW1

## What worked

- Created a runnable `main.py` runner that assembles agents, tasks, and a Crew to execute the homework workflow.
- Added `.env.example` and `.gitignore` to protect secrets and document required environment variables.
- Provided a concise README with minimal, repeatable setup steps (create `.env`, create Python venv, install requirements, run).

## What didn't work

- Attempting to run and install dependencies in the original execution environment failed due to an older system Python (3.9) and missing Homebrew/python installers in that environment.
- The `FileWriterTool` from the example did not seem to exist anymore in the `crewai_tools`, so I had to go for a new direction on my agent/task.

- Tried to use Google Gemini through `crewai`'s LLM path but it didn't work. I experimented with a custom Gemini HTTP adapter and also attempted to instantiate an `LLM` from `crewai`, but the installed `crewai` package didn't expose the expected `LLM` class and the Gemini model/resource naming required by the REST endpoint proved fiddly. In short: Gemini integration was not achievable in the workshop timeframe, so I reverted to using OpenAI for now.

- My free OpenAI key hit limits while exercising the crew/agent flows: runs reached 401 (unauthorized) initially during setup and later 429 / insufficient_quota when testing repeatedly. The free/trial quota isn't sufficient for heavy interactive testing. Short-term fixes are adding retry/backoff logic or using a paid key with enough quota.

- Example code field names and shapes from `crewai` samples didn't match the runtime expectations. I had to rename fields (for example `background` → `backstory`, `expected_outcome` → `expected_output`) and avoid passing `llm=None` into Agent constructors (that led to a NoneType `.bind` AttributeError). These mismatches required checking stack traces and aligning my code with the runtime API.

## What I learned

- `crewai` requires Python 3.10+ (Python 3.12 was used for local runs). Using the system Python (3.9) causes a compatible issue.
- When pip reports "resolution-too-deep" or similar dependency resolver issues, upgrading pip (python -m pip install --upgrade pip) and re-running installs resolved it.

## AI use

- Creation of json file from original CV, explaining the format and mentioning that it would be used for an interviewer agent
- Creation of README (with various adaptations)
- Creation of main function (with many manual and automated fixes)
