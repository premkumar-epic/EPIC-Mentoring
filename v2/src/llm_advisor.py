import os
import json
from google import genai
from google.genai import types

class LLMAdvisor:
    """
    Integrates the Gemini API to handle complex tasks:
    1. Legally compliant resource suggestions (using Google Search grounding).
    2. Contextual session tips for mentors.
    """
    def __init__(self):
        # Initialize the client using the GEMINI_API_KEY environment variable
        try:
            self.client = genai.Client()
            self.model = 'gemini-2.5-flash'
            print("LLM Advisor Initialized with Gemini Client.")
        except Exception as e:
            print(f"Error initializing Gemini client: {e}. Ensure GEMINI_API_KEY is set.")
            self.client = None

    def _call_gemini_with_safety(self, prompt, tools=None):
        """Standardized function for making API calls with a system instruction."""
        if not self.client:
            return "LLM Service is offline. Check API key."

        config = types.GenerateContentConfig(
            # System instruction to enforce legal/accuracy constraints
            system_instruction="You are a professional educational and legal compliance AI advisor. All advice must be accurate, respectful, and include a clear disclaimer that it is not a substitute for official school policy.",
            tools=tools,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt],
            config=config
        )

        return response.text

    # --- 1. Student Query Function (Legal & Accuracy Compliance) ---

    def suggest_resources(self, query):
        """
        Generates legally compliant, accurate advice.
        Uses the Google Search tool for grounding (RAG) to ensure accuracy.
        """
        prompt = (
            f"As an educational consultant, analyze the following student query and provide a structured, helpful response. "
            f"The response MUST include a clear academic/legal disclaimer at the end. "
            f"Query: {query}"
        )

        # Enable the Google Search tool for grounding (RAG)
        tools = [{"google_search": {}}]

        response_text = self._call_gemini_with_safety(prompt, tools=tools)

        # Format for HTML display in the student portal
        return response_text.replace('\n', '<br>')

    # --- 2. Mentor Session Prep Function ---

    def generate_session_tips(self, student_data, mentor_assessment):
        """
        Analyzes mentor input and student data to generate actionable session tips.
        """
        student_summary = json.dumps(student_data, indent=2)
        assessment_summary = "\n".join([f"- {k}: {v}" for k, v in mentor_assessment.items()])

        prompt = (
            f"You are an AI counseling coach. Generate a 3-point actionable plan for the mentor. "
            f"The tips should combine the student's data and the mentor's perspective. "
            f"Focus on session flow, empathy points, and specific resources.\n\n"
            f"--- STUDENT DATA ---\n{student_summary}\n\n"
            f"--- MENTOR ASSESSMENT ---\n{assessment_summary}"
        )

        response_text = self._call_gemini_with_safety(prompt)

        # Format the response clearly for the mentor dashboard
        # Assuming the LLM returns a list-like structure, replace dashes with bullet points
        html_content = f"<p class='font-bold text-lg text-mentor-green'>AI-Generated Session Plan:</p>"
        html_content += f"<ul class='list-disc list-inside space-y-2'>"

        for line in response_text.split('\n'):
            if line.strip():
                 html_content += f"<li>{line.strip('- ').strip()}</li>"

        html_content += f"</ul>"

        return html_content

    # --- 3. Career Path Analysis ---

    def analyze_career_path(self, assessment_data):
        """Generates the initial draft of the career report based on psychometric answers."""
        # The prompt is simpler here, focusing on profile analysis
        prompt = (
            f"Analyze the following psychometric assessment data (scores 1=Strongly Disagree, 5=Strongly Agree) "
            f"to recommend 3 primary career paths and explain the reasoning based on the scores. "
            f"Assessment Data: {json.dumps(assessment_data)}"
        )
        response_text = self._call_gemini_with_safety(prompt)
        return response_text.replace('\n', '<br>')
