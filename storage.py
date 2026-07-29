import json
import os

from state import HealthProfile, HealthState

STORAGE_DIR = "user_data"
os.makedirs(STORAGE_DIR, exist_ok=True)


def save_state(user_id: str, state: HealthState) -> None:
    path = os.path.join(STORAGE_DIR, f"{user_id}.json")

    serializable = {
        "messages": state["messages"],
        "profile": state["profile"].model_dump(),
        "missing_fields": state["missing_fields"],
        "follow_up_question": state.get("follow_up_question", ""),
        "completed": state["completed"],
        "next_field": state.get("next_field"),
        "language": state.get("language"),
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            serializable,
            f,
            ensure_ascii=False,
            indent=4,
        )


def load_state(user_id: str) -> HealthState | None:
    path = os.path.join(STORAGE_DIR, f"{user_id}.json")

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "messages": data.get("messages", []),
        "profile": HealthProfile(**data.get("profile", {})),
        "missing_fields": data.get("missing_fields", []),
        "follow_up_question": data.get("follow_up_question", ""),
        "completed": data.get("completed", False),
        "next_field": data.get("next_field"),
        "language": data.get("language"),
    }