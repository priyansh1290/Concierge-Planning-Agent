import os
import json
from typing import Optional, Dict, Any, List
from agents.base import BaseAgent
from models import UserPreferences, ProjectProposal, DailyTask

class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Memory Agent",
            system_instruction=(
                "You are the Memory Agent. Your job is to organize, summarize, and record the user's history, "
                "active projects, and learning preferences. You extract key details from user actions to build "
                "a long-term profile of their strengths and focus areas."
            )
        )
        self.db_path = "memory_store.json"
        self._init_db()

    def _init_db(self):
        """Initializes the JSON database if it does not exist."""
        if not os.path.exists(self.db_path):
            self.save_state({
                "preferences": None,
                "active_project": None,
                "project_history": [],
                "user_summary": "New user with no project history."
            })

    def load_state(self) -> Dict[str, Any]:
        """Loads the full state from the JSON file."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.log_thought(f"Error loading state: {str(e)}. Reinitializing database.")
            self._init_db()
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)

    def save_state(self, state: Dict[str, Any]):
        """Saves the given state to the JSON file."""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4, ensure_ascii=False)
            self.log_thought("State successfully saved to memory_store.json")
        except Exception as e:
            self.log_thought(f"Error saving state: {str(e)}")

    def get_preferences(self) -> Optional[UserPreferences]:
        """Gets user preferences if stored."""
        state = self.load_state()
        pref_data = state.get("preferences")
        if pref_data:
            return UserPreferences(**pref_data)
        return None

    def save_preferences(self, preferences: UserPreferences):
        """Saves user preferences."""
        state = self.load_state()
        state["preferences"] = preferences.model_dump()
        self.save_state(state)
        self.log_thought(f"Preferences updated: {preferences.interests}, {preferences.hours_per_day}h/day.")

    def get_active_project(self) -> Optional[ProjectProposal]:
        """Gets the currently active project."""
        state = self.load_state()
        project_data = state.get("active_project")
        if project_data:
            return ProjectProposal(**project_data)
        return None

    def save_active_project(self, project: ProjectProposal):
        """Sets the active project."""
        state = self.load_state()
        state["active_project"] = project.model_dump()
        self.save_state(state)
        self.log_thought(f"Active project saved: '{project.name}' ({project.total_days} days).")

    def abandon_active_project(self, reason: str = "Abandoned by user"):
        """Abandons the active project and moves it to history."""
        state = self.load_state()
        project_data = state.get("active_project")
        if project_data:
            project_data["status"] = "Abandoned"
            project_data["abandon_reason"] = reason
            state["project_history"].append(project_data)
            state["active_project"] = None
            self.save_state(state)
            self.log_thought(f"Project '{project_data.get('name')}' abandoned. Reason: {reason}")
            self.update_user_summary()
        else:
            self.log_thought("No active project to abandon.")

    def complete_active_project(self):
        """Marks the active project as completed and moves it to history."""
        state = self.load_state()
        project_data = state.get("active_project")
        if project_data:
            project_data["status"] = "Completed"
            state["project_history"].append(project_data)
            state["active_project"] = None
            self.save_state(state)
            self.log_thought(f"Project '{project_data.get('name')}' completed! Moving to history.")
            self.update_user_summary()
        else:
            self.log_thought("No active project to complete.")

    def update_task_completion(self, day: int, task_title: str, completed: bool):
        """Updates the completion status of a specific daily task."""
        state = self.load_state()
        project_data = state.get("active_project")
        if project_data:
            for task in project_data.get("daily_tasks", []):
                if task.get("day") == day and task.get("title") == task_title:
                    task["completed"] = completed
                    self.save_state(state)
                    self.log_thought(f"Task '{task_title}' on day {day} set to completed={completed}.")
                    break
        else:
            self.log_thought("No active project to update task completion.")

    def update_user_summary(self):
        """Uses Gemini to summarize the user's progress and update their profile summary."""
        state = self.load_state()
        history = state.get("project_history", [])
        if not history:
            state["user_summary"] = "New user with no project history."
            self.save_state(state)
            return

        # Prepare summary prompt
        summary_prompt = f"Analyze the following history of user projects and summarize their achievements, strengths, and preferences:\n"
        for i, proj in enumerate(history):
            tasks = proj.get("daily_tasks", [])
            completed_tasks = [t for t in tasks if t.get("completed")]
            completion_rate = (len(completed_tasks) / len(tasks)) * 100 if tasks else 0
            summary_prompt += (
                f"- Project {i+1}: {proj.get('name')} | Status: {proj.get('status')} | "
                f"Completed: {len(completed_tasks)}/{len(tasks)} tasks ({completion_rate:.1f}%)\n"
            )
            if "abandon_reason" in proj:
                summary_prompt += f"  Reason for abandonment: {proj.get('abandon_reason')}\n"

        try:
            summary = self.generate_chat(summary_prompt)
            state["user_summary"] = summary
            self.save_state(state)
            self.log_thought("User achievements and learning summary updated.")
        except Exception as e:
            self.log_thought(f"Failed to update user summary using LLM: {str(e)}")
