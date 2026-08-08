from config import llm
from pydantic import BaseModel, Field
from typing import Literal
from database import save_risk_assessment
from prompts import (
    EXTRACTION_PROMPT,
    TONE_SYSTEM_PROMPT,
    MICRO_DECISION_PROMPT
)

from state import (
    ExtractedInfo,
    HealthState,
    required_fields
)



def interaction(state: HealthState):

    extractor = llm.with_structured_output(ExtractedInfo)

    result = extractor.invoke([
        {
            "role":"system",
            "content":EXTRACTION_PROMPT
        },
        *state["messages"]
    ])

    extracted = result.model_dump()

    profile = state["profile"]

    for key,value in extracted.items():

        if value is not None:
            setattr(profile,key,value)

    state["profile"]=profile

    return state
def normalize_profile(state: HealthState):

    p = state["profile"]

    if p.gender:

        gender = str(p.gender).lower()

        female = [
            "female",
            "woman",
            "lady",
            "girl",
            "زن",
            "خانم",
            "مونث"
        ]

        male = [
            "male",
            "man",
            "boy",
            "مرد",
            "آقا",
            "پسر"
        ]

        if gender in female:
            p.gender="female"

        elif gender in male:
            p.gender="male"

    if p.family_history:

        txt=p.family_history.lower()

        if txt in [
            "none",
            "no",
            "ندارم",
            "هیچ",
            "خیر"
        ]:
            p.family_history="none"

    state["profile"]=p

    return state

CATEGORY_FIELDS = {
    "weight_status": ["height", "weight"],
    "cardiovascular_risk": ["blood_pressure", "heart_disease", "family_history"],
    "metabolic_risk": ["diabetes", "family_history"],
    "lifestyle": ["exercise", "smoking", "diet"],
    "nutrition": ["diet"],
    "preventive_care": ["last_checkup"] 
}


def completeness_checker(state: HealthState):

    profile = state["profile"]

    missing = []


    for field in required_fields:

        value = getattr(
            profile,
            field
        )

        # None = user has not answered
        # [] = user answered none
        if value is None:

            missing.append(field)



    state["missing_fields"] = missing


    state["completed"] = (
        len(missing) == 0
    )


    return state



def planner(state: HealthState):


    if state["completed"]:

        state["next_field"] = None


    else:

        state["next_field"] = (
            state["missing_fields"][:3]
        )


    return state


def supervisor(state):
    last_user_message = state["messages"][-1]["content"] if state["messages"] else ""

    if state["completed"]:
        closing = llm.invoke([
            {"role": "system", "content": TONE_SYSTEM_PROMPT},
            {"role": "user", "content": f"The user's last message was: \"{last_user_message}\". Their profile is now complete. Write a short, warm message in the same language, letting them know you'll now look over their information."}
        ])
        reply = closing.content
    else:
        next_field = state["missing_fields"][0]
        question = llm.invoke([
            {"role": "system", "content": TONE_SYSTEM_PROMPT},
            {"role": "user", "content": f"The user's last message was: \"{last_user_message}\". Ask them for their {next_field.replace('_', ' ')}, gently, in the same language."}
        ])
        reply = question.content

    state["messages"].append({"role": "assistant", "content": reply})
    return state



def question_generator(state: HealthState):


    language = state["language"]

    missing_fields = state["next_field"]



    field_names = {

        "name": {
            "en": "your name",
            "fa": "نام"
        },

        "age": {
            "en": "your age",
            "fa": "سن"
        },

        "gender": {
            "en": "your gender",
            "fa": "جنسیت"
        },

        "height": {
            "en": "your height",
            "fa": "قد"
        },

        "weight": {
            "en": "your weight",
            "fa": "وزن"
        },

        "medications": {
            "en": "your medications or supplements",
            "fa": "داروها یا مکمل‌ها"
        },

        "allergies": {
            "en": "your allergies",
            "fa": "آلرژی‌ها"
        },

        "family_history": {
            "en": "your family medical history",
            "fa": "سابقه بیماری‌های خانوادگی"
        },

        "exercise": {
            "en": "your exercise habits",
            "fa": "فعالیت ورزشی"
        },

        "smoking": {
            "en": "your smoking status",
            "fa": "مصرف سیگار"
        },

        "diet": {
            "en": "your diet habits",
            "fa": "رژیم غذایی"
        }
    }



    topics = []


    for field in missing_fields:

        topics.append(
            field_names[field][language]
        )


    topic_text = ", ".join(topics)



    response = llm.invoke(
        [

            {
                "role": "system",
                "content": TONE_SYSTEM_PROMPT,
            },


            {
                "role": "user",

                "content": f"""
Language: {language}


The following health information is missing:

{topic_text}


Ask the user to provide these missing details together in one message.


Rules:

- Ask about all listed topics.
- Do not ask about information already provided.
- Do not ask one topic only.
- Be warm and conversational.
- Reply only in {language}.
- Keep it short.
"""
            }

        ]
    )



    reply = response.content



    state["follow_up_question"] = reply



    state["messages"].append(
        {
            "role": "assistant",
            "content": reply
        }
    )



    return state






