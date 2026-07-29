from graph import graph
from state import HealthState, HealthProfile


def run():

    state: HealthState = {
        "messages": [],
        "profile": HealthProfile(),
        "missing_fields": [],
        "follow_up_question": "",
        "completed": False,
        "next_field": ""
    }

    print(
        "Assistant: Hi! I'd love to get to know a bit about your health."
    )

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        state["messages"].append(
            {
                "role": "user",
                "content": user_input
            }
        )

        state = graph.invoke(state)

        print(
            "Assistant:",
            state["follow_up_question"]
        )

        if state["completed"]:
            break


if __name__ == "__main__":
    run()

