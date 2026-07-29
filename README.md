# Healthcare Prevention Agent

A conversational AI agent (built with LangGraph + Chainlit) that collects a user's health profile through natural, low-pressure dialogue and will provide personalized prevention suggestions in later phases.

## Phase 1 — Intake Agent

The main goal of this phase is to create a UI platform for the user to communicate with the agent and build a complete health profile through conversation. The first four layers of the architecture are implemented here:

- **Interaction layer** — receives the user's message, detects whether it's in English or Persian, extracts relevant health information, and updates the user's profile accordingly.
- **Completeness checker** — verifies whether the user's profile is complete by checking each required field against the profile. Missing fields are collected into an array; if the array is non-empty, the profile is considered incomplete.
- **Plan & Replan** — creates a strategy for the conversation. If fields are missing, it plans which ones to ask about next. If the user updates previously given information, the plan adjusts accordingly.
- **Supervisor** — validates the planner's output (e.g. confirms a field the planner wants to ask about is actually missing) and generates the message the user actually reads. Since this is the only layer whose output reaches the user directly, its tone is deliberately kept warm and low-pressure, so the user feels comfortable sharing sensitive health information rather than pressured to answer.

Analysis, retrieval (RAG), and clinical suggestions are not part of Phase 1 — this phase focuses entirely on building an accurate, complete profile through a comfortable conversational experience.

## Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — orchestrates the agent's layers as a graph of nodes and edges
- **[Chainlit](https://github.com/Chainlit/chainlit)** — provides the chat UI
- **Groq API** — LLM provider
- **Pydantic** — structured data models for the health profile and extraction

## Project Structure

```
HealthCareAgent/
├── app.py              # Chainlit entry point
├── main.py             # CLI test entry point
├── config.py              # LLM and environment configuration
├── graph.py               # LangGraph graph construction
├── nodes.py                # Individual layer implementations (interaction, completeness_checker, planner, supervisor)
├── prompts.py              # System prompts (tone, extraction)
├── state.py               # HealthProfile, HealthState, ExtractedInfo models
├── storage.py            # Profile and conversation persistence
├── docs/
│   └── architecture.md   # Full architecture diagrams and design notes
└── user_data/            # Saved user profiles (gitignored — not tracked)
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/MahakHaddadi-03/healthcare-prevention-agent.git
   cd healthcare-prevention-agent
   ```

2. Create and activate a virtual environment (Python 3.12 recommended):
   ```bash
   py -3.12 -m venv venv
   .\venv\Scripts\Activate.ps1   # Windows PowerShell
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Running the Agent

**Chat UI (Chainlit):**
```bash
python -m chainlit run app.py -w
```
Opens at `http://localhost:8000`.

**CLI test mode:**
```bash
python main.py
```

## Status

🚧 Phase 1 in progress — intake, completeness checking, and profile persistence are functional. Clinical analysis, RAG-based retrieval, and rule-engine-based suggestions are planned for Phase 2.

## Documentation

See [`docs/architecture.md`](docs/architecture.md) for full architecture diagrams, layer-by-layer design notes, and the roadmap for future phases (RAG, MCP, confidence routing, guideline integration).
