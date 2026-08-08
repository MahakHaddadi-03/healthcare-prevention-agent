from typing import Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class HealthProfile(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    diabetes: Optional[bool] = None
    heart_disease: Optional[bool] = None
    allergies: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    family_history: Optional[str] = None
    exercise: Optional[bool] = None
    smoking: Optional[bool] = None
    diet: Optional[str] = None
    blood_pressure: Optional[str] = None


class HealthState(TypedDict):
    messages: list[dict[str, str]]
    profile: HealthProfile
    missing_fields: list[str]
    completed: bool
    next_field: Optional[list[str]]  
    follow_up_question: str
    language: Optional[Literal["en", "fa"]]
    user_id: Optional[str]
    session_id: Optional[str]
    micro_decisions: list[dict]       
    passed_decisions: list[dict]       
    escalated_categories: list[dict]


required_fields = [
    "name", "age", "gender", "height", "weight",
    "medications", "allergies", "family_history",
    "exercise", "smoking", "diet"
]


class ExtractedInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="User's name.")
    age: Optional[int] = Field(default=None, description="User's age.")
    gender: Optional[str] = Field(default=None, description="User's gender.")
    height: Optional[float] = Field(default=None, description="User's height in centimeters.")
    weight: Optional[float] = Field(default=None, description="User's weight in kilograms.")
    diabetes: Optional[bool] = Field(default=None, description="Whether the user has diabetes.")
    heart_disease: Optional[bool] = Field(default=None, description="Whether the user has heart disease.")
    allergies: Optional[list[str]] = Field(default=None, description="User allergies. Return empty list if user has no allergies.")
    medications: Optional[list[str]] = Field(default=None, description="User medications, vitamins, and supplements. Return empty list if none.")
    family_history: Optional[str] = Field(default=None, description="Family medical history.")
    exercise: Optional[bool] = Field(default=None, description="Whether the user exercises regularly.")
    smoking: Optional[bool] = Field(default=None, description="Whether the user smokes.")
    diet: Optional[str] = Field(default=None, description="User diet habits.")
    blood_pressure: Optional[str] = Field(default=None, description="User blood pressure if mentioned.")