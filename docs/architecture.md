Healthcare Prevention Agent
Architecture & Phase 1 Documentation
Mahak Haddadi

Purpose
This agent collects information about a user's health condition and wellbeing, builds a structured health profile, then provides suggestions and prevention tips to help them stay healthy and reduce the risk of future illness.
Architecture — Layers
Interaction / Perception Layer
Receives the user's messages, manages the conversation, and guides the user through the information-collection process. Converts raw user input into structured information and updates the user's profile.
•	Receive user input
•	Extract health-related information
•	Ask follow-up questions to complete the profile
•	Handle profile corrections and updates
•	Communicate with the memory layer to access the current user profile
Memory Layer
Holds the user's data across the conversation and across sessions.
•	Working memory: information collected during the current session
•	Persistent memory: the saved profile + full conversation history from past sessions
Provides context to other components and allows the agent to maintain continuity across interactions.
Completeness Checker
Compares the current profile against a fixed, predefined list of required fields (age, weight, height, last checkup, etc.) and reports what's missing. This check is deterministic — a checklist comparison, not an LLM judgment call — so behavior is identical regardless of phrasing.
If information is missing, control returns to the Interaction layer so additional questions can be asked.
Plan & Replan
Creates an execution plan based on the user's profile. Instead of immediately generating recommendations, the agent first determines which analyses should be performed. Runs as a bounded loop (5–20 iterations) rather than an open-ended one.
•	Create assessment plans
•	Update plans when new information is received
•	Determine the next actions required


