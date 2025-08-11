from pydantic import BaseModel
from datetime import datetime


class WorkoutSchema(BaseModel):
    id: int
    date: datetime
    exercises: list["ExerciseSchema"]

    class Config:
        orm_mode = True


class ExerciseSchema(BaseModel):
    id: int
    name: str
    workout_id: int
    workout: "WorkoutSchema"
    sets: list["SetSchema"]

    class Config:
        orm_mode = True


class SetSchema(BaseModel):
    id: int
    reps: int
    weight: int
    exercise_id: int
    exercise: "ExerciseSchema"

    class Config:
        orm_mode = True


class WorkoutRequestSchema(BaseModel):
    date: datetime
    exercises: list["ExerciseRequestSchema"]


class ExerciseRequestSchema(BaseModel):
    name: str
    workout_id: int
    sets: list["SetRequestSchema"]


class SetRequestSchema(BaseModel):
    reps: int
    weight: int
    exercise_id: int


class WorkoutResponseSchema(BaseModel):
    id: int
    date: datetime
    exercises: list["ExerciseResponseSchema"]


class ExerciseResponseSchema(BaseModel):
    id: int
    name: str
    workout_id: int
    workout: "WorkoutResponseSchema"
    sets: list["SetResponseSchema"]


class SetResponseSchema(BaseModel):
    id: int
    reps: int
    weight: int
    exercise_id: int
    exercise: "ExerciseResponseSchema"
