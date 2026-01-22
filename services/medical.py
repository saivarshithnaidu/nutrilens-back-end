from typing import List
from models.schemas import UserProfile, NutritionInfo

class MedicalEngine:
    @staticmethod
    def analyze(user: UserProfile, nutrition: NutritionInfo, food_names: List[str]) -> (List[str], str):
        warnings = []
        advice = []

        # Diabetes Rules
        if "diabetes" in [c.lower() for c in user.medical_conditions]:
            if nutrition.sugar_g > 10:
                warnings.append("High sugar content detected. Not suitable for diabetes.")
            if nutrition.carbs_g > 50:
                warnings.append("High carbohydrate load. Monitor insulin.")
            advice.append("Prioritize fiber-rich foods to stabilize blood sugar.")

        # Hypertension Rules
        if "hypertension" in [c.lower() for c in user.medical_conditions] or "bp" in [c.lower() for c in user.medical_conditions]:
             # Assuming we had salt data, but general advice for now
             advice.append("Avoid adding extra salt. Drink plenty of water.")
             if any("pickle" in f.lower() or "chips" in f.lower() for f in food_names):
                 warnings.append("Detected high-sodium food item.")

        # General Advice based on Macros
        if nutrition.protein_g < 10:
             advice.append("This meal is low in protein. Consider adding a protein source.")
        
        return warnings, " ".join(advice)
