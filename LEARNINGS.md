# Learnings — HW1

## What worked

- Created a runnable `main.py` runner that assembles agents, tasks, and a Crew to execute the homework workflow.
- Added `.env.example` and `.gitignore` to protect secrets and document required environment variables.
- Provided a concise README with minimal, repeatable setup steps (create `.env`, create Python venv, install requirements, run).

## What didn't work

- Attempting to run and install dependencies in the original execution environment failed due to an older system Python (3.9) and missing Homebrew/python installers in that environment.
- The `FileWriterTool` from the example did not seem to exist anymore in the `crewai_tools`, so I had to go for a new direction on my agent/task

## What I learned

- `crewai` requires Python 3.10+ (Python 3.12 was used for local runs). Using the system Python (3.9) causes a compatible issue.
- When pip reports "resolution-too-deep" or similar dependency resolver issues, upgrading pip (python -m pip install --upgrade pip) and re-running installs resolved it.

## AI use

- Creation of json file from original CV, explaining the format and mentioning that it would be used for an interviewer agent
- Creation of README (with various adaptations)
- Creation of .env and .env.example files
- Creation of main function (with many manual and automated fixes)
