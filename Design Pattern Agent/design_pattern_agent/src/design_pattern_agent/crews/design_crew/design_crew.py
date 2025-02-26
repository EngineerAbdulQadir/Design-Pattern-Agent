import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai import LLM
import speech_recognition as sr
import pyttsx3

load_dotenv()

llm1_model = LLM(
    provider="google",
    model=os.getenv("MODEL", "gemini/gemini-1.5-flash"),
    api_key=os.getenv("GEMINI_API_KEY"),
    config={
        "temperature": 0.7,
        "max_tokens": 2048
    }
)

def speak(text: str):
    """Convert text to speech and log it."""
    print("[Agent says]:", text)
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen() -> str:
    """Listen for voice input and return the recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening for your response.")
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        recognized_text = recognizer.recognize_google(audio)
        return recognized_text
    except Exception as e:
        print("Error recognizing speech:", e)
        speak("Sorry, I could not understand you.")
        return ""

def voice_interaction() -> str:
    """
    Greets the user, asks for the problem, listens for input, and repeats it.
    If no input is captured, returns a default problem statement.
    """
    speak("Hi, I am Design Pattern Agent powered by Xactrix AI.")
    speak("Please state your problem.")
    problem_statement = listen()
    if not problem_statement:
        default_problem = (
            "Analyze the given codebase, detect applicable design patterns, "
            "suggest improvements based on Anthropic guidelines, and provide a structured refactoring plan"
        )
        speak("No problem statement was captured. Using default problem statement: " + default_problem)
        return default_problem
    else:
        speak("You said: " + problem_statement)
        return problem_statement

class DesignCrew:
    def __init__(self):
        agents_path = os.path.join(os.path.dirname(__file__), "config", "agents.yaml")
        tasks_path = os.path.join(os.path.dirname(__file__), "config", "tasks.yaml")
        
        with open(agents_path, 'r', encoding='utf-8') as f:
            self.agents_config = yaml.safe_load(f)
        with open(tasks_path, 'r', encoding='utf-8') as f:
            self.tasks_config = yaml.safe_load(f)

        self.design_agent = Agent(
            role=self.agents_config["design_agent"]["role"],
            goal=self.agents_config["design_agent"]["goal"],
            backstory=self.agents_config["design_agent"]["backstory"],
            llm=llm1_model,
            verbose=True
        )
        
        self.review_agent = Agent(
            role=self.agents_config["review_agent"]["role"],
            goal=self.agents_config["review_agent"]["goal"],
            backstory=self.agents_config["review_agent"]["backstory"],
            llm=llm1_model,
            verbose=True
        )

        self.refactoring_agent = Agent(
            role=self.agents_config["refactoring_agent"]["role"],
            goal=self.agents_config["refactoring_agent"]["goal"],
            backstory=self.agents_config["refactoring_agent"]["backstory"],
            llm=llm1_model,
            verbose=True
        )

        self.tasks = [
            Task(
                description=self.tasks_config["apply_anthropic_pattern"]["description"],
                expected_output=self.tasks_config["apply_anthropic_pattern"]["expected_output"],
                agent=self.design_agent
            ),
            Task(
                description=self.tasks_config["review_design_pattern"]["description"],
                expected_output=self.tasks_config["review_design_pattern"]["expected_output"],
                agent=self.review_agent
            ),
            Task(
                description=self.tasks_config["propose_refactoring_plan"]["description"],
                expected_output=self.tasks_config["propose_refactoring_plan"]["expected_output"],
                agent=self.refactoring_agent
            )
        ]

    def crew(self) -> Crew:
        return Crew(
            agents=[self.design_agent, self.review_agent, self.refactoring_agent],
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
