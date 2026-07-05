import os
import sys
from dotenv import load_dotenv

# Set sys.argv to mock streamlit run environment or mock imports
# Since streamlit uses session state, we mock streamlit session state for backend tests
class MockSessionState(dict):
    pass

import streamlit as st
if "agent_logs" not in st.__dict__:
    st.session_state = MockSessionState()
    st.session_state["agent_logs"] = []

from models import UserPreferences, ProjectProposal, DailyTask
from agents.planner import PlannerAgent
from agents.memory import MemoryAgent
from agents.preference import PreferenceAgent
from agents.recommendation import ProjectRecommendationAgent
from agents.progress import ProgressAgent

def run_tests():
    print("=== Starting Capstone Agent Verification ===")
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("\n1. Verifying Class Imports...")
    try:
        # Instantiate agents to verify imports and initialization
        memory = MemoryAgent()
        preference = PreferenceAgent()
        recommendation = ProjectRecommendationAgent()
        progress = ProgressAgent()
        planner = PlannerAgent()
        print("[SUCCESS] All Agent classes imported and instantiated successfully!")
    except Exception as e:
        print(f"[FAIL] Class import or instantiation failed: {str(e)}")
        sys.exit(1)

    print("\n2. Verifying Memory System Initialization...")
    try:
        # Check if memory database file is initialized
        if os.path.exists("memory_store.json"):
            print("[SUCCESS] 'memory_store.json' exists and was successfully initialized.")
            state = memory.load_state()
            print(f"   Current active project in memory: {state.get('active_project')}")
        else:
            print("[FAIL] Memory file 'memory_store.json' not found.")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Memory verification failed: {str(e)}")
        sys.exit(1)

    print("\n3. Verifying Gemini API Configuration...")
    if not api_key:
        print("[WARNING] GEMINI_API_KEY not found in environment (or .env).")
        print("   Skipping live API integration tests. Please configure GEMINI_API_KEY to run full tests.")
    else:
        print("[SUCCESS] GEMINI_API_KEY is present in environment.")
        print("\n4. Running Live LLM Integration Tests...")
        try:
            # Test Preference parsing via Preference Agent
            print("   [Test 4.1] Testing Preference Agent Parsing...")
            test_input = "I am interested in Rust programming and web servers. I can work 3 hours per day. I want a 3-day project. Skill level beginner."
            parsed_prefs = preference.parse_preferences(test_input)
            print(f"   [SUCCESS] Parsed Interests: {parsed_prefs.interests}")
            print(f"   [SUCCESS] Parsed Hours per Day: {parsed_prefs.hours_per_day}")
            print(f"   [SUCCESS] Parsed Duration: {parsed_prefs.target_duration_days} days")
            
            # Validate preferences
            is_valid, err = preference.validate_preferences(parsed_prefs)
            print(f"   [SUCCESS] Preference Validity: {is_valid} (Error: '{err}')")
            
            # Test Project Recommendation via Recommendation Agent
            print("\n   [Test 4.2] Testing Project Recommendation Agent...")
            proposal = recommendation.recommend_project(parsed_prefs)
            print(f"   [SUCCESS] Proposed Project Name: '{proposal.name}'")
            print(f"   [SUCCESS] Total Days: {proposal.total_days} days")
            print(f"   [SUCCESS] Milestone tasks generated: {len(proposal.daily_tasks)}")
            assert len(proposal.daily_tasks) == proposal.total_days, "Mismatch in days vs task count."
            
            # Test Reconfiguration via Progress Agent
            print("\n   [Test 4.3] Testing Progress/Reconfiguration Agent...")
            # Simulate user falling behind: mark Day 1 task complete, leave Day 2 and Day 3 tasks pending on Day 3
            proposal.daily_tasks[0].completed = True # Day 1 completed
            proposal.daily_tasks[1].completed = False # Day 2 pending
            proposal.daily_tasks[2].completed = False # Day 3 pending
            
            reconfig = progress.analyze_and_reconfigure(parsed_prefs, proposal, current_day=3)
            print(f"   [SUCCESS] Reconfiguration Justification: '{reconfig.justification[:80]}...'")
            print(f"   [SUCCESS] Revised tasks generated: {len(reconfig.revised_tasks)}")
            
            print("\n[SUCCESS] Live LLM Integration Tests Succeeded!")
        except Exception as e:
            print(f"[FAIL] Live LLM Integration Tests failed: {str(e)}")
            sys.exit(1)

    print("\n=== Verification Completed Successfully ===")

if __name__ == "__main__":
    run_tests()
