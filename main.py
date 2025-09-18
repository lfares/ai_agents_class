from dotenv import load_dotenv

# Reads the .env file and loads the variables into the environment
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain.chat_models import ChatOpenAI
from crewai_tools import FileReadTool
import os
import json
import sys

# Agent factories
def create_interviewer_agent(llm=None):
    cfg = dict(
        role="Interview Helper",
        goal="Help a candidate prepare to a job interview based on their CV and the job description.",
        backstory="You are helping Livia prepare for a job interview. You have access to her CV information and the job description. Use this information to generate relevant interview questions and answers. Talk like Livia would - natural, direct to the point but polite.",
        verbose=True,
        allow_delegation=False,
    )
    if llm is not None:
        cfg["llm"] = llm
    return Agent(**cfg)


def create_reading_summary(llm=None):
    cfg = dict(
        role="Reading Summarizer",
        goal="Read a pdf file (e.g. an article or book chapter) and generate an excel file with what Livia would find relevant and a summary of the key concepts.",
        backstory="You are helping Livia summarize readings from her Graduate Education classes. You have access to the reading material in pdf format. Use this information to generate an excel file with what Livia would find relevant, given her interests, and a summary of the key concepts. Write like Livia would - natural and informal.",
        verbose=True,
        allow_delegation=False,
        tools=[FileReadTool()],
    )
    if llm is not None:
        cfg["llm"] = llm
    return Agent(**cfg)

def create_interview_task(agent, cv, job_description):
    # Define the task for the interview helper agent
    return Task(
        description=f"""Help Livia prepare for a job interview based on her CV and the job description. You should generate a list of potential interview questions and answers that Livia can use to practice. Focus on the most relevant skills and experiences from her CV that match the job description. Give concise and clear answers that Livia can easily remember, and tips to help her prepare and feel calm at the day. Remember that the answers should be in Livia's voice, so they should sound natural and polite.
        Use the following information:
        CV: {cv}
        Job Description: {job_description}""",
        expected_output=f"""A full preparation for the interview. Include the following:
        1) A list of potential questions
        2) Answers in Livia's voice following the STAR method
        3) Tips for Livia to feel confident and prepared.""",
        agent=agent,
    )


def create_reading_summary_task(agent, pdf_path, excel_path, interests):
    # Define the task for the interview helper agent
    return Task(
        description=f"""Read the pdf file located at {pdf_path}. It contains an article or book chapter about a subject within education. Then, generate an excel file at {excel_path} with a summary of the key concepts and what Livia would find relevant. Write like Livia would - natural and informal. Livia is interested in the following topics: {interests}. Use this information to determine what she would find relevant in the context of the reading.""",
        expected_output=f"""An excel file located at {excel_path} with the following columns:
        1) Name - name of the reading
        2) Key concepts & Definitions - summary of the key concepts and its corresponding definitions, as Livia would write them - informal and natural
        3) Relevance & Curiosity - why this is relevant to Livia's interests
        The row should be filled with the relevant information from the reading.""",
        agent=agent,
    )

# Topics of interest used when summarizing readings
INTERESTS = [
    "leveraging AI in education",
    "marginalized communities",
    "edtechs",
    "learning design",
    "career readiness",
    "K-12",
    "soft skill development",
]


def main():
    """Concise runner for hw1.

    Behavior:
    - Loads `hw1/cv.json` and pretty-prints it for agent context.
    - Prompts once for a job description string (falls back to a short default).
    - Optionally asks for a PDF to summarize and an output excel path.
    - Creates agents/tasks, assembles a Crew and kicks it off.
    """

    # Minimal LLM wiring: always construct a small OpenAI chat model (default: gpt-3.5-turbo).
    # Keep this simple — no Gemini checks or complex fallbacks.
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    openai_key = os.environ.get("OPENAI_API_KEY")
    llm = ChatOpenAI(model_name=openai_model, openai_api_key=openai_key)

    # Retrieve inputs from user
    cv_path = os.path.join(os.path.dirname(__file__), "cv.json")
    with open(cv_path, "r", encoding="utf-8") as f:
        cv_text = json.dumps(json.load(f), indent=2, ensure_ascii=False)

    job_description = input(
        "Paste the job description text for the role (brief or full). Press Enter to use a short default: "
    ) or "Default job description: Researcher position focused on AI in education."

    pdf = input("Optional: path to a reading PDF to summarize (press Enter to use example_reading.pdf or provide your own): ").strip()
    if not pdf:
        pdf = os.path.join(os.path.dirname(__file__), "example_reading.pdf")
    excel = None
    if pdf:
        excel = input("Optional: excel output path (default: reading_summary.xlsx): ").strip() or "reading_summary.xlsx"

    # Create agents and tasks
    print("\nCreating agents...")
    if llm is None:
        interviewer = create_interviewer_agent()
        reader = create_reading_summary()
    else:
        interviewer = create_interviewer_agent(llm=llm)
        reader = create_reading_summary(llm=llm)

    print("Preparing tasks...")
    tasks = [create_interview_task(interviewer, cv_text, job_description)]
    if pdf:
        tasks.append(create_reading_summary_task(reader, pdf, excel, interests=INTERESTS))

    print("Launching crew...")
    crew = Crew(
        agents=[interviewer, reader],
        tasks=tasks,
        processor=Process.sequential,
        verbose=True,
    )

    print("Running crew...")
    result = crew.kickoff()

    print("\nCrew finished. Result:\n")
    print(result)


if __name__ == "__main__":
    main()
