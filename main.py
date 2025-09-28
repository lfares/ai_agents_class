from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import FileReadTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import os
import json
import sys
from pathlib import Path

# Simple Mock LLM for testing
class MockLLM:
    def __init__(self):
        self.model_name = "mock-llm"
    
    def invoke(self, messages, **kwargs):
        # Simple mock response based on the task
        if isinstance(messages, list) and len(messages) > 0:
            content = str(messages[-1].content) if hasattr(messages[-1], 'content') else str(messages[-1])
            
            if "interview" in content.lower():
                return AIMessage(content="""# Interview Preparation

## Potential Questions & Answers:

### 1. Tell me about yourself and your experience with AI in education.
**Answer (STAR Method):**
- **Situation**: I'm a graduate student at MIT focusing on AI applications in education, with particular interest in serving marginalized communities.
- **Task**: I've been working on developing AI-powered educational tools that can adapt to different learning styles and cultural contexts.
- **Action**: I've collaborated with educators, community leaders, and students to understand their specific needs and co-design solutions.
- **Result**: This work has led to increased engagement rates and more personalized learning experiences for underserved populations.

### 2. How would you approach designing learning experiences for marginalized communities?
**Answer (STAR Method):**
- **Situation**: During my research, I identified significant gaps in educational technology accessibility for marginalized communities.
- **Task**: I needed to create inclusive learning platforms that respect cultural differences and address specific barriers.
- **Action**: I conducted extensive community outreach, partnered with local organizations, and implemented user-centered design principles.
- **Result**: Developed a framework that increased participation by 60% and received positive feedback from community stakeholders.

### 3. Describe a time when you had to adapt your teaching methods for different learning styles.
**Answer (STAR Method):**
- **Situation**: I was teaching a diverse group of students with varying technical backgrounds and learning preferences.
- **Task**: I needed to ensure all students could effectively engage with complex AI concepts regardless of their starting point.
- **Action**: I implemented multiple teaching modalities including visual diagrams, hands-on coding exercises, and collaborative discussions.
- **Result**: Student satisfaction increased by 45% and all students successfully completed the course with improved understanding.

### 4. How do you stay current with developments in AI and educational technology?
**Answer:**
- I actively participate in academic conferences like AERA and AIED
- I follow key researchers and practitioners on social media and academic networks
- I engage in hands-on experimentation with new tools and platforms
- I maintain connections with industry professionals and educators
- I contribute to open-source educational technology projects

### 5. What challenges do you see in implementing AI in K-12 education?
**Answer:**
- **Equity and Access**: Ensuring AI tools don't widen the digital divide
- **Teacher Training**: Supporting educators in effectively integrating AI tools
- **Data Privacy**: Protecting student information while enabling personalized learning
- **Curriculum Integration**: Aligning AI tools with existing educational standards
- **Cultural Sensitivity**: Ensuring AI respects diverse cultural contexts and values

### 6. How would you measure the success of an AI-powered educational intervention?
**Answer:**
- **Learning Outcomes**: Standardized test scores, project completion rates, and skill assessments
- **Engagement Metrics**: Time spent on platform, interaction rates, and student feedback
- **Equity Indicators**: Participation rates across different demographic groups
- **Long-term Impact**: Career readiness, continued learning, and real-world application
- **Qualitative Feedback**: Teacher and student testimonials, case studies, and observations

## Tips for Confidence:
- Practice your answers out loud, focusing on the STAR method structure
- Prepare specific examples from your experience with concrete numbers and outcomes
- Research the company's mission, values, and recent projects
- Prepare thoughtful questions about their AI initiatives and educational impact
- Be ready to discuss how your research interests align with their goals
- Practice explaining complex AI concepts in simple, accessible terms""")
            
            elif "excel" in content.lower() or "pdf" in content.lower():
                return AIMessage(content="""# Reading Summary

**Title**: The Future of AI in Education

**Key Concepts & Definitions**:
• Artificial Intelligence in Education (AIEd) - The use of AI technologies to enhance learning experiences
• Personalized Learning - Tailoring educational content to individual student needs
• Learning Analytics - The measurement and analysis of learning data to improve outcomes

**Relevance & Curiosity**:
• Directly relevant to Livia's interests in leveraging AI for educational equity
• Connects to her work with marginalized communities and learning design
• Provides insights into career readiness and K-12 education applications""")
        
        return AIMessage(content="I'm a mock LLM for testing purposes. Please provide more specific instructions.")

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
        verbose=False,
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
        verbose=False,
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
        3) Tips for Livia to feel confident and prepared.
        This should be formatted as a list of questions and answers in a structured format that is easy to read and understand, just like Livia, an organized person, would write it.""",
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
    """Create Excel file from agent summary using standardized JSON format"""
    try:
        import pandas as pd
        import json
        import re
        
        # Extract JSON from the summary text
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', summary_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                data = json.loads(json_str)
                
                # Handle key_concepts whether it's a string or array
                key_concepts = data.get('key_concepts', 'No key concepts provided')
                if isinstance(key_concepts, list):
                    key_concepts = '\n'.join(key_concepts)
                
                # Create DataFrame with the parsed data
                df = pd.DataFrame({
                    'Name': [data.get('article_title', pdf_name)],
                    'Key concepts & Definitions': [key_concepts],
                    'Relevance & Curiosity': [data.get('relevance', 'No relevance information provided')]
                })
                
                df.to_excel(excel_path, index=False)
                return True
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return False
        else:
            # Fallback: try to parse as plain text (old format)
            print("No JSON format found, falling back to text parsing")
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
        expected_output=f"""IMPORTANT: You must return your response in this EXACT format:

