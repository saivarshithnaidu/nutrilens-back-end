
from models.sql_models import UserProfile, DailyActivity
import datetime

# MET Value for Walking (Moderate pace -> 3.5)
MET_WALKING = 3.5
CALORIES_PER_STEP = 0.04 # Standard approximation

class LifestyleService:
    
    @staticmethod
    def calculate_walking_calories(steps: int = 0, duration_min: int = 0, weight_kg: float = 70.0) -> float:
        """
        Mode A: Steps * 0.04
        Mode B: MET * Weight * Time(hr)
        """
        if steps > 0:
            return steps * CALORIES_PER_STEP
        
        if duration_min > 0:
            duration_hours = duration_min / 60.0
            # Formula: MET * Weight * Time
            return MET_WALKING * weight_kg * duration_hours
            
        return 0.0

    @staticmethod
    def calculate_daily_water_target(weight_kg: float) -> int:
        """
        Target: 35ml per kg body weight
        """
        return int(weight_kg * 35)

    @staticmethod
    def get_hourly_drink_status(current_intake: int, target: int) -> str:
        # Simple logic: Spread intake over ~14 awake hours (e.g. 7am to 9pm)
        # If it's early, low intake is fine. But we just want a reminder if 0 in last hour.
        # Since we don't store hourly logs in DB yet (just daily total), we simulate advice.
        
        # Real-time check logic would need a timestamped log. 
        # For this requirement "Show reminder if no water logged in last 1 hour", 
        # we'll assume the frontend tracks "last_log_time" or we assume simple daily progress.
        
        percent = (current_intake / target) * 100 if target > 0 else 0
        
        # Check time of day to give context
        hour = datetime.datetime.now().hour
        if hour < 10:
             expected_percent = 15
        elif hour < 14:
             expected_percent = 40
        elif hour < 18:
             expected_percent = 70
        else:
             expected_percent = 90
             
        if percent < expected_percent:
            glasses_behind = int((expected_percent - percent) / 100 * target / 250)
            if glasses_behind > 0:
                return f"Drink {glasses_behind} more glasses to catch up!"
        
        return "You are hydrated well!"
