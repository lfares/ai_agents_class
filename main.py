from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import FileReadTool
import os
import json
import sys
from pathlib import Path

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

def create_reading_summary_agent(llm=None):
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
    """Create interview preparation task"""
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

def convert_pdf_to_text(pdf_path):
    """Convert PDF to text using pypdf"""
    try:
        import pypdf
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() + "\n"
        return pdf_text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def create_excel_from_summary(summary_text, excel_path, pdf_name):
    """Create Excel file from agent summary"""
    try:
        import pandas as pd
        
        lines = summary_text.split('\n')
        key_concepts = []
        relevance = []
        
        # Parse summary text for key concepts and relevance
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '*')):
                if len(line) > 10:  # Skip very short lines
                    if 'concept' in line.lower() or 'definition' in line.lower():
                        key_concepts.append(line)
                    elif 'relevant' in line.lower() or 'interest' in line.lower():
                        relevance.append(line)
        
        # Fallback if no specific sections found
        if not key_concepts:
            key_concepts = [summary_text[:500] + "..." if len(summary_text) > 500 else summary_text]
        if not relevance:
            relevance = ["Relevant to Livia's interests in AI and education"]
        
        # Create DataFrame and save to Excel
        data = {
            'Name': [pdf_name],
            'Key concepts & Definitions': [' '.join(key_concepts[:3])],
            'Relevance & Curiosity': [' '.join(relevance[:2])]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)
        return True
        
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False

def create_reading_summary_task(agent, pdf_path, excel_path, interests):
    """Create reading summarization task"""
    # Convert PDF to text first
    pdf_text = convert_pdf_to_text(pdf_path)
    
    # Create a temporary text file with the PDF content
    temp_txt_path = pdf_path.replace('.pdf', '_temp.txt')
    try:
        with open(temp_txt_path, 'w', encoding='utf-8') as f:
            f.write(pdf_text)
    except Exception as e:
        print(f"Warning: Could not create temp text file: {e}")
        temp_txt_path = None
    
    # Create task description based on available options
    if temp_txt_path:
        task_description = f"""Read the text file located at {temp_txt_path}. It contains the content of a PDF article or book chapter about a subject within education. Then, generate an excel file at {excel_path} with a summary of the key concepts and what Livia would find relevant. Write like Livia would - natural and informal. Livia is interested in the following topics: {interests}. Use this information to determine what she would find relevant in the context of the reading.

IMPORTANT: Use the FileReadTool to read the text file at: {temp_txt_path}"""
    else:
        # Fallback: provide the text directly in the task description
        task_description = f"""Analyze the following text content from a PDF article or book chapter about a subject within education. Generate an excel file at {excel_path} with a summary of the key concepts and what Livia would find relevant. Write like Livia would - natural and informal. Livia is interested in the following topics: {interests}. Use this information to determine what she would find relevant in the context of the reading.

PDF Content:
{pdf_text[:5000]}{'...' if len(pdf_text) > 5000 else ''}"""
    
    return Task(
        description=task_description,
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
    """Main function to run the AI Agent Assistant"""
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
        cv_path = os.path.join(os.path.dirname(__file__), "cv.json")
        is_valid, message = validate_file_path(cv_path, "CV file")
        if not is_valid:
            print(f"❌ {message}")
            return
        
        try:
            with open(cv_path, "r", encoding="utf-8") as f:
                cv_data = json.load(f)
                cv_text = json.dumps(cv_data, indent=2, ensure_ascii=False)
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
                summarize_pdf = False
            else:
                excel_path = get_user_input(
                    "Enter Excel output path",
                    default="reading_summary.xlsx"
                )

        # Create agents and tasks
        try:
            if llm is None:
                interviewer = create_interviewer_agent()
                reader = create_reading_summary_agent()
            else:
                interviewer = create_interviewer_agent(llm=llm)
                reader = create_reading_summary_agent(llm=llm)
        except Exception as e:
            print(f"❌ Error creating agents: {e}")
            return

        # Prepare tasks
        tasks = [create_interview_task(interviewer, cv_text, job_description)]
        
        if summarize_pdf:
            tasks.append(create_reading_summary_task(reader, pdf_path, excel_path, interests=INTERESTS))

        # Create and run crew
        print("\n🤖 Creating AI agents...")
        print("✅ Agents created successfully")
        
        print("\n📋 Preparing tasks...")
        if summarize_pdf:
            print("✅ Interview preparation + PDF summarization tasks ready")
        else:
            print("✅ Interview preparation task ready")
        
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

            print("\n" + "="*60)
            print("🎉 CREW EXECUTION COMPLETED!")
            print("="*60)
            
            if summarize_pdf and excel_path:
                # Create Excel file from the agent's summary
                print("\n📊 Creating Excel file from summary...")
                pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
                success = create_excel_from_summary(str(result), excel_path, pdf_name)
                
                if success and os.path.exists(excel_path):
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