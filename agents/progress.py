from typing import List
from agents.base import BaseAgent
from models import UserPreferences, DailyTask, ReconfiguredSchedule, ProjectProposal

class ProgressAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Progress Agent",
            system_instruction=(
                "You are the Progress and Reconfiguration Agent. Your primary job is to track the user's progress "
                "against their project schedule, identify when they are falling behind or struggling, and dynamically "
                "reconfigure their roadmap. You adjust the schedule by redistributing pending tasks, breaking them down, "
                "or scaling down scope so that they can finish the project without feeling overloaded or experiencing burnout."
            )
        )

    def analyze_and_reconfigure(
        self,
        preferences: UserPreferences,
        project: ProjectProposal,
        current_day: int
    ) -> ReconfiguredSchedule:
        """Analyzes the completed vs. pending tasks and uses Gemini to reconfigure the schedule."""
        self.log_thought("Analyzing current task progress and scheduling status...")
        
        # Format task progress for the prompt
        tasks_status_str = ""
        completed_count = 0
        pending_count = 0
        
        for task in project.daily_tasks:
            status = "[COMPLETED]" if task.completed else "[PENDING]"
            if task.completed:
                completed_count += 1
            else:
                pending_count += 1
            tasks_status_str += f"- Day {task.day}: {task.title} | {task.description} | {task.estimated_hours}h | Status: {status}\n"

        self.log_thought(f"Progress summary: {completed_count} completed, {pending_count} pending. Current Day: {current_day}")

        # Construct Prompt for reconfiguration
        prompt = (
            f"The user is working on the project: '{project.name}' (Difficulty: {project.difficulty}).\n"
            f"Here are their preferences:\n"
            f"- Interests: {', '.join(preferences.interests)}\n"
            f"- Skill Level: {preferences.skill_level}\n"
            f"- Time available: {preferences.hours_per_day} hours/day\n"
            f"- Total project duration: {project.total_days} days\n"
            f"- Current day of execution: Day {current_day}\n\n"
            f"Here is the status of all daily tasks in the project:\n"
            f"{tasks_status_str}\n"
            f"The user has fallen behind or progress is not matching the original deadlines. "
            f"Please reconfigure the remaining PENDING tasks. Keep completed tasks as they are.\n\n"
            f"CONSTRAINTS:\n"
            f"1. Do NOT modify the overall project duration. The project must still complete by Day {project.total_days}.\n"
            f"2. You must reschedule the pending tasks across the remaining days (Day {current_day} to Day {project.total_days}).\n"
            f"3. Each day's new combined workload must not exceed the user's available time of {preferences.hours_per_day} hours/day. "
            f"If there are too many pending tasks, you must simplify the scope, reduce the estimated hours, or merge tasks, "
            f"clearly explaining your reasoning in the 'justification' field.\n"
            f"4. The output must contain the full list of revised tasks for the remaining days, preserving the original day indexing."
        )

        reconfigured = self.generate_structured(prompt, ReconfiguredSchedule)
        
        self.log_thought("Reconfiguration complete. Adjustments structured successfully.")
        return reconfigured
