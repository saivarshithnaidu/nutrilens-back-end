from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    profile_image = Column(String, nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    logs = relationship("DailyLog", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    age = Column(Integer)
    gender = Column(String)
    activity_level = Column(String)
    diet_preset = Column(String) # legacy from phase 1, keep or sync with new goal
    diet_preference = Column(String, default="non_veg") # veg, non_veg, vegan
    goal = Column(String, default="maintenance") # weight_loss, weight_gain, maintenance
    medical_conditions = Column(String)
    target_calories = Column(Integer, nullable=True)

    user = relationship("User", back_populates="profile")

class DailyActivity(Base):
    __tablename__ = "daily_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.date.today)
    
    steps_count = Column(Integer, default=0)
    walking_duration_min = Column(Integer, default=0)
    calories_burned_walking = Column(Float, default=0.0)
    
    water_intake_ml = Column(Integer, default=0)
    water_target_ml = Column(Integer, default=0)
    
    # Relationships if needed
    user = relationship("User")

class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.date.today)
    weight_kg = Column(Float)

class HealthAlert(Base):
    __tablename__ = "health_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.date.today)
    alert_type = Column(String) # rapid_weight_loss, sudden_gain, low_intake, low_water
    severity = Column(String) # low, medium, high
    message = Column(String)
    suggested_tests = Column(String) # JSON string of list
    is_consulted = Column(Boolean, default=False)
    
    user = relationship("User")

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    calories_100g = Column(Float)
    protein_100g = Column(Float)
    carbs_100g = Column(Float)
    fat_100g = Column(Float)
    sugar_100g = Column(Float)

    portions = relationship("PortionSize", back_populates="food")
    logs = relationship("DailyLog", back_populates="food")

class PortionSize(Base):
    __tablename__ = "portion_sizes"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("food_items.id"))
    portion_name = Column(String)  # e.g., "1 bowl", "1 piece", "1 cup"
    weight_g = Column(Float)

    food = relationship("FoodItem", back_populates="portions")

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("food_items.id"), nullable=True) # Nullable if custom manual entry without DB food
    food_name = Column(String) # Store name even if linked, for history preservation
    date = Column(Date, default=datetime.date.today)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    portion_consumed_g = Column(Float)
    calories_calc = Column(Float)
    protein_calc = Column(Float)
    carbs_calc = Column(Float)
    fat_calc = Column(Float)
    sugar_calc = Column(Float)
    
    user = relationship("User", back_populates="logs")
    food = relationship("FoodItem", back_populates="logs")

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reset_token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    used = Column(Boolean, default=False)

    user = relationship("User")