def final_response(state: HealthState):


    language = state["language"]



    response = llm.invoke(
        [

            {
                "role": "system",
                "content": TONE_SYSTEM_PROMPT
            },


            {
                "role": "user",

                "content": f"""
Language: {language}


The health profile is complete.


Write a short final message.


Include:

- Thank the user.
- Confirm the health profile is complete.
- Mention personalized recommendations will be available in future versions.


Do not ask questions.
"""
            }

        ]
    )



    state["messages"].append(
        {
            "role": "assistant",
            "content": response.content
        }
    )


    return state


def route_after_checker(state: HealthState):


    if state["completed"]:

        return "final_response"


    return "planner"


def confidence_router(state: HealthState):
    passed = []
    escalated = []

    for d in state["micro_decisions"]:
        if d["confidence"] < 0.5:
            escalated.append(d)
        elif d["risk_level"] == "high" and d["confidence"] < 0.75:
            escalated.append(d)
        elif d["risk_level"] == "high" and d["category"] in ("cardiovascular_risk", "metabolic_risk"):
            escalated.append(d)  # sensitive categories escalate regardless of confidence
        else:
            passed.append(d)

    state["passed_decisions"] = passed
    state["escalated_categories"] = escalated
    return state

class MicroDecision(BaseModel):
    category: str
    finding: str
    confidence: float = Field(..., ge=0, le=1)
    risk_level: Literal["low", "moderate", "high"]
    reasoning: str

def run_micro_decision(category, profile_segment):

    extractor = llm.with_structured_output(MicroDecision)

    result = extractor.invoke([
        {
            "role": "system",
            "content": MICRO_DECISION_PROMPT
        },
        {
            "role": "user",
            "content": f"""
Category:
{category}

Profile Data:
{profile_segment}
"""
        }
    ])

    result.category = category

    return result

def decision_layer(state):
    profile_dict = state["profile"].model_dump()
    micro_decisions = []
    for category, fields in CATEGORY_FIELDS.items():
        segment = {f: profile_dict.get(f) for f in fields}
        if all(v is None for v in segment.values()):
            continue
        decision = run_micro_decision(category, segment)
        micro_decisions.append(decision.model_dump())
    state["micro_decisions"] = micro_decisions
    return state

def rule_engine(state: HealthState):
    profile = state["profile"]

    if profile.height and profile.weight:
        bmi = profile.weight / ((profile.height / 100) ** 2)
        if bmi >= 30:
            state["escalated_categories"].append({
                "category": "weight_status", "finding": "BMI indicates obesity range",
                "confidence": 1.0, "risk_level": "high", "reasoning": f"BMI = {bmi:.1f}"
            })
            state["passed_decisions"] = [d for d in state["passed_decisions"] if d["category"] != "weight_status"]

    return state


def output_layer(state: HealthState):
    lines = []

    for d in state["passed_decisions"]:
        confidence_label = "high confidence" if d["confidence"] >= 0.75 else "moderate confidence"
        lines.append(f"**{d['category'].replace('_', ' ').title()}** ({confidence_label}): {d['finding']} — {d['reasoning']}")

    for d in state["escalated_categories"]:
        lines.append(f"**{d['category'].replace('_', ' ').title()}**: This needs a closer look from a professional before we suggest anything — flagged for review.")

    reply_prompt = f"""Turn these clinical findings into a warm, non-alarming set of prevention suggestions for the user, in {state.get('language', 'English')}.
Keep the same facts and confidence framing — do not add new claims.

Findings:
{chr(10).join(lines)}
"""
    reply = llm.invoke([{"role": "user", "content": reply_prompt}])
    state["messages"].append({"role": "assistant", "content": reply.content})
    return state

def risk_persistence(state: HealthState):

    risks = (
        state["passed_decisions"]
        +
        state["escalated_categories"]
    )

    save_risk_assessment(
        state["user_id"],
        risks
    )

    return state