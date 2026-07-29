from config import llm

from prompts import (
    EXTRACTION_PROMPT,
    TONE_SYSTEM_PROMPT
)

from state import (
    ExtractedInfo,
    HealthState,
    required_fields
)



def interaction(state: HealthState):

    extractor = llm.with_structured_output(
        ExtractedInfo
    )


    result = extractor.invoke(
        [
            {
                "role": "system",
                "content": EXTRACTION_PROMPT,
            },

            *state["messages"]
        ]
    )


    extracted = result.model_dump()


    profile = state["profile"]


    for key, value in extracted.items():

        if value is not None:

            setattr(
                profile,
                key,
                value
            )


    state["profile"] = profile


    return state





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

        # Ask several missing topics together
        state["next_field"] = (
            state["missing_fields"][:4]
        )


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