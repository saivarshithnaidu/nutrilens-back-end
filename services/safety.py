
from sqlalchemy.orm import Session
from models.sql_models import User, WeightLog, DailyLog, DailyActivity, HealthAlert, UserProfile
from datetime import datetime, timedelta, date
import json

class SafetyService:

    @staticmethod
    def check_for_anomalies(db: Session, user_id: int):
        """
        Main runner to check all health rules.
        Should be called when relevant data is updated (e.g. daily, or on weight log).
        """
        active_alerts = []
        
        # 1. Weight Analysis
        w_alert = SafetyService._check_weight_trend(db, user_id)
        if w_alert: active_alerts.append(w_alert)
        
        # 2. Calorie Analysis
        c_alert = SafetyService._check_calorie_trend(db, user_id)
        if c_alert: active_alerts.append(c_alert)
        
        # 3. Water Analysis
        # wtr_alert = SafetyService._check_water_trend(db, user_id)
        # if wtr_alert: active_alerts.append(wtr_alert)

        return active_alerts

    @staticmethod
    def _check_weight_trend(db: Session, user_id: int):
        # Get logs sorted by date desc
        logs = db.query(WeightLog).filter(WeightLog.user_id == user_id).order_by(WeightLog.date.desc()).limit(14).all()
        
        if len(logs) < 2:
            return None
            
        current = logs[0]
        past_7_days = None
        
        # Find log closest to 7 days ago
        target_date = current.date - timedelta(days=7)
        for log in logs:
            if log.date <= target_date:
                past_7_days = log
                break
        
        if not past_7_days:
            # Fallback: check 5% in month logic if we have data, but keep simple for now
            return None
            
        diff = current.weight_kg - past_7_days.weight_kg
        
        # Rule A: Weight loss > 2kg in 7 days
        if diff < -2.0:
            return SafetyService._create_alert_obj(
                user_id, "rapid_weight_loss", "high",
                "Unexpected weight loss detected (>2kg in 7 days).",
                ["CBC", "Thyroid Profile", "LFT", "Blood Sugar (FBS/HbA1c)"]
            )
            
        # Rule B: Sudden Gain > 2kg
        if diff > 2.0:
             return SafetyService._create_alert_obj(
                user_id, "rapid_weight_gain", "medium",
                "Rapid weight gain detected (>2kg in 7 days). Possible fluid retention.",
                ["Kidney Function Test (KFT)", "Thyroid Profile", "Lipid Profile"]
            )
            
        return None

    @staticmethod
    def _check_calorie_trend(db: Session, user_id: int):
        # Check last 3 days
        today = date.today()
        start = today - timedelta(days=3)
        
        logs = db.query(DailyLog).filter(
            DailyLog.user_id == user_id, 
            DailyLog.date >= start,
            DailyLog.date < today # Don't count today as it might be incomplete
        ).all()
        
        # Group by date
        daily_cals = {}
        for log in logs:
            d_str = str(log.date)
            daily_cals[d_str] = daily_cals.get(d_str, 0) + (log.calories_calc or 0)
            
        if len(daily_cals) < 3:
            return None # Need 3 full days of history
            
        # Check if ALL 3 days < 1200
        low_days = 0
        for day_cals in daily_cals.values():
            if day_cals < 1200:
                low_days += 1
                
        if low_days >= 3:
             return SafetyService._create_alert_obj(
                user_id, "low_calorie_intake", "medium",
                "Calorie intake has been very low (<1200 kcal) for 3 days.",
                ["Consult Dietitian", "Vitamin B12", "Vitamin D"]
            )
            
        return None

    @staticmethod
    def _create_alert_obj(user_id, type, sev, msg, tests):
        return {
            "alert_type": type,
            "severity": sev,
            "message": msg,
            "suggested_tests": json.dumps(tests)
        }
        
    @staticmethod
    def save_alert(db: Session, user_id: int, alert_data: dict):
        # Check cooldown: Don't show same alert type if active one exists today
        existing = db.query(HealthAlert).filter(
            HealthAlert.user_id == user_id,
            HealthAlert.alert_type == alert_data['alert_type'],
            HealthAlert.is_consulted == False,
            HealthAlert.date == date.today()
        ).first()
        
        if existing:
            return existing
            
        new_alert = HealthAlert(
            user_id=user_id,
            alert_type=alert_data['alert_type'],
            severity=alert_data['severity'],
            message=alert_data['message'],
            suggested_tests=alert_data['suggested_tests']
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        return new_alert
