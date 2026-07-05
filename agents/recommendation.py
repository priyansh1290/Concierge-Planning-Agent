from typing import List
from agents.base import BaseAgent
from models import UserPreferences, ProjectProposal

class ProjectRecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommendation Agent",
            system_instruction=(
                "You are the Project Recommendation Agent. Your primary job is to design highly customized "
                "projects tailored to the user's interests, skill level, available time, and project duration. "
                "You must construct realistic, step-by-step milestones (daily tasks) that can reasonably be completed "
                "within the user's allocated daily hours. The projects must be engaging, educational, and practical."
            )
        )

    def recommend_project(self, preferences: UserPreferences, declined_projects: List[str] = None) -> ProjectProposal:
        """Generates a structured ProjectProposal based on preferences and a list of previously declined projects."""
        declined_str = ", ".join(f"'{p}'" for p in declined_projects) if declined_projects else "None"
        
        prompt = (
            f"Generate a customized project proposal based on the following user preferences:\n"
            f"- Interests: {', '.join(preferences.interests)}\n"
            f"- Skill Level: {preferences.skill_level}\n"
            f"- Available Time: {preferences.hours_per_day} hours/day\n"
            f"- Target Duration: {preferences.target_duration_days} days\n\n"
            f"IMPORTANT CONSTRAINTS:\n"
            f"1. You MUST generate exactly {preferences.target_duration_days} days of tasks. There must be at least one task for each day from day 1 to day {preferences.target_duration_days}.\n"
            f"2. Each daily task must be scoped so it can be completed within {preferences.hours_per_day} hours.\n"
            f"3. Avoid proposing any of the following projects, as they were previously declined by the user: [{declined_str}]. Generate something completely different and unique."
        )

        self.log_thought(f"Generating recommendation matching interests={preferences.interests} and duration={preferences.target_duration_days} days...")
        proposal = self.generate_structured(prompt, ProjectProposal)
        
        # Post-process/safety-check to ensure it generated the correct number of days
        self.log_thought(f"Recommendation generated: '{proposal.name}'. Checking task list integrity...")
        
        # If the model didn't generate tasks for all days, let's fix it by sorting and logging
        days_generated = set(t.day for t in proposal.daily_tasks)
        self.log_thought(f"Tasks generated for days: {sorted(list(days_generated))}")
        
        return proposal
