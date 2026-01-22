
from services.nutrition import calculate_bmr, calculate_daily_limit
from models.sql_models import UserProfile
import datetime

class AdaptiveDietService:
    
    @staticmethod
    def get_realtime_advice(profile: UserProfile, consumed: int, burned_walking: int, water_ml: int):
        """
        Generates dynamic advice based on current live status.
        """
        # 1. Calculate baselines
        bmr = calculate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
        daily_limit = calculate_daily_limit(bmr, profile.activity_level, profile.goal)
        
        # Effective Remaining: Limit + Burned - Eaten
        effective_remaining = (daily_limit + burned_walking) - consumed
        
        # Time of day
        hour = datetime.datetime.now().hour
        time_slot = "Morning"
        if 11 <= hour < 15: time_slot = "Lunch"
        elif 15 <= hour < 19: time_slot = "Snack"
        elif hour >= 19: time_slot = "Dinner"
        
        # Advice Logic
        status = "Good"
        color = "green"
        recommendation = ""
        
        # Rule Set 1: Calorie Balance
        if effective_remaining < 0:
            status = "Over Limit"
            color = "red"
            recommendation = f"You have exceeded your target by {abs(effective_remaining)} kcal. Try to take a 20 min walk to balance it out."
            
        elif effective_remaining < 200 and hour < 18:
            status = "Tight Budget"
            color = "orange"
            recommendation = "You have very few calories left for the day. Choose low-calorie, high-volume foods like salads or clear soups."
            
        else:
            status = "On Track"
            if time_slot == "Dinner":
                recommendation = "You have a good calorie buffer. Enjoy a balanced dinner with protein and fiber."
            else:
                 recommendation = f"You have {effective_remaining} kcal available. Stay consistent!"

        # Rule Set 2: Activity Adjustment
        if burned_walking > 300:
            recommendation += " Great walking effort! You've earned some extra flexibility."
            
        # Rule Set 3: Medical Specifics
        conditions = profile.medical_conditions.lower() if profile.medical_conditions else ""
        if "diabetes" in conditions:
            if consumed > (daily_limit * 0.5) and hour < 12:
                recommendation = "Caution: You've consumed 50% of your calories early. Watch your glucose levels."
                color = "orange"
                
        return {
            "time_slot": time_slot,
            "status": status,
            "color": color,
            "remaining": int(effective_remaining),
            "recommendation": recommendation,
            "limit": int(daily_limit)
        }
