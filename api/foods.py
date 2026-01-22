from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.sql_models import FoodItem, PortionSize
from pydantic import BaseModel
from typing import List

router = APIRouter()

class PortionSchema(BaseModel):
    id: int
    name: str
    weight_g: float

class FoodItemSchema(BaseModel):
    id: int
    name: str
    portions: List[PortionSchema]

@router.get("/foods", response_model=List[FoodItemSchema])
def get_all_foods(db: Session = Depends(get_db)):
    foods = db.query(FoodItem).all()
    results = []
    for f in foods:
        portions = [PortionSchema(id=p.id, name=p.portion_name, weight_g=p.weight_g) for p in f.portions]
        results.append(FoodItemSchema(id=f.id, name=f.name, portions=portions))
    return results

from pydantic import BaseModel
from services.nutrition import check_medical_safety, get_traffic_light_color, get_activity_equivalent
from models.sql_models import UserProfile # DB Model

class CheckRequest(BaseModel):
    food_id: int
    portion_weight_g: float
    user_profile: dict # Simpler to pass profile dict from frontend for this stateless check

@router.post("/check_food")
def check_food_health(req: CheckRequest, db: Session = Depends(get_db)):
    food = db.query(FoodItem).get(req.food_id)
    if not food:
        return {"error": "Food not found"}
    
    # Construct temp profile
    from models.sql_models import UserProfile as DBProfile
    p_data = req.user_profile
    profile = DBProfile(
        diet_preset=p_data.get('diet_preset', 'maintenance'),
        medical_conditions=",".join(p_data.get('medical_conditions', []))
    )
    
    warnings = check_medical_safety(food, profile)
    light = get_traffic_light_color(food, profile)
    
    calories = (req.portion_weight_g / 100) * food.calories_100g
    context = get_activity_equivalent(calories)
    
    return {
        "calories": int(calories),
        "traffic_light": light,
        "warnings": warnings,
        "context_message": context
    }
