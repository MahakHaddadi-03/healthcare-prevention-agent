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
    blood_pressure: Optional[str] = None


class HealthState(TypedDict):
    # Conversation history
    messages: list[dict[str, str]]

    # User health profile
    profile: HealthProfile

    # Workflow state
    missing_fields: list[str]
    completed: bool
    next_field: Optional[str]
    follow_up_question: str

    # User preference
    language: Optional[Literal["en", "fa"]]


required_fields = [
    "name",
    "age",
    "gender",
    "height",
    "weight",
    "medications",
    "allergies",
    "family_history",
]


class ExtractedInfo(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="User's name and family name."
    )
    age: Optional[int] = Field(
        default=None,
        description="User's age in years."
    )

    gender: Optional[str] = Field(
        default=None,
        description="User's gender."
    )

    height: Optional[float] = Field(
        default=None,
        description="User's height in centimeters."
    )

    weight: Optional[float] = Field(
        default=None,
        description="User's weight in kilograms."
    )

    diabetes: Optional[bool] = Field(
        default=None,
        description="Whether the user has diabetes."
    )

    heart_disease: Optional[bool] = Field(
        default=None,
        description="Whether the user has heart disease."
    )

    allergies: Optional[list[str]] = Field(
        default=None,
        description=(
            "List of the user's allergies. "
            "If the user explicitly says they have no allergies, return an empty list []."
        ),
    )

    medications: Optional[list[str]] = Field(
        default=None,
        description=(
            "List of the user's current medications. "
            "If the user explicitly says they take no medication, return an empty list []."
        ),
    )

    family_history: Optional[str] = Field(
        default=None,
        description="Relevant family medical history."
    )

    exercise: Optional[bool] = Field(
        default=None,
        description="Whether the user exercises regularly."
    )

    smoking: Optional[bool] = Field(
        default=None,
        description="Whether the user currently smokes."
    )

    blood_pressure: Optional[str] = Field(
        default=None,
        description="The user's blood pressure if mentioned."
    )