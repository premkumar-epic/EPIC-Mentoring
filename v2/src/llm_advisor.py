import os
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError # Import specific error type

class LLMAdvisor:
    """
    Integrates the Gemini API to handle complex tasks with robust error handling.
    """
    def __init__(self):
        try:
            self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            self.model = 'gemini-2.5-flash'
            print("LLM Advisor Initialized with Gemini Client.")
        except Exception as e:
            print(f"Error initializing Gemini client: {e}. Check API key and dependencies.")
            self.client = None

    def _call_gemini_with_safety(self, prompt, tools=None):
        """Standardized function for making API calls with safety and error handling."""
        if not self.client:
            return "<p class='text-red-500'>[AI OFFLINE] LLM Service is not available. Please check the GEMINI_API_KEY.</p>"

        config = types.GenerateContentConfig(
            system_instruction="You are a professional educational and legal compliance AI advisor. All advice must be accurate, respectful, and include a clear disclaimer that it is not a substitute for official school policy.",
            tools=tools,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=config
            )
            return response.text
        except APIError as e:
            print(f"Gemini API Error: {e}")
            return f"<p class='text-red-500'>[API ERROR] The AI service failed to generate a response (Code: {e.status_code}). Please try again later.</p>"
        except Exception as e:
            print(f"General AI Error: {e}")
            return f"<p class='text-red-500'>[NETWORK ERROR] Could not connect to the AI service. (Details: {str(e)})</p>"


    def suggest_resources(self, query):
        """Generates legally compliant, accurate advice, using Google Search grounding."""
        prompt = (
            f"As an educational consultant, analyze the following student query and provide a structured, helpful response. "
            f"Query: {query}"
        )
        tools = [{"google_search": {}}]
        response_text = self._call_gemini_with_safety(prompt, tools=tools)
        return response_text.replace('\n', '<br>')

    def generate_session_tips(self, student_data, mentor_assessment):
        """Analyzes mentor input and student data to generate actionable session tips."""
        # ... (Keep the existing prompt preparation logic here) ...
        student_summary = json.dumps(student_data, indent=2)
        assessment_summary = "\n".join([f"- {k}: {v}" for k, v in mentor_assessment.items()])

        prompt = (
            f"You are an AI counseling coach. Generate a 3-point actionable plan for the mentor. "
            f"The tips should combine the student's data and the mentor's perspective. \n\n"
            f"--- STUDENT DATA ---\n{student_summary}\n\n"
            f"--- MENTOR ASSESSMENT ---\n{assessment_summary}"
        )

        response_text = self._call_gemini_with_safety(prompt)

        # Format the response clearly for the mentor dashboard
        html_content = f"<p class='font-bold text-lg text-mentor-green'>AI-Generated Session Plan:</p><ul class='list-disc list-inside space-y-2'>"
        for line in response_text.split('\n'):
            if line.strip():
                 html_content += f"<li>{line.strip('- ').strip()}</li>"
        html_content += f"</ul>"

        return html_content

    def analyze_career_path(self, assessment_data):
        """Generates the initial draft of the career report based on psychometric answers."""
        prompt = (
            f"Analyze the following psychometric assessment data to recommend 3 primary career paths and explain the reasoning. "
            f"Assessment Data: {json.dumps(assessment_data)}"
        )
        response_text = self._call_gemini_with_safety(prompt)
        return response_text.replace('\n', '<br>')
