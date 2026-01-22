
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.sql_models import HealthAlert, WeightLog, User
from api.auth import get_current_user
from services.safety import SafetyService
from pydantic import BaseModel
import datetime
import json

router = APIRouter()

class WeightEntry(BaseModel):
    weight_kg: float

@router.post("/log/weight")
def log_weight_api(entry: WeightEntry, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Update Profile if exists
    if current_user.profile:
        current_user.profile.weight_kg = entry.weight_kg
    
    # 2. Add to Log
    new_log = WeightLog(
        user_id=current_user.id,
        date=datetime.date.today(),
        weight_kg=entry.weight_kg
    )
    db.add(new_log)
    db.commit()
    
    # 3. Trigger Safety Check
    alerts = SafetyService.check_for_anomalies(db, current_user.id)
    created_alerts = []
    for a in alerts:
        saved = SafetyService.save_alert(db, current_user.id, a)
        created_alerts.append(saved)
        
    return {"message": "Weight updated", "alerts_generated": len(created_alerts)}

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # First, run a check to ensure fresh alerts
    anomalies = SafetyService.check_for_anomalies(db, current_user.id)
    for a in anomalies:
        SafetyService.save_alert(db, current_user.id, a)
        
    # Fetch active alerts
    alerts = db.query(HealthAlert).filter(
        HealthAlert.user_id == current_user.id,
        HealthAlert.is_consulted == False
    ).all()
    
    # Parse JSON
    result = []
    for a in alerts:
        result.append({
            "id": a.id,
            "type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "tests": json.loads(a.suggested_tests) if a.suggested_tests else [],
            "date": a.date
        })
        
    return result

@router.post("/alerts/{id}/resolve")
def resolve_alert(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(HealthAlert).filter(HealthAlert.id == id, HealthAlert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_consulted = True
    db.commit()
    return {"message": "Alert marked as consulted."}
