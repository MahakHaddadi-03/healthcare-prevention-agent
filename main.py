from graph import graph
from state import HealthState, HealthProfile


def run():

    state: HealthState = {
        "messages": [],
        "profile": HealthProfile(),
        "missing_fields": [],
        "follow_up_question": "",
        "completed": False,
        "next_field": None,
        "language": "en",
        "initial_intake_done": False,
    }

    print("Assistant: Hi! I'd love to get to know a bit about your health.")

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        state["messages"].append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        state = graph.invoke(state)

        if state["messages"] and state["messages"][-1]["role"] == "assistant":
            print("Assistant:", state["messages"][-1]["content"])

        if state["completed"]:
            break


if __name__ == "__main__":
    run()