import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from state import HealthProfile

DB_CONFIG = {
    "host": "localhost",
    "database": "healthcare_agent",
    "user": "postgres",
    "password": "Mahak-2325"  
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def save_profile(user_id: str, profile: HealthProfile):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_profiles 
        (user_id, name, age, gender, height, weight, diabetes,
         heart_disease, allergies, medications, family_history,
         exercise, smoking, diet, blood_pressure)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (user_id) DO UPDATE SET
            name = EXCLUDED.name,
            age = EXCLUDED.age,
            gender = EXCLUDED.gender,
            height = EXCLUDED.height,
            weight = EXCLUDED.weight,
            diabetes = EXCLUDED.diabetes,
            heart_disease = EXCLUDED.heart_disease,
            allergies = EXCLUDED.allergies,
            medications = EXCLUDED.medications,
            family_history = EXCLUDED.family_history,
            exercise = EXCLUDED.exercise,
            smoking = EXCLUDED.smoking,
            diet = EXCLUDED.diet,
            blood_pressure = EXCLUDED.blood_pressure,
            updated_at = NOW()
    """, (
        user_id,
        profile.name, profile.age, profile.gender,
        profile.height, profile.weight, profile.diabetes,
        profile.heart_disease, profile.allergies,
        profile.medications, profile.family_history,
        profile.exercise, profile.smoking,
        profile.diet, profile.blood_pressure
    ))
    conn.commit()
    cursor.close()
    conn.close()

def load_profile(user_id: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(row) if row else None

def save_message(user_id: str, session_id: str, role: str, content: str, language: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversation_history 
        (user_id, session_id, role, content, language)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, session_id, role, content, language))
    conn.commit()
    cursor.close()
    conn.close()

def load_messages(user_id: str, session_id: str) -> list:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT role, content FROM conversation_history
        WHERE user_id = %s AND session_id = %s
        ORDER BY created_at ASC
    """, (user_id, session_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in rows]

def save_risk_assessment(user_id: str, risks: list):
    conn = get_connection()
    cursor = conn.cursor()

    for risk in risks:
        cursor.execute("""
            INSERT INTO risk_assessments
            (
                user_id,
                category,
                finding,
                confidence,
                risk_level,
                reasoning,
                status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            risk.get("category"),
            risk.get("finding"),
            risk.get("confidence"),
            risk.get("risk_level"),
            risk.get("reasoning"),
            risk.get("status", "passed")
        ))

    conn.commit()
    cursor.close()
    conn.close()