Tool Selection Layer
Selects the most appropriate resource(s) required to execute the approved plan, before retrieval runs.
•	User profile data
•	External search sources
•	Database / RAG system (Phase 2)
Decision Layer (Prompt Chaining + Micro-Decisions)
The reasoning component of the agent. Rather than reasoning about the whole profile at once, every process the agent executes is broken down into individual micro-decisions — one per health category. Each micro-decision uses prompt chaining and returns a structured, self-scored result: a finding, a confidence score, and a risk level.
Input: the user's profile, segmented into category-specific views.
Output: one structured finding per category, later merged into a single draft by the Combine step.
Standard segmentation used for micro-decisions:
•	Weight status (BMI, weight trend)
•	Cardiovascular risk (blood pressure indicators, heart-related family history)
•	Metabolic risk (blood sugar / diabetes indicators, liver-related factors)
•	Lifestyle & behavioral (exercise, smoking, alcohol, sleep)
•	Nutrition (general diet pattern)
•	Preventive care engagement (checkup history, screening compliance)
The output is considered a draft recommendation and is not shown directly to the user until it passes Confidence Routing and the Rule Engine.
Confidence Routing
A deterministic check — not an LLM call — that evaluates each micro-decision's confidence and risk level against fixed thresholds, and decides whether that category is safe to include in the draft answer or must be escalated to a human before anything is shown to the user.
Routing logic (illustrative):
•	If confidence < 0.5 → escalate
•	If risk level = high and confidence < 0.75 → escalate
•	If risk level = high and the category is sensitive (e.g. cardiac, BP) → escalate regardless of confidence
Escalated categories are pulled out before the Combine step runs, so a low-confidence finding never reaches the user unmediated. Confidence is shown to the user per suggestion in the final output, not as a single blended score for the whole response — see "Confidence Display" below.
Supervisor
Acts as a control and validation layer for the generated plan. The supervisor reviews the plan before execution and ensures the plan is complete, appropriate tools were selected, and high-risk situations are detected. If problems are found, the plan is sent back to the Plan & Replan layer for revision.
•	Validate plans
•	Detect missing analysis steps
•	Identify high-risk situations
•	Trigger replanning when necessary
In Phase 1 (no analysis yet), the Supervisor's scope is limited to the completeness gate and generating the message the user reads — its full validation/escalation role activates in Phase 2.
Rule Engine
Applies predefined deterministic rules independently from the LLM, to ensure safety, consistency, and policy compliance. Same input always produces the same rule outcome.
A deterministic decision from this layer typically does one of: gate/block an answer, escalate/route to a human, inject a required fact into the output, or tag/classify risk.
Examples: missing critical information, extremely high blood pressure, high-risk conditions requiring medical attention.
•	Apply deterministic rules
•	Enforce safety constraints
•	Handle escalation scenarios
Output Layer
Generates the final response shown to the user.
•	Prevention recommendations
•	Lifestyle suggestions
•	Potential risk factors
•	References to the specific profile data used in the assessment
•	A confidence label attached to each individual suggestion (see "Confidence Display")
Audit Trail
Maintains a timestamped record of important system decisions and actions across every layer that makes a decision or changes data — not a single step in the pipeline, but a layer every stage writes into continuously.
•	Profile completeness checks
•	Planning and replanning decisions
•	Supervisor interventions
•	Triggered rules
•	Confidence-routing escalations
•	Final recommendations delivered to the user
This improves transparency, traceability, and explainability — and is the evidence trail for liability protection and regulatory compliance.
Layer Connections
How each layer connects to the next: what data crosses, and what triggers the handoff.
From → To	What crosses	Trigger
User → Interaction layer	Raw message	Every user turn
Interaction ↔ Memory	Read current profile / write new fields	Every message
Completeness checker → Interaction	List of missing fields	Loop-back, when incomplete
Completeness checker → Tool Selection	"Profile complete" signal	Gate — only when complete
Tool Selection → Retrieval	Chosen source(s) + query	Per plan step
Decision layer → Tool Selection	"Need more information"	Loop-back (Plan & Replan, capped 5–20)
Decision layer → Confidence routing	Finding + confidence + risk per category	After each micro-decision
Confidence routing → Escalation	Flagged category	Conditional
Combine → Rule Engine	Merged draft object	Once per cycle
Rule Engine → Output	Approved / modified / blocked content	After rule check
All layers → Audit Trail	Decision + reasoning, timestamped	Continuous, one-way
Clinical Guidelines Integration (WHO / CDC)
Guidelines are never scraped live at runtime — this would be unreliable and impossible to version-control for audit purposes. Instead, they enter the system through two separate, curated, offline paths:
Rule Engine path: a person reads the guideline and manually encodes the threshold as a fixed rule (e.g. WHO's BMI ≥ 25 = overweight definition becomes a hard-coded rule). Reviewed and updated periodically, not generated automatically by the agent.
RAG path: guideline documents are chunked, embedded, and stored with source/version metadata in a retrieval database, so the Decision layer can ground its explanations in the actual guideline text and cite it — rather than paraphrasing from model training data.
The Rule Engine decides what the finding is (the hard threshold); RAG explains why (the supporting text). Both are kept in sync deliberately — when a guideline updates, both the rule and its corresponding RAG chunk are reviewed together.
Special Scenarios & Error Handling
Every one of the four scenarios below is logged to the Audit Trail, and the user always receives a clear message — never a silent failure, never a confident-sounding guess standing in for genuine uncertainty.
Scenario	Detecting layer	Response
Missing information	Completeness checker	Loop back to the Interaction layer; ask for the next missing field. Not an error — expected, normal flow.
High-risk situation / low confidence	Confidence routing	Blocks that category from the draft answer and routes it for human review before Combine runs.
System error (API/tool failure)	Tool Selection / Retrieval	Retry once, then a clear error message. Never proceeds silently with incomplete or stale data.
Escalation to doctor / specialist	Rule Engine (guideline-derived hard rule)	Hard stop — no partial suggestion, only an explicit referral message.
Confidence Display in the Final Output
Rather than one blended confidence score for the whole response, each suggestion in the final output carries its own visible confidence label, matching how the decision was actually made — per category, not globally. A suggestion drawn from a well-supported, high-confidence finding is labeled accordingly; a category that was escalated is shown as "flagged for professional review" rather than answered with a guess.
Task 2 — Information Needed From the User
Core biometric
•	Demographic characteristics: age and gender
•	Physical health: weight and height (BMI), blood pressure, cholesterol levels
Lifestyle / behavioral
•	Exercise, eating habits, smoking status
•	Sleep and diet (general pattern is enough for Phase 1)
Medical history
•	Existing diagnosed or previous health conditions
•	Current medications
•	Family history of major conditions
•	Allergies
Care engagement
•	Last checkup date
•	Last checkup result, if available
•	Whether they see a doctor regularly / have a primary care provider
Task 3 — Information Stored by the Agent
•	User demographic information (age, gender)
•	Physical health measurements (height, weight, blood pressure, cholesterol)
•	Lifestyle information (exercise, smoking, diet, sleep)
•	Medical history
•	Full conversation history and profile, persisted per session (Phase 1 implementation)

 
Phase 1 — Intake Agent
The goal of Phase 1 is to build a conversational healthcare intake agent capable of collecting a user's health information through natural dialogue and constructing a structured health profile. At this stage, the agent focuses only on gathering information; health analysis, risk assessment, retrieval, and personalized medical recommendations are intentionally postponed until Phase 2.
User Interface
The chat interface is implemented using Chainlit, providing a simple conversational environment for interacting with the agent. When a new conversation begins, the user first selects their preferred language (English or Persian). The remainder of the conversation is then conducted entirely in the selected language to provide a more natural user experience.
The interface also supports resuming previous conversations by loading the user's saved state from local storage.
Interaction Layer
The interaction layer receives every user message and sends the conversation history to the LLM using a structured extraction prompt. Rather than generating free-text responses, the model extracts only structured health information defined by the application's schema.
The extraction prompt is designed to:
•	support both English and Persian conversations, 
•	use the entire conversation history instead of only the latest message, 
•	avoid guessing missing information, 
•	recognize different ways users express the same information (e.g., "none", "nothing", or "هیچ"), 
•	correctly interpret medications, supplements, and vitamins, 
•	extract the user's first name when provided, 
•	return only structured fields defined by the Pydantic model. 
The extracted information is then merged into the user's health profile.
Completeness Checker
The completeness checker verifies whether all required health fields have been collected. Each required field is inspected individually, and any missing fields are stored in a list.
If the list is empty, the user's health profile is considered complete. Otherwise, the conversation continues until every required field has been collected.
This approach prevents the agent from skipping important information while still allowing users to answer multiple questions in a single message.
Plan & Replan
The planner determines which missing field should be requested next.
Instead of presenting the user with a long questionnaire, the conversation follows a hybrid approach:
•	The initial welcome message encourages users to provide as much information as they wish in a single response. 
•	After processing that response, the planner identifies only the remaining missing information. 
•	Subsequent questions are asked one at a time, making the conversation more natural while ensuring that no required information is overlooked. 
If the user later corrects or updates previously supplied information, the planner automatically adjusts the conversation flow.
Supervisor / Response Generation
The supervisor is responsible for generating every message shown to the user.
A dedicated conversation prompt controls the assistant's behavior and ensures that it:
•	always responds in the language selected by the user, 
•	asks exactly one follow-up question at a time, 
•	maintains a warm, friendly, and professional tone, 
•	avoids sounding like a medical questionnaire, 
•	briefly explains why information is requested when appropriate, 
•	generates a final completion message once the health profile is complete. 
Since this layer is the only component directly interacting with users, prompt engineering focused heavily on making conversations feel natural rather than robotic.
State Management
The application state is defined using Pydantic models and a TypedDict.
The HealthProfile model stores all collected health information, while ExtractedInfo defines the structured schema returned by the LLM during information extraction.
The application state also stores:
•	conversation history, 
•	current health profile, 
•	missing required fields, 
•	next field to request, 
•	conversation language, 
•	completion status, 
•	generated follow-up questions. 
This centralized state allows every layer of the LangGraph workflow to access and update the same information consistently.
Local Storage
During Phase 1, user information is stored locally as JSON files.
Each conversation state—including messages, extracted profile information, language preference, completion status, and planner state—is serialized into JSON and can be restored when the user returns.
This lightweight storage mechanism is sufficient for development and testing. In Phase 2, it will be replaced by a database to support persistent user accounts, scalable storage, and more advanced retrieval capabilities.

LangGraph Workflow
The overall workflow is orchestrated using LangGraph.
Each architectural layer is implemented as an independent node inside nodes.py, including:
•	Interaction 
•	Completeness Checker 
•	Planner 
•	Question Generator 
•	Final Response 
The graph controls the execution order of these nodes and determines whether the conversation should continue collecting information or finish once the profile is complete.
This modular design makes it easier to extend the system in future phases by adding new nodes for retrieval, reasoning, recommendation generation, and clinical decision support without modifying the existing workflow.



Prompt Engineering
Several dedicated prompts were developed to control different parts of the conversation:
•	bilingual welcome messages, 
•	conversation resume messages, 
•	profile completion messages, 
•	hybrid intake instructions, 
•	structured information extraction prompt, 
•	conversational tone and response-generation prompt. 
Special attention was given to multilingual support, ensuring the assistant consistently maintains the language chosen by the user throughout the entire interaction.
Project Structure
The implementation is organized into several modules:
•	app.py — Chainlit application and user interface. 
•	graph.py — LangGraph workflow definition and node routing. 
•	nodes.py — implementation of each architectural layer as individual functions. 
•	state.py — Pydantic models, state definitions, and required profile fields. 
•	prompts.py — all system prompts, welcome messages, and multilingual conversation templates. 
•	storage.py — JSON-based persistence for saving and restoring user sessions. 
•	config.py — LLM configuration and API initialization. 
Technologies Used
•	Python 
•	LangGraph (workflow orchestration) 
•	Chainlit (chat interface) 
•	Groq API / Gemini API (Large Language Models) 
•	Pydantic (structured data models) 
•	JSON (temporary local storage) 

Challenges
Several challenges were encountered during Phase 1.
The primary challenge was reliable access to LLM APIs. Due to regional network restrictions and API availability limitations, both Groq and Gemini occasionally returned authorization or connectivity errors, requiring experimentation with different providers and network configurations during development.
Another challenge was prompt engineering. Considerable effort was spent refining prompts so the assistant could correctly understand both Persian and English inputs, preserve the selected language throughout the conversation, recognize negative responses such as "none" or "هیچ", and maintain a conversational tone instead of behaving like a rigid medical form.
Additional work was also required to ensure that missing information was accurately identified while still allowing users to provide multiple health details in a single message, resulting in the hybrid intake strategy adopted in this phase.

