Concierge Planning Agent

A multi-agent personal scheduler and project assistant built with Gemini 2.5 Flash and Streamlit for the Google & Kaggle AI Agents Intensive Capstone Project (Concierge Agent Track).


What is this project?

When learning new skills or building personal projects, it is easy to set unrealistic goals, fall behind, and eventually burn out. Standard calendar tools do not understand the difficulty of your tasks or adapt when life gets busy.

The Concierge Planning Agent solves this by acting as your personal project manager. It takes your interests, experience level, and daily time budget, then builds a custom project plan with daily milestones tailored specifically for you.

If you fall behind on your schedule, the system does not just leave overdue tasks pending. Instead, its Progress Agent steps in to analyze your actual pace and automatically reconfigures your remaining schedule so you can finish without feeling overwhelmed.


Key Features

- Personalized Project Generation: Recommends customized project blueprints based on your interests, skill level, and daily availability.
- Burnout Prevention: Enforces a strict single active project limit. You cannot start a new project until you complete or abandon your current one.
- Dynamic Reconfiguration: If you fall behind, the Progress Agent dynamically re-budgets remaining tasks to fit your available hours.
- Persistent Memory: Saves project history and progress to a local JSON file (memory_store.json), allowing the agent to remember your past achievements and summarize your learning trajectory over time.
- Live Agent Console: A real-time log viewer in the web dashboard that shows the internal thoughts and communications between agents.


Architecture and How It Works

The system is coordinated by a central Planner Orchestrator Agent that manages state transitions and communicates with four specialized sub-agents:

1. Planner Agent (Root Orchestrator): Manages overall state flow, handles errors, enforces safety rules, and routes requests to sub-agents.
2. Preference Agent: Extracts and validates user preferences such as interests, skill level, available hours per day, and duration.
3. Project Recommendation Agent: Generates tailored project blueprints with daily step-by-step tasks using Gemini structured outputs.
4. Memory Agent: Handles persistent storage, task completion tracking, project history, and long-term user profile summaries.
5. Progress & Reconfiguration Agent: Analyzes completion status when a user falls behind and reschedules remaining tasks within the existing timeframe.

![Multi-Agent Architecture Diagram](./assets/architecture_diagram.jpg)
![Dynamic Schedule Reconfiguration Flow](./assets/reconfiguration_flow.jpg)


Course Concepts Applied

This project demonstrates several key concepts covered in the AI Agents Intensive course:

- Multi-Agent Orchestration: A root orchestrator agent delegating work to four dedicated sub-agents.
- Structured Outputs (Pydantic Schemas): Enforcing strict JSON outputs for user preferences, project blueprints, daily tasks, and reconfigured schedules using the Gemini API.
- Persistent Memory & State Management: Storing state locally and using Gemini to maintain an evolving summary of user achievements.
- Safety Controls: Enforcing single-project constraints to prevent user burnout and validating API key configurations securely.


Setup and Running Locally

Prerequisites:
- Python 3.10 or higher
- A Gemini API Key from Google AI Studio

Installation Steps:

1. Clone the repository:
   git clone https://github.com/yourusername/concierge-planning-agent.git
   cd concierge-planning-agent

2. Create and activate a Python virtual environment:
   # On Windows:
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # On macOS/Linux:
   python -m venv .venv
   source .venv/bin/activate

3. Install the required dependencies:
   pip install -r requirements.txt

4. Create a .env file in the project root directory and add your API key:
   GEMINI_API_KEY=your_gemini_api_key_here

5. Run the verification test script:
   python verify_agents.py

6. Launch the Streamlit web dashboard:
   streamlit run app.py


Cloud Deployment (Google Cloud Run)

You can containerize and deploy this application to Google Cloud Run using the included Dockerfile:

1. Build and push the container image:
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/concierge-agent

2. Deploy to Cloud Run:
   gcloud run deploy concierge-agent \
     --image gcr.io/YOUR_PROJECT_ID/concierge-agent \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your_gemini_api_key_here


Project Structure

app.py                  - Main Streamlit web application dashboard
models.py               - Pydantic data schemas for structured agent outputs
verify_agents.py        - Automated backend verification test script
memory_store.json       - Local JSON database for persistent memory
requirements.txt        - Python package dependencies
.env.example            - Template for environment variables
Dockerfile              - Container specification for Cloud Run deployment
agents/                 - Multi-agent modules
  base.py               - Base agent class with Gemini API wrapper
  planner.py            - Root orchestrator agent
  preference.py         - Preference parser and validator agent
  recommendation.py     - Project recommendation and task generator agent
  memory.py             - Memory management and profile summary agent
  progress.py           - Progress analysis and schedule reconfiguration agent


Security

- API Keys: Keys are loaded strictly from the local .env file or entered directly in the UI sidebar session state. They are never committed to code repositories or printed in log files.
- Safety Checks: The system validates all user inputs and prevents starting multiple projects simultaneously to avoid user burnout.
