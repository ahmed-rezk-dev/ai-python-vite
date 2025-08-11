from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now, index=True)
    exercises = relationship("Exercise", back_populates="workout")

    def __repr__(self):
        return f"<Workout(id={self.id}, date='{self.date}')>"


class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), index=True)
    workout = relationship("Workout", back_populates="exercises")
    sets = relationship("Set", back_populates="exercise")

    def __repr__(self):
        return f"<Exercise(name='{self.name}')>"


class Set(Base):
    __tablename__ = "sets"
    id = Column(Integer, primary_key=True, index=True)
    reps = Column(Integer, index=True)
    weight = Column(Integer, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), index=True)
    exercise = relationship("Exercise", back_populates="sets")

    def __repr__(self):
        return f"<Set(reps={self.reps}, weight={self.weight})>"
