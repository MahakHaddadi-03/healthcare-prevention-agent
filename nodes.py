from config import llm
from prompts import EXTRACTION_PROMPT
from prompts import TONE_SYSTEM_PROMPT
from state import ExtractedInfo, HealthState
from state import required_fields

def interaction(state: HealthState):

    extractor = llm.with_structured_output(ExtractedInfo)

    result = extractor.invoke([
        {
            "role": "system",
            "content": EXTRACTION_PROMPT,
        },
        *state["messages"],
    ])

    for key, value in result.model_dump().items():
        if value is not None:
            setattr(state["profile"], key, value)

    return state


def completeness_checker(state: HealthState):

    profile = state["profile"]

    missing = []

    for field in required_fields:

        value = getattr(profile, field)

        if value is None:
            missing.append(field)

    state["missing_fields"] = missing

    state["completed"] = len(missing) == 0

    return state

def planner(state: HealthState):

    if state["completed"]:
        state["next_field"] = None
    else:
        state["next_field"] = state["missing_fields"][0]

    return state

def question_generator(state: HealthState):

    language = state["language"]
    next_field = state["next_field"]

    response = llm.invoke([
        {
            "role": "system",
            "content": TONE_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
Language: {language}

Ask about ONLY this field:

{next_field}

Requirements:

- Reply only in {language}.
- Ask exactly one question.
- Sound warm and conversational.
- Do not mention any other fields.
- If appropriate, briefly explain why this information is helpful.
""",
        },
    ])

    reply = response.content

    state["follow_up_question"] = reply

    state["messages"].append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    return state


def final_response(state: HealthState):

    language = state["language"]

    response = llm.invoke([
        {
            "role": "system",
            "content": TONE_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
Language: {language}

The user's profile is complete.

Reply only in {language}.

Write a short thank-you message.

Tell them:

- Their health profile is complete.
- Personalized recommendations will be available in a future version.

Do not ask another question.
""",
        },
    ])

    reply = response.content

    state["messages"].append(
        {
            "role": "assistant",
            "content": reply,
        }
    )

    return state

def route_after_checker(state: HealthState):

    if state["completed"]:
        return "final_response"

    return "planner"