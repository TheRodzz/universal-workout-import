from pydantic import BaseModel, Field
from typing import List, Optional


class Reps(BaseModel):
    is_range: bool = Field(..., alias="isRange")
    value: str
    min: str
    max: str

    class Config:
        populate_by_name = True


class Weight(BaseModel):
    value: str
    unit: str


class RestTime(BaseModel):
    value: str
    unit: str


class SetItem(BaseModel):
    set_number: int = Field(..., alias="Set Number")
    reps: Reps = Field(..., alias="Reps")
    weight: Weight = Field(..., alias="Weight")
    rest_time: RestTime = Field(..., alias="Rest Time")

    class Config:
        populate_by_name = True


class Exercise(BaseModel):
    exercise_name: str = Field(..., alias="Exercise Name", description="Name of the exercise")
    sets: List[SetItem] = Field(..., alias="Sets")
    notes: str = Field(default="", alias="Notes", description="Additional notes for the exercise")

    class Config:
        populate_by_name = True


class WorkoutDay(BaseModel):
    """Represents exercises for a single workout day"""
    day: str = Field(..., description="Name of the day, e.g., 'Monday' or 'Day 1'")
    exercises: List[Exercise] = Field(..., description="List of exercises for this day")


class WeeklyWorkout(BaseModel):
    """Represents a complete week of workouts"""
    week: str = Field(..., description="Name of the week, e.g., 'Week 1'")
    days: List[WorkoutDay] = Field(..., description="List of workout days for the week")


class WorkoutProgram(BaseModel):
    """Represents the complete workout program with multiple weeks"""
    weeks: List[WeeklyWorkout] = Field(
        ..., 
        description="List of weekly workouts for the program"
    ) 