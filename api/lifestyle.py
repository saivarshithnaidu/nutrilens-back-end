
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.sql_models import DailyActivity, UserProfile, User
from api.auth import get_current_user
from services.lifestyle import LifestyleService
from services.diet_generator import DietGenerator
from pydantic import BaseModel
import datetime

router = APIRouter()

# Schema Input Models
class WalkLog(BaseModel):
    steps: int = 0
    duration_min: int = 0

class WaterLog(BaseModel):
    amount_ml: int = 250 # Default glass size

class DietPlanResponse(BaseModel):
    daily_calories: int
    goal: str
    meals: dict

@router.post("/log/walk")
def log_walking(log: WalkLog, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = datetime.date.today()
    activity = db.query(DailyActivity).filter(DailyActivity.user_id == current_user.id, DailyActivity.date == today).first()
    
    if not activity:
        activity = DailyActivity(user_id=current_user.id, date=today)
        db.add(activity)
    
    # Update Stats
    if log.steps > 0:
        activity.steps_count += log.steps
    if log.duration_min > 0:
        activity.walking_duration_min += log.duration_min
        
    # Get weight for accurate calc
    weight = 70.0
    if current_user.profile:
        weight = current_user.profile.weight_kg
        
    burned = LifestyleService.calculate_walking_calories(log.steps, log.duration_min, weight)
    activity.calories_burned_walking += burned
    
    db.commit()
    return {"message": "Walking logged", "burned": burned}

@router.post("/log/water")
def log_water(log: WaterLog, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = datetime.date.today()
    activity = db.query(DailyActivity).filter(DailyActivity.user_id == current_user.id, DailyActivity.date == today).first()
    
    if not activity:
        activity = DailyActivity(user_id=current_user.id, date=today)
        db.add(activity)
        
    activity.water_intake_ml += log.amount_ml
    
    # Check target
    weight = 70.0
    if current_user.profile:
        weight = current_user.profile.weight_kg
    
    target = LifestyleService.calculate_daily_water_target(weight)
    activity.water_target_ml = target
    
    db.commit()
    
    advice = LifestyleService.get_hourly_drink_status(activity.water_intake_ml, target)
    
    return {"message": "Water logged", "total": activity.water_intake_ml, "advice": advice}

@router.get("/stats")
def get_daily_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = datetime.date.today()
    activity = db.query(DailyActivity).filter(DailyActivity.user_id == current_user.id, DailyActivity.date == today).first()
    
    # Calc target on fly if missing
    weight = 70.0
    if current_user.profile:
        weight = current_user.profile.weight_kg
    water_target = LifestyleService.calculate_daily_water_target(weight)
    
    if not activity:
        return {
            "steps": 0,
            "calories_burned": 0,
            "water_ml": 0,
            "water_target": water_target,
            "water_advice": "Start your day with a glass of water!"
        }
        
    advice = LifestyleService.get_hourly_drink_status(activity.water_intake_ml, water_target)
    
    return {
        "steps": activity.steps_count,
        "calories_burned": int(activity.calories_burned_walking),
        "water_ml": activity.water_intake_ml,
        "water_target": water_target,
        "water_advice": advice
    }

from services.adaptive_diet import AdaptiveDietService

class AdviceRequest(BaseModel):
    consumed: int
    burned: int
    water: int

@router.post("/adaptive_advice")
def get_adaptive_advice(req: AdviceRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.profile:
        # Return generic safe advice if no profile
        return {
            "time_slot": "Day",
            "status": "No Profile",
            "color": "gray",
            "remaining": 2000 - req.consumed,
            "recommendation": "Please complete your profile for personalized advice.",
            "limit": 2000
        }
        
    advice = AdaptiveDietService.get_realtime_advice(current_user.profile, req.consumed, req.burned, req.water)
    return advice
