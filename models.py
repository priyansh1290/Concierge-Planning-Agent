from pydantic import BaseModel, Field
from typing import List, Optional

class UserPreferences(BaseModel):
    interests: List[str] = Field(..., description="List of topics, technologies, or subjects the user is interested in.")
    hours_per_day: float = Field(..., description="Number of hours the user can dedicate to the project per day (minimum 0.5, maximum 24).")
    skill_level: str = Field(..., description="The user's experience level: 'Beginner', 'Intermediate', or 'Advanced'.")
    target_duration_days: int = Field(..., description="The target duration of the project in days.")

class DailyTask(BaseModel):
    day: int = Field(..., description="The day number of the project (1-indexed).")
    title: str = Field(..., description="Short title of the task.")
    description: str = Field(..., description="Brief description of what needs to be done.")
    estimated_hours: float = Field(..., description="Estimated hours to complete this task.")
    completed: bool = Field(default=False, description="Whether the task has been marked as completed.")

class ProjectProposal(BaseModel):
    name: str = Field(..., description="A creative and catchy name for the project.")
    description: str = Field(..., description="A high-level summary of what the project is and what the user will build/learn.")
    difficulty: str = Field(..., description="Assessed difficulty level matching user skill level (e.g. Beginner, Intermediate, Advanced).")
    total_days: int = Field(..., description="Total duration of the project in days.")
    daily_tasks: List[DailyTask] = Field(..., description="Chronological list of tasks, one or more for each day of the project.")

class ReconfiguredSchedule(BaseModel):
    justification: str = Field(..., description="Explanation of how and why the schedule is being adjusted based on current progress.")
    revised_tasks: List[DailyTask] = Field(..., description="The list of all remaining tasks, rescheduled to fit the remaining timeline and pace.")
