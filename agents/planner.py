from typing import List, Optional, Tuple, Dict, Any
from agents.base import BaseAgent
from agents.preference import PreferenceAgent
from agents.recommendation import ProjectRecommendationAgent
from agents.memory import MemoryAgent
from agents.progress import ProgressAgent
from models import UserPreferences, ProjectProposal, DailyTask, ReconfiguredSchedule

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner Orchestrator (Root)",
            system_instruction=(
                "You are the root Planner Orchestrator Agent. Your job is to coordinate the Preference, "
                "Recommendation, Memory, and Progress agents. You manage the user interaction state machine, "
                "resolve conflicts, enforce system safety constraints (like single active project limits), "
                "and ensure a high-quality user experience."
            )
        )
        # Initialize sub-agents
        self.preference_agent = PreferenceAgent()
        self.recommendation_agent = ProjectRecommendationAgent()
        self.memory_agent = MemoryAgent()
        self.progress_agent = ProgressAgent()

    def process_preferences(self, raw_input: str) -> Tuple[bool, str]:
        """Tells the Preference Agent to parse and validate user preferences, then saves them to memory."""
        self.log_thought("Processing user preferences input...")
        
        # Check if there is already an active project
        active_project = self.memory_agent.get_active_project()
        if active_project:
            self.log_thought("Preference update blocked: An active project already exists.")
            return False, "You cannot update preferences or start a new project while you have an active project. Please complete or abandon it first."

        try:
            # Parse preferences
            prefs = self.preference_agent.parse_preferences(raw_input)
            
            # Validate preferences
            is_valid, error_msg = self.preference_agent.validate_preferences(prefs)
            if not is_valid:
                self.log_thought(f"Preference validation failed: {error_msg}")
                return False, error_msg
            
            # Save to memory
            self.memory_agent.save_preferences(prefs)
            self.log_thought("Preferences processed and saved successfully.")
            return True, "Preferences successfully configured."
        except Exception as e:
            error_msg = f"Failed to process preferences: {str(e)}"
            self.log_thought(error_msg)
            return False, error_msg

    def get_recommendation(self, declined_projects: List[str] = None) -> Tuple[Optional[ProjectProposal], str]:
        """Gets a project recommendation. Validates that preferences exist and that the user does not have an active project."""
        self.log_thought("Orchestrating project recommendation request...")

        # 1. Enforce single project safety constraint
        active_project = self.memory_agent.get_active_project()
        if active_project:
            self.log_thought("Recommendation blocked: User has an active project.")
            return None, "You are not allowed to work on more than one project. It will lead to burnout!"

        # 2. Check if preferences are set
        prefs = self.memory_agent.get_preferences()
        if not prefs:
            self.log_thought("Recommendation blocked: No user preferences found.")
            return None, "Please configure your learning preferences before requesting a project recommendation."

        try:
            # 3. Call recommendation agent
            proposal = self.recommendation_agent.recommend_project(prefs, declined_projects)
            self.log_thought(f"Orchestrator received proposal: '{proposal.name}'")
            return proposal, ""
        except Exception as e:
            error_msg = f"Failed to get recommendation: {str(e)}"
            self.log_thought(error_msg)
            return None, error_msg

    def accept_project(self, project: ProjectProposal) -> Tuple[bool, str]:
        """Saves the project as the active project in memory."""
        self.log_thought(f"Orchestrator handling project acceptance for: '{project.name}'")
        
        # Enforce safety check
        active_project = self.memory_agent.get_active_project()
        if active_project:
            return False, "You already have an active project. Abandon or complete it first."

        try:
            self.memory_agent.save_active_project(project)
            self.log_thought(f"Project '{project.name}' is now active!")
            return True, f"Project '{project.name}' started!"
        except Exception as e:
            error_msg = f"Failed to accept project: {str(e)}"
            self.log_thought(error_msg)
            return False, error_msg

    def abandon_project(self, reason: str = "Abandoned by user") -> Tuple[bool, str]:
        """Abandons the active project so the user can start a new one."""
        self.log_thought("Orchestrating project abandonment...")
        try:
            self.memory_agent.abandon_active_project(reason)
            return True, "Project successfully abandoned. You are now free to start a new project."
        except Exception as e:
            error_msg = f"Failed to abandon project: {str(e)}"
            self.log_thought(error_msg)
            return False, error_msg

    def complete_project(self) -> Tuple[bool, str]:
        """Marks the active project as completed."""
        self.log_thought("Orchestrating project completion...")
        try:
            self.memory_agent.complete_active_project()
            return True, "Congratulations on completing your project! Your achievements have been saved in memory."
        except Exception as e:
            error_msg = f"Failed to complete project: {str(e)}"
            self.log_thought(error_msg)
            return False, error_msg

    def reconfigure_schedule(self, current_day: int) -> Tuple[Optional[ReconfiguredSchedule], str]:
        """Triggers the Progress Agent to review task status and re-budget remaining tasks."""
        self.log_thought("Orchestrating schedule reconfiguration...")
        
        active_project = self.memory_agent.get_active_project()
        if not active_project:
            return None, "No active project found to reconfigure."

        prefs = self.memory_agent.get_preferences()
        if not prefs:
            return None, "Preferences missing."

        try:
            # 1. Generate reconfigured tasks
            reconfigured = self.progress_agent.analyze_and_reconfigure(prefs, active_project, current_day)
            
            # 2. Update active project tasks in memory
            # Map the revised tasks back to the active project
            revised_task_map = {t.day: t for t in reconfigured.revised_tasks}
            updated_tasks = []
            
            for task in active_project.daily_tasks:
                if task.completed:
                    updated_tasks.append(task)
                elif task.day in revised_task_map:
                    revised_t = revised_task_map[task.day]
                    # Retain completion status (it should be False since it was pending, but just in case)
                    updated_tasks.append(DailyTask(
                        day=task.day,
                        title=revised_t.title,
                        description=revised_t.description,
                        estimated_hours=revised_t.estimated_hours,
                        completed=task.completed
                    ))
                else:
                    updated_tasks.append(task)
                    
            active_project.daily_tasks = updated_tasks
            self.memory_agent.save_active_project(active_project)
            
            self.log_thought(f"Project schedule reconfigured successfully: '{reconfigured.justification[:60]}...'")
            return reconfigured, ""
        except Exception as e:
            error_msg = f"Failed to reconfigure schedule: {str(e)}"
            self.log_thought(error_msg)
            return None, error_msg
