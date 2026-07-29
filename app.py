import chainlit as cl

from graph import graph
from state import HealthProfile, HealthState
from storage import load_state, save_state

from prompts import (
    WELCOME_EN,
    WELCOME_FA,
    RESUME_EN,
    RESUME_FA,
)



def create_initial_state(language: str) -> HealthState:

    return {
        "messages": [],

        "profile": HealthProfile(),

        "missing_fields": [],

        "completed": False,

        "next_field": None,

        "follow_up_question": "",

        "language": language,

        "initial_intake_done": False,
    }




def get_initial_intake(language):

    if language == "fa":

        return """
برای ساخت پروفایل سلامت، لطفاً هر اطلاعاتی که درباره وضعیت سلامت خود می‌دانید را در یک پیام بنویسید.

می‌توانید شامل موارد زیر باشد:

- نام
- سن
- جنسیت
- قد
- وزن
- داروها، ویتامین‌ها یا مکمل‌ها
- آلرژی‌ها
- سابقه بیماری‌های خانوادگی
- بیماری‌های فعلی
- فعالیت ورزشی
- مصرف سیگار
- رژیم غذایی

لازم نیست همه موارد را پاسخ دهید.
بعد از بررسی پاسخ شما، فقط اطلاعاتی که باقی مانده‌اند را می‌پرسم.
"""


    return """
To build your health profile, please share any health information you already know in one message.

You may include:

- Name
- Age
- Gender
- Height
- Weight
- Medications, vitamins, or supplements
- Allergies
- Family medical history
- Existing diseases
- Exercise habits
- Smoking
- Diet

You don't need to answer everything.
After reviewing your answer, I will only ask about missing information.
"""




@cl.on_chat_start
async def start():

    await cl.Message(
        content=
        "🌍 Please choose your language.\n\n"
        "🌍 لطفاً زبان خود را انتخاب کنید.",

        actions=[

            cl.Action(
                name="choose_language",
                payload={"language": "en"},
                label="🇬🇧 English",
            ),

            cl.Action(
                name="choose_language",
                payload={"language": "fa"},
                label="🇮🇷 فارسی",
            ),

        ],
    ).send()





@cl.action_callback("choose_language")
async def choose_language(action: cl.Action):

    language = action.payload["language"]

    user_id = cl.user_session.get("id")


    state = load_state(user_id)



    if state is None:

        state = create_initial_state(language)

    else:

        state["language"] = language



    cl.user_session.set(
        "state",
        state
    )



    if state["messages"]:

        welcome = (
            RESUME_FA
            if language == "fa"
            else RESUME_EN
        )


        await cl.Message(
            content=welcome
        ).send()


    else:

        welcome = (
            WELCOME_FA
            if language == "fa"
            else WELCOME_EN
        )


        await cl.Message(
            content=welcome
        ).send()



        intake = get_initial_intake(language)



        state["messages"].append(
            {
                "role": "assistant",
                "content": intake
            }
        )



        state["initial_intake_done"] = True



        cl.user_session.set(
            "state",
            state
        )



        await cl.Message(
            content=intake
        ).send()






@cl.on_message
async def main(message: cl.Message):

    user_id = cl.user_session.get("id")


    state = cl.user_session.get("state")



    if state is None:

        await cl.Message(
            content="Please select a language first."
        ).send()

        return




    state["messages"].append(
        {
            "role": "user",
            "content": message.content
        }
    )



    try:

        state = graph.invoke(state)



    except Exception as e:

        print(
            "GRAPH ERROR:",
            e
        )


        await cl.Message(
            content=(
                "Sorry, something went wrong."
                if state["language"] == "en"
                else
                "متأسفانه خطایی رخ داد."
            )
        ).send()


        return




    cl.user_session.set(
        "state",
        state
    )


    save_state(
        user_id,
        state
    )




    last_message = state["messages"][-1]



    if last_message["role"] == "assistant":

        await cl.Message(
            content=last_message["content"]
        ).send()