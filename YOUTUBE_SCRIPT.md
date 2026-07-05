# YouTube Submission Video Script 🎥🎙️
*(Target Duration: < 3 Minutes)*

This script helps you record the video submission for your Kaggle Capstone Project. It is divided into 5 clear segments matching the evaluation criteria.

---

## ⏱️ Timeline Overview
*   **0:00 - 0:30**: Problem Statement (The "Why")
*   **0:30 - 1:00**: Why Agents? (Concept & Value)
*   **1:00 - 1:30**: Agent Architecture (How it Works)
*   **1:30 - 2:30**: Live Demo (Walkthrough)
*   **2:30 - 3:00**: Technical Build & Outro

---

## 🎬 Section 1: The Problem (0:00 - 0:30)
**[Visual: Show your face or a title slide: "Concierge Planning Agent - Burnout Prevention Scheduler"]**

> "Hi everyone! In self-directed learning, we all face a major obstacle: **scope creep and planning burnout**. 
> 
> We try to learn Python, Rust, or Machine Learning, but we size our goals unrealistically, fall behind, get overwhelmed, and ultimately abandon the project. Standard static calendars don't know the difficulty of what we are doing, and they don't adapt when we struggle."

---

## 🧠 Section 2: Why Agents? (0:30 - 1:00)
**[Visual: Transition to the Streamlit App interface showing the main landing page]**

> "That's why I built the **Concierge Planning Agent**. 
> 
> Instead of a static calendar, this project uses a coordinated team of AI agents. Agents are uniquely suited here because planning is a negotiation:
> *   The **Preference Agent** parses your constraints.
> *   The **Recommendation Agent** acts as an advisor, designing custom roadmaps calibrated to your daily hours.
> *   And most importantly, the **Progress Agent** acts as a coach—detecting when you are behind and dynamically re-arranging your remaining goals to fit your actual pace without causing burnout."

---

## 🏗️ Section 3: Agent Architecture (1:00 - 1:30)
**[Visual: Show the Architecture Mermaid Diagram (from the README.md)]**

> "Here is our architecture:
> At the root, we have a **Planner Orchestrator Agent**. It directs the state machine. 
> When you enter preferences, it coordinates with the Preference and Recommendation sub-agents. 
> When you accept a project, the details are saved in the **Memory Agent**, which keeps a JSON database of completed milestones and builds a persistent summary of your strengths over time. 
> If you fall behind, the Planner invokes the **Progress Agent** to calculate a reconfigured schedule."

---

## 💻 Section 4: Live Demo (1:30 - 2:30)
**[Visual: Record your screen while interacting with the Streamlit app]**

> "Let's see it in action.
> 
> First, I will input my interests: *'Data Science and Streamlit'* and set my time availability to *2 hours a day* for *7 days*.
> 
> When I submit, the **Preference Agent** validates and parses the inputs. Now I ask the **Recommendation Agent** to generate a blueprint. 
> 
> Look at this beautiful 7-day blueprint, custom-sized for a 2-hour daily workload. If I decline, it runs again, checking my decline history to suggest a fresh project. 
> 
> Once I click **Accept**, the project starts and is locked into memory. The app enforces a strict safety check: **I cannot start another project while this is active**, preventing burnout.
> 
> Now, let's simulate falling behind. I am on Day 3, but I have only completed Day 1's tasks. I click **Reconfigure Deadlines**. Behind the scenes, the Progress Agent analyzes my completion rate and redistributes the pending tasks, restructuring the scope to fit my actual pace."

---

## 🛠️ Section 5: The Build & Outro (2:30 - 3:00)
**[Visual: Show the codebase structure or Dockerfile/verify_agents.py terminal run]**

> "I built this system in Python using the modern **Google GenAI SDK** powered by **Gemini 2.5 Flash**. 
> 
> Pydantic schemas enforce strict JSON schemas for agent communications. The front end is a glassmorphic Streamlit web dashboard featuring a live console showing agent thoughts in real-time.
> 
> The project includes a full Docker container setup, ready to deploy to Google Cloud Run.
> 
> Thank you! Build smarter, learn sustainably, and check out my GitHub repository below."
