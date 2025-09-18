# Learnings — HW1

## What worked

- Fully ran the `crewai` library end-to-end: created agents, tasks, and a Crew that executes the workflow.
- Created a local Python virtual environment and installed all required dependencies.

## What didn't work

- Attempting to run and install dependencies in the original execution environment failed due to an older system Python (3.9) and missing Homebrew/python installers in that environment.
- The `FileWriterTool` from the example did not seem to exist anymore in the `crewai_tools`, so I had to go for a new direction on my agent/task

## What I learned

- `crewai` requires Python 3.10+ (Python 3.12 was used for local runs). Using the system Python (3.9) causes a compatible issue.
- When pip reports "resolution-too-deep" or similar dependency resolver issues, upgrading pip (python -m pip install --upgrade pip) and re-running installs resolved it.
 - How to create agents and tools with `crewai`: supply `role`, `goal`, `backstory`, and use `tools=[...]` for file/IO helpers.
 - How to manage API keys: keep secrets in `.env`, load them with `python-dotenv` (`load_dotenv()`), and read them via `os.environ.get()`.

## AI use

- Creation of json file from original CV, explaining the format and mentioning that it would be used for an interviewer agent
- Creation of README (with various adaptations)
- Creation of main function (with many manual and automated fixes)
