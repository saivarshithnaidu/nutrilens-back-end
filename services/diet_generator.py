
from services.nutrition import calculate_bmr, calculate_daily_limit
from models.sql_models import UserProfile, FoodItem
from typing import List, Dict

class DietGenerator:
    
    @staticmethod
    def generate_plan(profile: UserProfile):
        # 1. Calculate Targets
        bmr = calculate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
        daily_calories = calculate_daily_limit(bmr, profile.activity_level, profile.goal)
        
        # Medical Checks
        conditions = [c.strip().lower() for c in profile.medical_conditions.split(",")] if profile.medical_conditions else []
        is_diabetic = "diabetes" in conditions or "diabetic" in conditions
        is_bp = "bp" in conditions or "hypertension" in conditions
        
        # Meal Split
        # Breakfast 25%, Lunch 35%, Snack 15%, Dinner 25%
        targets = {
            "Breakfast": int(daily_calories * 0.25),
            "Lunch": int(daily_calories * 0.35),
            "Snack": int(daily_calories * 0.15),
            "Dinner": int(daily_calories * 0.25)
        }
        
        # Suggest Foods (Mock Logic based on preferences)
        # In a real app, this would query DB for foods matching criteria
        is_veg = getattr(profile, 'diet_preference', 'non_veg') == 'veg'
        
        suggestions = {}
        
        for meal, cal_target in targets.items():
            meal_suggestion = DietGenerator._get_suggestion(meal, cal_target, is_veg, is_diabetic, is_bp)
            suggestions[meal] = meal_suggestion
            
        return {
            "daily_calories": daily_calories,
            "goal": profile.goal,
            "meals": suggestions
        }

    @staticmethod
    def _get_suggestion(meal: str, calories: int, is_veg: bool, is_diabetic: bool, is_bp: bool) -> Dict:
        # Rule Based Suggestions
        food_name = "Standard Meal"
        desc = "Balanced meal"
        
        if meal == "Breakfast":
            if is_diabetic:
                food_name = "Oats Upma with Vegetables" if is_veg else "Egg White Omelet + Multigrain Toast"
                desc = "Low GI, High Fiber"
            else:
                food_name = "Poha with Peanuts" if is_veg else "Boiled Eggs + Toast"
                desc = "Energy start"
                
        elif meal == "Lunch":
            if is_veg:
                food_name = "2 Roti + Dal + Sabzi + Salad"
            else:
                food_name = "Rice + Chicken Curry + Salad"
            
            if is_diabetic:
                food_name = food_name.replace("Rice", "Brown Rice").replace("Potato", "Green Veg")

        elif meal == "Snack":
            if is_diabetic:
                food_name = "Roasted Chana / Nuts"
            else:
                food_name = "Fruit + Green Tea"
                
        elif meal == "Dinner":
            # Light dinner logic
            food_name = "Grilled Paneer Salad" if is_veg else "Grilled Fish/Chicken + Soup"
            if is_bp:
                desc = "Low Sodium"
        
        return {
            "food": food_name,
            "target_calories": calories,
            "description": desc
        }
