import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables from .env file
load_dotenv()

class BaseAgent:
    def __init__(self, name: str, system_instruction: str):
        self.name = name
        self.system_instruction = system_instruction
        self._client = None
        self._model = "gemini-2.5-flash"

    def get_client(self):
        """Initializes and returns the GenAI Client, retrieving the key from environment or streamlit session."""
        if self._client is not None:
            return self._client

        # First, try to get GEMINI_API_KEY from environment (loaded via dotenv)
        api_key = os.getenv("GEMINI_API_KEY")

        # Fallback to Streamlit session state if available (allows user to enter it in UI)
        if not api_key and "gemini_api_key" in st.session_state and st.session_state["gemini_api_key"]:
            api_key = st.session_state["gemini_api_key"]

        if not api_key:
            raise ValueError(
                f"[{self.name}] GEMINI_API_KEY is not configured. Please add it to your '.env' file or enter it in the dashboard settings."
            )

        # Initialize Google GenAI client
        self._client = genai.Client(api_key=api_key)
        return self._client

    def log_thought(self, message: str):
        """Log the agent's internal thoughts to Streamlit session state so it can be rendered live."""
        if "agent_logs" not in st.session_state:
            st.session_state["agent_logs"] = []
        log_entry = f"[{self.name}] {message}"
        st.session_state["agent_logs"].append(log_entry)
        print(log_entry) # Also print to terminal for debugging

    def generate_structured(self, prompt: str, schema):
        """Generates structured content conforming to a Pydantic schema."""
        self.log_thought(f"Generating structured response matching schema '{schema.__name__}'...")
        try:
            client = self.get_client()
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2, # Lower temperature for more factual structuring
                )
            )
            self.log_thought("Structured response generation succeeded.")
            return response.parsed
        except APIError as e:
            self.log_thought(f"Gemini API Error occurred: {str(e)}")
            raise e
        except Exception as e:
            self.log_thought(f"Unexpected error during structured generation: {str(e)}")
            raise e

    def generate_chat(self, prompt: str, history=None) -> str:
        """Generates a standard unstructured text response (chat format)."""
        self.log_thought("Generating chat response...")
        try:
            client = self.get_client()
            
            # Format contents based on optional history
            contents = []
            if history:
                for role, text in history:
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)]
                    ))
            contents.append(prompt)

            response = client.models.generate_content(
                model=self._model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,
                )
            )
            self.log_thought("Chat response generation succeeded.")
            return response.text
        except APIError as e:
            self.log_thought(f"Gemini API Error occurred: {str(e)}")
            raise e
        except Exception as e:
            self.log_thought(f"Unexpected error during chat generation: {str(e)}")
            raise e
