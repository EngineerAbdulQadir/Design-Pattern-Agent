from crewai.flow import Flow, start
from design_pattern_agent.crews.design_crew.design_crew import DesignCrew, voice_interaction, speak, listen

class DesignFlow(Flow):

    @start()
    def crew_run(self):
        user_problem = voice_interaction()
        
        design_crew = DesignCrew()
        original_desc = design_crew.tasks_config["apply_anthropic_pattern"]["description"]
        updated_desc = original_desc + "\nUser's problem: " + user_problem
        design_crew.tasks[0].description = updated_desc


        speak("I am now processing your request. Please wait while I work on your problem.")
        print("Processing your request...")

        output = design_crew.crew().kickoff(inputs={"problem": user_problem})
        final_output = output.raw


        speak("Would you like me to read the output? Please say yes or no.")
        answer = listen().lower().strip()
        if "yes" in answer:
            speak("The final output is: " + final_output)
        else:
            speak("Your output is ready and has been saved in DesignPattern.md.")

        print("Final output:")
        print(final_output)
        
        with open("DesignPattern.md", "w", encoding="utf-8") as f:
            f.write(final_output)
        speak("The output has been saved to DesignPattern.md.")
        print("Output saved to DesignPattern.md")
        return final_output

def kickoff():
    flow = DesignFlow()
    flow.kickoff()
