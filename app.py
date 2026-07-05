import streamlit as st
import os
import time
from dotenv import load_dotenv
from agents.planner import PlannerAgent
from models import ProjectProposal, UserPreferences, DailyTask

# Page configuration
st.set_page_config(
    page_title="AI Agentic Project Planner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injects custom glassmorphism CSS
st.markdown("""
<style>
    /* Global Background and Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Glowing Title Gradient */
    .glowing-title {
        background: linear-gradient(90deg, #c084fc, #6366f1, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
        padding-top: 10px;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .glass-card-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
    }

    /* Console Terminal Look */
    .terminal-container {
        background-color: #090d16;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #10b981;
        max-height: 250px;
        overflow-y: auto;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }

    .terminal-line {
        margin-bottom: 6px;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    
    .terminal-agent {
        color: #38bdf8;
        font-weight: bold;
    }
    
    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse 1.6s infinite;
        vertical-align: middle;
        margin-right: 8px;
    }

    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }

    /* Custom Metrics */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# Helper: load environment at startup
load_dotenv()

# Initialize API key and Planner Agent in Session State
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = os.getenv("GEMINI_API_KEY", "")

if "agent_logs" not in st.session_state:
    st.session_state["agent_logs"] = ["[System] Multi-Agent System initialized. Awaiting API Key configuration."]

# Instantiate orchestrator
# We run the constructor, which doesn't query the LLM immediately (API client is lazy-loaded)
try:
    planner = PlannerAgent()
except Exception as e:
    st.error(f"Error initializing agents: {str(e)}")
    planner = None

# Sidebar Content
with st.sidebar:
    st.markdown("### 🤖 Agent Control Center")
    st.markdown("---")

    # API Key management
    env_key_found = bool(os.getenv("GEMINI_API_KEY"))
    if env_key_found:
        st.success("✅ Gemini Key loaded from `.env`")
    else:
        st.warning("⚠️ No Gemini Key found in `.env`")
        api_key_input = st.text_input(
            "Enter GEMINI_API_KEY:",
            value=st.session_state["gemini_api_key"],
            type="password",
            help="Get your key from https://aistudio.google.com/"
        )
        if api_key_input != st.session_state["gemini_api_key"]:
            st.session_state["gemini_api_key"] = api_key_input
            st.rerun()

    st.markdown("### 💾 Long-Term Memory Summary")
    if planner:
        state = planner.memory_agent.load_state()
        st.info(state.get("user_summary", "No history available yet."))
    else:
        st.text("Awaiting agent system setup...")

    st.markdown("---")
    if st.button("🧹 Clear Live Agent Logs", use_container_width=True):
        st.session_state["agent_logs"] = ["[System] Console logs cleared."]
        st.rerun()

# Title banner
st.markdown('<div class="glowing-title">Concierge Planning Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A multi-agent scheduler that aligns your learning goals, prevents burnout, and adapts to your pace.</div>', unsafe_allow_html=True)

# Safety check: ensure API key is available
api_configured = env_key_found or bool(st.session_state["gemini_api_key"])

if not api_configured:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <h3 style="color:#f43f5e;">API Key Configuration Required</h3>
        <p>Please enter your <strong>GEMINI_API_KEY</strong> in the sidebar settings or create a <code>.env</code> file in the project folder with <code>GEMINI_API_KEY=your_key</code>.</p>
        <p style="font-size:0.9rem; color:#94a3b8;">This capstone project relies on Gemini models to power the Orchestrator, Preference, Recommendation, Memory, and Progress agents.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Helper function to add a line to agent logs in UI
def add_ui_log(agent_name: str, message: str):
    st.session_state["agent_logs"].append(f"[{agent_name}] {message}")

# --- Load Main State Variables ---
active_project = planner.memory_agent.get_active_project() if planner else None
preferences = planner.memory_agent.get_preferences() if planner else None

# Check for temporary proposed project in session state
if "proposed_project" not in st.session_state:
    st.session_state["proposed_project"] = None

if "declined_projects" not in st.session_state:
    st.session_state["declined_projects"] = []

# Tabs layout
tab_dashboard, tab_plan, tab_history = st.tabs([
    "📊 Workspace Dashboard", 
    "🎯 Plan a New Project", 
    "📜 Project History"
])

# ==========================================
# TAB 1: WORKSPACE DASHBOARD (Active Project)
# ==========================================
with tab_dashboard:
    if active_project:
        # Title of the Project & Info
        st.markdown(f"""
        <div class="glass-card">
            <div class="glass-card-header">🚀 Active Project: {active_project.name}</div>
            <p style="font-size:1.1rem; color:#e2e8f0; margin-bottom:15px;">{active_project.description}</p>
            <div style="display: flex; gap: 40px; margin-top: 10px;">
                <div>
                    <div class="metric-label">Difficulty</div>
                    <div class="metric-value">{active_project.difficulty}</div>
                </div>
                <div>
                    <div class="metric-label">Total Duration</div>
                    <div class="metric-value">{active_project.total_days} Days</div>
                </div>
                <div>
                    <div class="metric-label">Daily Allocation</div>
                    <div class="metric-value">{preferences.hours_per_day if preferences else 'N/A'} Hours</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Progress calculation
        total_tasks = len(active_project.daily_tasks)
        completed_tasks = sum(1 for t in active_project.daily_tasks if t.completed)
        progress_percentage = (completed_tasks / total_tasks) if total_tasks > 0 else 0.0

        col_prog, col_status = st.columns([3, 1])
        with col_prog:
            st.markdown("### Progress Roadmap")
            st.progress(progress_percentage)
            st.caption(f"{completed_tasks} of {total_tasks} milestones completed ({int(progress_percentage * 100)}%)")
        
        with col_status:
            # Check if user is behind schedule
            # Simple heuristic: if any task prior to selected day is pending
            st.markdown("### Schedule Health")
            
            # Allow user to pick current execution day
            if "current_day_index" not in st.session_state:
                st.session_state["current_day_index"] = 1
                
            current_day = st.number_input("Current day of execution:", min_value=1, max_value=active_project.total_days, value=st.session_state["current_day_index"])
            st.session_state["current_day_index"] = current_day

            # Is the user behind?
            behind = False
            for t in active_project.daily_tasks:
                if t.day < current_day and not t.completed:
                    behind = True
                    break
            
            if behind:
                st.markdown("<span style='color:#f43f5e; font-weight:bold; font-size:1.2rem;'>⚠️ BEHIND SCHEDULE</span>", unsafe_allow_html=True)
                st.caption("You have uncompleted tasks from prior days.")
            else:
                st.markdown("<span style='color:#10b981; font-weight:bold; font-size:1.2rem;'>✅ ON TRACK</span>", unsafe_allow_html=True)
                st.caption("All historical goals completed!")

        # Task checklist layout
        st.markdown("### Task Roadmap Checklist")
        st.markdown("Check off tasks as you complete them. The system auto-updates memory.")
        
        tasks_by_day = {}
        for task in active_project.daily_tasks:
            tasks_by_day.setdefault(task.day, []).append(task)
            
        for day in sorted(tasks_by_day.keys()):
            # Highlight current day in a card, others in simple expanders
            is_current = (day == current_day)
            day_title = f"Day {day} Goal" + (" (TODAY'S TASK)" if is_current else "")
            
            with st.expander(day_title, expanded=is_current):
                for task in tasks_by_day[day]:
                    checkbox_key = f"task_{day}_{task.title}"
                    checked = st.checkbox(
                        f"**{task.title}** ({task.estimated_hours} hours) - *{task.description}*",
                        value=task.completed,
                        key=checkbox_key
                    )
                    # If state changed, update memory
                    if checked != task.completed:
                        planner.memory_agent.update_task_completion(day, task.title, checked)
                        st.rerun()

        # Reconfiguration & Abandon actions
        st.markdown("---")
        col_actions_1, col_actions_2 = st.columns([1, 1])
        
        with col_actions_1:
            st.markdown("#### Schedule Adjuster")
            st.markdown("Falling behind? Get the Progress Agent to review your completion rate and re-budget your remaining tasks dynamically.")
            if st.button("🔄 Reconfigure Remaining Deadlines", use_container_width=True):
                with st.spinner("Progress Agent is re-arranging the schedule..."):
                    reconfigured, error = planner.reconfigure_schedule(current_day)
                    if error:
                        st.error(error)
                    else:
                        st.success("Deadlines reconfigured successfully!")
                        st.info(f"Justification: {reconfigured.justification}")
                        time.sleep(2)
                        st.rerun()
                        
        with col_actions_2:
            st.markdown("#### Danger Zone")
            st.markdown("If this project is too difficult or no longer interesting, you can abandon it. Enforces the single active project safety rule.")
            
            abandon_confirm = st.checkbox("Check this box to confirm you want to abandon the project.")
            if st.button("🚨 Abandon Project & Start Fresh", type="primary", disabled=not abandon_confirm, use_container_width=True):
                success, msg = planner.abandon_project("User requested project abandonment.")
                if success:
                    st.success(msg)
                    st.session_state["proposed_project"] = None
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(msg)
                    
        # Check if project complete
        if completed_tasks == total_tasks and total_tasks > 0:
            st.balloons()
            st.markdown("""
            <div class="glass-card" style="text-align: center; border-color: #10b981;">
                <h3 style="color:#10b981;">🎉 Project Fully Completed!</h3>
                <p>Congratulations! You have completed all daily goals for this project.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Complete Project & Archive to Memory", use_container_width=True):
                success, msg = planner.complete_project()
                if success:
                    st.success(msg)
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(msg)

    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 40px 20px;">
            <h3>No Active Project</h3>
            <p style="color:#94a3b8;">You do not have any active project in progress. To start planning your roadmap, configure your preferences in the next tab.</p>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# TAB 2: PLAN A NEW PROJECT
# ==========================================
with tab_plan:
    if active_project:
        st.warning("⚠️ You are already working on an active project. Single-project limits are enforced to prevent burnout. You must complete or abandon your active project before planning a new one.")
        st.stop()

    st.markdown("### Configure Project Preferences")
    st.markdown("Tell the Preference Agent what you want to learn, how much time you have, and your background level.")

    # Show preferences if already saved in memory to prepopulate
    default_interests = ", ".join(preferences.interests) if preferences else "Python, Machine Learning, Web Scraping"
    default_hours = preferences.hours_per_day if preferences else 2.0
    default_skill = preferences.skill_level if preferences else "Intermediate"
    default_days = preferences.target_duration_days if preferences else 7

    # Preference Capture Form
    with st.form("preference_form"):
        interests_input = st.text_input("What topics, technologies, or skills are you interested in?", value=default_interests)
        
        col_form_1, col_form_2, col_form_3 = st.columns([1, 1, 1])
        with col_form_1:
            hours_input = st.slider("Time available (hours per day):", min_value=0.5, max_value=8.0, value=default_hours, step=0.5)
        with col_form_2:
            skill_input = st.selectbox("Your experience level:", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(default_skill))
        with col_form_3:
            duration_input = st.number_input("Project Duration (days):", min_value=1, max_value=60, value=default_days)

        submit_pref = st.form_submit_button("Submit Preferences to Preference Agent")

    if submit_pref:
        with st.spinner("Preference Agent is validating and structured parsing..."):
            raw_pref_str = f"Interests: {interests_input}. Time available: {hours_input} hours per day. Experience level: {skill_input}. Project duration: {duration_input} days."
            success, msg = planner.process_preferences(raw_pref_str)
            if success:
                st.success(msg)
                # Clear past proposed project to trigger a clean regeneration
                st.session_state["proposed_project"] = None
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)

    # Project recommendation display
    if preferences:
        st.markdown("---")
        st.markdown("### Generate Project Proposal")
        st.markdown("Ready? Ask the Project Recommendation Agent to design a customized project blueprint based on your preferences.")
        
        # Recommendation triggers
        col_rec_1, col_rec_2 = st.columns([1, 1])
        with col_rec_1:
            if st.button("✨ Generate Project Recommendation", use_container_width=True):
                with st.spinner("Project Recommendation Agent is designing your project..."):
                    proposal, error = planner.get_recommendation(st.session_state["declined_projects"])
                    if error:
                        st.error(error)
                    else:
                        st.session_state["proposed_project"] = proposal
                        st.success(f"Proposal '{proposal.name}' generated!")
                        
        with col_rec_2:
            if st.button("Reset Declined History", use_container_width=True):
                st.session_state["declined_projects"] = []
                st.success("Declined history reset. Recommendation Agent can suggest past projects again.")

        # Show Proposal if available
        proposed = st.session_state["proposed_project"]
        if proposed:
            st.markdown("---")
            st.markdown(f"""
            <div class="glass-card" style="border-color: #818cf8;">
                <div class="glass-card-header">📋 Proposed Blueprint: {proposed.name}</div>
                <p style="font-size:1.1rem; color:#e2e8f0;">{proposed.description}</p>
                <p><strong>Difficulty Level:</strong> {proposed.difficulty} | <strong>Total Duration:</strong> {proposed.total_days} Days</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show proposed task roadmap
            st.markdown("#### Proposed Daily Milestones")
            for task in proposed.daily_tasks:
                st.markdown(f"- **Day {task.day}**: {task.title} ({task.estimated_hours}h) - *{task.description}*")
                
            # Accept / Decline options
            st.markdown("---")
            col_acc, col_dec, col_ex = st.columns([1, 1, 1])
            with col_acc:
                if st.button("✅ Accept Proposal & Start Project", type="primary", use_container_width=True):
                    success, msg = planner.accept_project(proposed)
                    if success:
                        st.success(msg)
                        st.session_state["proposed_project"] = None
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(msg)
            with col_dec:
                if st.button("❌ Decline (Recommend Another)", use_container_width=True):
                    st.session_state["declined_projects"].append(proposed.name)
                    st.session_state["proposed_project"] = None
                    st.warning(f"Declined '{proposed.name}'. Requesting a new project recommendation...")
                    with st.spinner("Generating alternative recommendation..."):
                        proposal, error = planner.get_recommendation(st.session_state["declined_projects"])
                        if error:
                            st.error(error)
                        else:
                            st.session_state["proposed_project"] = proposal
                            st.success(f"New proposal '{proposal.name}' generated!")
                            time.sleep(1)
                            st.rerun()
            with col_ex:
                if st.button("🚪 Exit Planning", use_container_width=True):
                    st.session_state["proposed_project"] = None
                    st.rerun()

# ==========================================
# TAB 3: PROJECT HISTORY
# ==========================================
with tab_history:
    st.markdown("### Completed and Abandoned Projects")
    st.markdown("Here is the record of your past projects saved in the Memory Agent.")
    
    if planner:
        state = planner.memory_agent.load_state()
        history = state.get("project_history", [])
        
        if not history:
            st.info("No project history in memory yet. Complete or abandon a project to see history here.")
        else:
            for idx, proj in enumerate(reversed(history)):
                status = proj.get("status", "Unknown")
                color = "#10b981" if status == "Completed" else "#f43f5e"
                
                with st.expander(f"{proj.get('name')} - {status}", expanded=False):
                    st.markdown(f"**Description**: {proj.get('description')}")
                    st.markdown(f"**Difficulty**: {proj.get('difficulty')} | **Total Days**: {proj.get('total_days')}")
                    st.markdown(f"**Status**: <span style='color:{color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
                    if status == "Abandoned":
                        st.markdown(f"**Reason for Abandonment**: *{proj.get('abandon_reason', 'Not specified')}*")
                        
                    # Calculate completed tasks
                    tasks = proj.get("daily_tasks", [])
                    comp_tasks = sum(1 for t in tasks if t.get("completed"))
                    st.markdown(f"**Milestone Completion**: {comp_tasks} of {len(tasks)} tasks completed.")

# ==========================================
# LIVE AGENT LOG CONSOLE
# ==========================================
st.markdown("---")
st.markdown("""
<h3>
    <div class="pulse-dot"></div> Live Agent Communication Log
</h3>
""", unsafe_allow_html=True)
st.markdown("Watch how the sub-agents and the main Orchestrator communicate behind the scenes:")

# Render logs in terminal format
log_html = '<div class="terminal-container">'
for log in st.session_state["agent_logs"]:
    # Format Agent tags with blue color, text with green
    if "[" in log and "]" in log:
        tag_end = log.find("]") + 1
        agent_tag = log[:tag_end]
        message_text = log[tag_end:]
        log_html += f'<div class="terminal-line"><span class="terminal-agent">{agent_tag}</span>{message_text}</div>'
    else:
        log_html += f'<div class="terminal-line">{log}</div>'
log_html += '</div>'

st.markdown(log_html, unsafe_allow_html=True)
