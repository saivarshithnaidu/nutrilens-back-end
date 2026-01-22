from pydantic import BaseModel
from typing import List, Optional

class UserProfileSchema(BaseModel):
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str  # sedentary, light, moderate, active
    diet_preset: str = "maintenance" # weight_loss, weight_gain, maintenance, diabetic
    medical_conditions: List[str] = []  # e.g., "diabetes", "hypertension"

class PortionOption(BaseModel):
    name: str
    weight_g: float

class NutritionInfo(BaseModel):
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    sugar_g: float

class FoodAnalysis(BaseModel):
    name: str
    confidence: float
    nutrition_per_100g: NutritionInfo
    available_portions: List[PortionOption]
    default_portion: PortionOption
    traffic_light: str # green, yellow, red
    warnings: List[str]
    context_message: str # "Equivalent to..."

class AnalysisResult(BaseModel):
    foods: List[FoodAnalysis]
    summary_message: str