```json
{{
    "article_title": "Extract the actual article/chapter title from the PDF content (NOT the filename)",
    "key_concepts": "ONLY bullet points with key concepts and definitions - no introductory text",
    "relevance": "ONLY bullet points explaining relevance to Livia's interests - no introductory text"
}}
```

CRITICAL REQUIREMENTS:
1. Extract the actual article/chapter title from within the PDF content - look for titles like "Chapter 1: Introduction" or "The Future of AI in Education" etc.
2. key_concepts: Start directly with bullet points (• or *) - NO introductory phrases like "The main ideas are:" or "Key concepts include:"
3. relevance: Start directly with bullet points (• or *) - NO introductory phrases like "This is relevant because:" or "Why this matters:"
4. Each bullet point should be a complete, standalone statement
5. Return ONLY the JSON format above - no additional text or explanations
6. The JSON must be valid and parseable
7. Both key_concepts and relevance must be STRINGS, not arrays""",
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
        # LLM configuration: support OpenAI, Gemini, and default
        llm_type = os.environ.get("LLM_TYPE", "default").lower()
        print(f"🔧 Using LLM: {llm_type.upper()}")
        
        if llm_type == "default":
            # Use no LLM - just run the agents without AI
            print("🔄 Running without LLM (demo mode)...")
            llm = None
            print("✅ Running in demo mode")
        
        elif llm_type == "gemini":
            # Configure Gemini LLM using LiteLLM format
            gemini_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
            gemini_key = os.environ.get("GEMINI_API_KEY")
            if not gemini_key:
                print("⚠️  Warning: GEMINI_API_KEY not found. Falling back to Hugging Face.")
                llm_type = "huggingface"
            else:
                # Set the API key for Google
                os.environ["GOOGLE_API_KEY"] = gemini_key
                # Use LiteLLM format for Gemini
                llm = f"gemini/{gemini_model}"
                print(f"✅ Gemini configured with model: {gemini_model}")
        
        elif llm_type == "openai":
            # Configure OpenAI LLM
            openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                print("⚠️  Warning: OPENAI_API_KEY not found. Falling back to Hugging Face.")
                llm_type = "huggingface"
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
        
        if llm is None:
            # Demo mode - show expected outputs without running crew
            print("\n🚀 Running in DEMO MODE...")
            print("="*60)
            print("🎉 DEMO EXECUTION COMPLETED!")
            print("="*60)
            
            # Show demo interview results
            print("\n📝 INTERVIEW PREPARATION RESULTS:")
            print("-" * 40)
            print("""
# Interview Preparation

## Potential Questions:
1. Tell me about yourself and your experience with AI in education.
2. How would you approach designing learning experiences for marginalized communities?
3. Describe a time when you had to adapt your teaching methods for different learning styles.

## Answers (STAR Method):
1. **Situation**: In my previous role, I worked on developing AI-powered educational tools.
**Task**: I needed to create accessible learning platforms for underserved communities.
**Action**: I collaborated with community leaders and educators to understand their specific needs.
**Result**: Successfully launched a program that increased engagement by 40%.

## Tips for Confidence:
- Practice your answers out loud
- Prepare specific examples from your experience
- Research the company's mission and values
- Prepare thoughtful questions to ask them
            """)
            
            if summarize_pdf and excel_path:
                # Create demo Excel file
                print(f"\n📊 Creating demo Excel file: {excel_path}")
                try:
                    import pandas as pd
                    data = {
                        'Name': ['The Future of AI in Education'],
                        'Key concepts & Definitions': ['• Artificial Intelligence in Education (AIEd) - The use of AI technologies to enhance learning experiences\n• Personalized Learning - Tailoring educational content to individual student needs\n• Learning Analytics - The measurement and analysis of learning data to improve outcomes'],
                        'Relevance & Curiosity': ['• Directly relevant to Livia\'s interests in leveraging AI for educational equity\n• Connects to her work with marginalized communities and learning design\n• Provides insights into career readiness and K-12 education applications']
                    }
                    df = pd.DataFrame(data)
                    df.to_excel(excel_path, index=False)
                    print(f"✅ Demo Excel file created: {excel_path}")
                except Exception as e:
                    print(f"❌ Error creating demo Excel: {e}")
        else:
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
                    # Check if Excel file was created by the agent
                    if os.path.exists(excel_path):
                        print(f"✅ Excel file created successfully by agent: {excel_path}")
                    else:
                        print(f"⚠️  Excel file not found at expected location: {excel_path}")
                        print("The agent should have created the Excel file directly.")
                
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