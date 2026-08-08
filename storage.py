import json
import os
import uuid

import psycopg2

from database import save_profile, load_profile, save_message, load_messages
from state import HealthProfile, HealthState

# Keep this for backward compatibility during migration
STORAGE_DIR = "user_data"
os.makedirs(STORAGE_DIR, exist_ok=True)


def save_state(user_id: str, state: HealthState) -> None:
    session_id = state.get("session_id", str(uuid.uuid4()))

    # Save profile to PostgreSQL
    save_profile(user_id, state["profile"])

    # Save only new messages to PostgreSQL
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        save_message(
            user_id=user_id,
            session_id=session_id,
            role=last_message["role"],
            content=last_message["content"],
            language=state.get("language", "en")
        )


def load_state(user_id: str, session_id: str = None) -> HealthState | None:
    profile_data = load_profile(user_id)

    if not profile_data:
        return None

    # Remove PostgreSQL metadata fields
    profile_fields = {
        k: v for k, v in profile_data.items()
        if k not in ["user_id", "created_at", "updated_at"]
    }
    profile = HealthProfile(**profile_fields)

    # Load conversation history
    messages = []
    if session_id:
        raw_messages = load_messages(user_id, session_id)
        messages = [{"role": m["role"], "content": m["content"]} for m in raw_messages]

    return {
        "messages": messages,
        "profile": profile,
        "missing_fields": [],
        "follow_up_question": "",
        "completed": profile_data.get("completed", False),
        "next_field": None,
        "language": None,
        "user_id": user_id,
        "session_id": session_id,
    }