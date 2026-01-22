
from typing import Dict, List, Optional
from models.sql_models import FoodItem, UserProfile

# Activity Factor Multipliers
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,      # Little or no exercise
    "light": 1.375,        # Light exercise 1-3 days/week
    "moderate": 1.55,      # Moderate exercise 3-5 days/week
    "active": 1.725,       # Hard exercise 6-7 days/week
    "very_active": 1.9     # Very hard exercise & physical job
}

# Diet Goal Adjustments (Calories)
GOAL_ADJUSTMENTS = {
    "weight_loss": -500,
    "weight_gain": 500,
    "maintenance": 0,
    "diabetic": -200,      # Slight deficit usually recommended
    "high_protein": 0       # Focus on macros, but assume maintenance calories
}

def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> int:
    """
    Mifflin-St Jeor Equation
    """
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    return int(bmr)

def calculate_daily_limit(bmr: int, activity_level: str, goal: str) -> int:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    tdee = bmr * multiplier
    adjustment = GOAL_ADJUSTMENTS.get(goal, 0)
    return int(tdee + adjustment)

def check_medical_safety(food: FoodItem, profile: UserProfile) -> List[str]:
    warnings = []
    if not profile.medical_conditions:
        return warnings

    conditions = [c.strip().lower() for c in profile.medical_conditions.split(",")]

    # Diabetes Rule
    if "diabetes" in conditions or "diabetic" in profile.diet_preset:
        if food.sugar_100g > 10:
            warnings.append("High Sugar Control: This food has high sugar content.")
        if food.carbs_100g > 60:
             warnings.append("Carb Monitor: High carbohydrate content.")

    # Hypertension / BP Rule
    if "bp" in conditions or "hypertension" in conditions:
        # Note: Sodium isn't in our standard DB yet, but generic advice:
        # Use existing macros as proxies if needed or skip. 
        # Since we only have fat/sugar/carbs/prot in FoodItem, checks are limited.
        if food.fat_100g > 20: 
             warnings.append("Heart Health: High fat content.")

    return warnings

def get_traffic_light_color(food: FoodItem, profile: UserProfile) -> str:
    """
    Returns 'green', 'yellow', or 'red'
    """
    # Base logic on nutrient density
    score = 0
    
    # Penalize sugar and high fat
    if food.sugar_100g > 15: score += 2
    elif food.sugar_100g > 5: score += 1
    
    if food.fat_100g > 20: score += 2
    elif food.fat_100g > 10: score += 1

    # Medical Overrides
    if profile.medical_conditions:
        conditions = profile.medical_conditions.lower()
        if "diabetes" in conditions and food.sugar_100g > 10:
            return "red"
        if "weight_loss" in profile.diet_preset and food.calories_100g > 400:
             return "red"

    if score >= 3: return "red"
    if score >= 1: return "yellow"
    return "green"

def get_activity_equivalent(calories: float) -> str:
    # Approx burn rates for 70kg person:
    # Walking: ~4 kcal/min
    # Jogging: ~10 kcal/min
    
    walk_min = int(calories / 4)
    jog_min = int(calories / 10)
    
    if walk_min < 10:
         return "Equivalent to a quick walk around the block."
    elif walk_min < 60:
         return f"Equivalent to a {walk_min}-minute walk."
    else:
         return f"Equivalent to {jog_min} minutes of jogging."
