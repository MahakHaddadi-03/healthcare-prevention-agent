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
        "follow_up_question": "",
        "completed": False,
        "next_field": "",
        "language": language,
    }


@cl.on_chat_start
async def start():
    await cl.Message(
    content="🌍 Please choose your language.\n\n🌍 لطفاً زبان خود را انتخاب کنید.",
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

    cl.user_session.set("state", state)

    if state["messages"]:
        welcome = RESUME_FA if language == "fa" else RESUME_EN
    else:
        welcome = WELCOME_FA if language == "fa" else WELCOME_EN

    await cl.Message(content=welcome).send()
@cl.on_message
async def main(message: cl.Message):

    user_id = cl.user_session.get("id")
    state: HealthState | None = cl.user_session.get("state")

    if state is None:
        await cl.Message(
            content="Please select a language first."
        ).send()
        return

    state["messages"].append(
        {
            "role": "user",
            "content": message.content,
        }
    )

    try:
        state = graph.invoke(state)

    except Exception as e:
        print(e)

        await cl.Message(
            content=(
                "Sorry, something went wrong while processing your message."
                if state["language"] == "en"
                else "متأسفانه هنگام پردازش پیام شما خطایی رخ داد."
            )
        ).send()
        return

    cl.user_session.set("state", state)
    save_state(user_id, state)

    if state["messages"] and state["messages"][-1]["role"] == "assistant":
        await cl.Message(
            content=state["messages"][-1]["content"]
        ).send()
