from agents.base import BaseAgent
from models import UserPreferences

class PreferenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Preference Agent",
            system_instruction=(
                "You are the Preference Agent. Your primary job is to extract, analyze, and validate "
                "user preferences (interests, daily hours available, skill level, and target project duration). "
                "You convert unstructured user inputs into structured configuration details. If any critical "
                "parameters are missing or highly unrealistic (e.g., negative hours, blank interests), you flag them."
            )
        )

    def parse_preferences(self, user_input: str) -> UserPreferences:
        """Parses a raw string of user preferences into a structured UserPreferences model using Gemini."""
        prompt = (
            f"Parse the following user request and extract their preferences into the required structure. "
            f"For duration, if not specified, default to 7 days. For skill level, default to 'Intermediate'. "
            f"Ensure hours per day is a positive number between 0.5 and 24.\n\n"
            f"User Request: \"{user_input}\""
        )
        self.log_thought(f"Parsing preferences from raw input: '{user_input[:60]}...'")
        preferences = self.generate_structured(prompt, UserPreferences)
        self.log_thought("Parsing complete. Preferences extracted successfully.")
        return preferences

    def validate_preferences(self, preferences: UserPreferences) -> tuple[bool, str]:
        """Validates preferences and returns (is_valid, error_message)."""
        if not preferences.interests:
            return False, "Please list at least one interest or topic you would like to work on."
        if preferences.hours_per_day < 0.5:
            return False, "Available time must be at least 0.5 hours (30 minutes) per day."
        if preferences.hours_per_day > 16.0:
            return False, "Working more than 16 hours a day is highly unsustainable and may lead to severe burnout. Please allocate 16 hours or less."
        if preferences.target_duration_days <= 0:
            return False, "Project duration must be at least 1 day."
        if preferences.skill_level not in ["Beginner", "Intermediate", "Advanced"]:
            return False, f"Invalid skill level '{preferences.skill_level}'. Must be 'Beginner', 'Intermediate', or 'Advanced'."
        
        return True, ""
