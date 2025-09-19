from dotenv import load_dotenv

# Reads the .env file and loads the variables into the environment
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import FileReadTool
import os
import json
import sys
import pandas as pd
from pathlib import Path
from langchain_core.tools import tool
from typing import List, Dict, Any, Optional

# Excel writing function
def write_excel_file(data: List[Dict[str, Any]], file_path: str, columns: Optional[List[str]] = None) -> str:
    """Write data to Excel file"""
    try:
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(file_path, index=False)
        return f"Successfully wrote data to {file_path}"
    except Exception as e:
        return f"Error writing to Excel: {str(e)}"

# Create a simple tool wrapper
@tool
def excel_writer_tool(data: str, file_path: str) -> str:
    """Write data to an Excel file. Data should be a JSON string of list of dictionaries."""
    try:
        import json
        data_list = json.loads(data)
        return write_excel_file(data_list, file_path)
    except Exception as e:
        return f"Error: {str(e)}"

# File validation functions
def validate_file_path(file_path, file_type="file"):
    """Validate if file exists and is accessible"""
    path = Path(file_path)
    if not path.exists():
        return False, f"{file_type.capitalize()} not found: {file_path}"
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    return True, "File is valid"

def get_user_input(prompt, default=None, required=False):
    """Get user input with better error handling"""
    while True:
        try:
            if default:
                user_input = input(f"{prompt} (default: {default}): ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if required and not user_input:
                print("This field is required. Please provide a value.")
                continue
            
            return user_input
        except (EOFError, KeyboardInterrupt):
            print("\n\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print(f"Error reading input: {e}")
            continue

def save_summary_to_excel(summary_text, excel_path):
    """Convert structured summary text to Excel file"""
    try:
        # Create a simple Excel file with the summary
        data = {
            'Section': ['Summary'],
            'Content': [summary_text]
        }
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)
        return True
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False

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
        goal="Read a pdf file (e.g. an article or book chapter) and generate a structured summary with what Livia would find relevant and key concepts.",
        backstory="You are helping Livia summarize readings from her Graduate Education classes. You have access to the reading material in pdf format. Use this information to generate a structured summary with what Livia would find relevant, given her interests, and a summary of the key concepts. Write like Livia would - natural and informal.",
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
    # Define the task for the reading summarizer agent
    return Task(
        description=f"""Read the pdf file located at {pdf_path}. It contains an article or book chapter about a subject within education. Generate a structured summary with what Livia would find relevant and key concepts. Write like Livia would - natural and informal. Livia is interested in the following topics: {interests}. Use this information to determine what she would find relevant in the context of the reading.

Format your response as a structured summary that can be easily converted to an Excel file.""",
        expected_output=f"""A structured summary with the following sections:
        1) Reading Title - name of the reading
        2) Key Concepts & Definitions - summary of the key concepts and their definitions, written in Livia's informal and natural style
        3) Relevance & Curiosity - why this is relevant to Livia's interests and what questions it raises
        4) Action Items - what Livia should do next based on this reading
        5) Connections - how this connects to other topics Livia is interested in
        
        Format this as clear, well-structured text that can be easily converted to an Excel file.""",
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
    """Enhanced runner for AI agents with better user interaction and error handling."""
    
    print("🤖 Welcome to Livia's AI Agent Assistant!")
    print("=" * 50)
    
    try:
        # LLM configuration: support both OpenAI and Gemini
        llm_type = os.environ.get("LLM_TYPE", "openai").lower()
        print(f"🔧 Using LLM: {llm_type.upper()}")
        
        if llm_type == "gemini":
            # Configure Gemini LLM using LiteLLM format
            gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            gemini_key = os.environ.get("GEMINI_API_KEY")
            if not gemini_key:
                print("⚠️  Warning: GEMINI_API_KEY not found. Falling back to OpenAI.")
                llm_type = "openai"
            else:
                # Set the API key for Google
                os.environ["GOOGLE_API_KEY"] = gemini_key
                # Use LiteLLM format for Gemini
                llm = f"gemini/{gemini_model}"
                print(f"✅ Gemini configured with model: {gemini_model}")
        
        if llm_type == "openai":
            # Configure OpenAI LLM (default)
            openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                print("⚠️  Warning: OPENAI_API_KEY not found. Using default model without API key.")
                llm = None
            else:
                llm = ChatOpenAI(model_name=openai_model, openai_api_key=openai_key)
                print(f"✅ OpenAI configured with model: {openai_model}")

        # Load CV data
        print("\n📄 Loading CV data...")
        cv_path = os.path.join(os.path.dirname(__file__), "cv.json")
        is_valid, message = validate_file_path(cv_path, "CV file")
        if not is_valid:
            print(f"❌ {message}")
            return
        
        try:
            with open(cv_path, "r", encoding="utf-8") as f:
                cv_data = json.load(f)
                cv_text = json.dumps(cv_data, indent=2, ensure_ascii=False)
            print("✅ CV data loaded successfully")
        except Exception as e:
            print(f"❌ Error loading CV: {e}")
            return

        # Get job description from user
        print("\n💼 Job Interview Preparation")
        print("-" * 30)
        job_description = get_user_input(
            "Enter the job description (or press Enter for default example)",
            default="Researcher position focused on AI in education with emphasis on marginalized communities and learning design"
        )
        print(f"✅ Job description: {job_description[:50]}...")

        # Ask about PDF summarization
        print("\n📚 Reading Summarization")
        print("-" * 25)
        summarize_pdf = get_user_input(
            "Would you like to summarize a PDF reading? (y/n)",
            default="y"
        ).lower().startswith('y')
        
        pdf_path = None
        excel_path = None
        
        if summarize_pdf:
            pdf_path = get_user_input(
                "Enter PDF file path",
                default=os.path.join(os.path.dirname(__file__), "example_reading.pdf")
            )
            
            # Validate PDF file
            is_valid, message = validate_file_path(pdf_path, "PDF file")
            if not is_valid:
                print(f"❌ {message}")
                print("Skipping PDF summarization...")
                summarize_pdf = False
            else:
                print("✅ PDF file validated")
                excel_path = get_user_input(
                    "Enter Excel output path",
                    default="reading_summary.xlsx"
                )
                print(f"✅ Will create Excel file: {excel_path}")

        # Create agents and tasks
        print("\n🤖 Creating AI agents...")
        try:
            if llm is None:
                interviewer = create_interviewer_agent()
                reader = create_reading_summary()
            else:
                interviewer = create_interviewer_agent(llm=llm)
                reader = create_reading_summary(llm=llm)
            print("✅ Agents created successfully")
        except Exception as e:
            print(f"❌ Error creating agents: {e}")
            return

        # Prepare tasks
        print("\n📋 Preparing tasks...")
        tasks = [create_interview_task(interviewer, cv_text, job_description)]
        
        if summarize_pdf:
            tasks.append(create_reading_summary_task(reader, pdf_path, excel_path, interests=INTERESTS))
            print("✅ Interview preparation + PDF summarization tasks ready")
        else:
            print("✅ Interview preparation task ready")

        # Create and run crew
        print("\n🚀 Launching AI crew...")
        try:
            crew = Crew(
                agents=[interviewer, reader] if summarize_pdf else [interviewer],
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
            )

            print("🏃‍♀️ Running crew...")
            result = crew.kickoff()

            print("\n" + "="*50)
            print("🎉 CREW EXECUTION COMPLETED!")
            print("="*50)
            print(f"\n📊 Results:\n{result}")
            
            # Convert summary to Excel if PDF summarization was requested
            if summarize_pdf and excel_path:
                print(f"\n📝 Converting summary to Excel: {excel_path}")
                if save_summary_to_excel(str(result), excel_path):
                    print(f"✅ Excel file created successfully: {excel_path}")
                else:
                    print(f"❌ Failed to create Excel file: {excel_path}")
            
        except Exception as e:
            print(f"❌ Error running crew: {e}")
            return

    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again.")


if __name__ == "__main__":
    main()
