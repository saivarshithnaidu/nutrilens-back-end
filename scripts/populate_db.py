
import sys
import os

# Add parent directory to path to allow importing from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
from models.sql_models import FoodItem, PortionSize
from sqlalchemy.orm import Session

def populate_food_data(db: Session):
    # Standard Food Data
    # Format: (Name, Calories, Protein, Carbs, Fat, Sugar) per 100g
    foods = [
        # Staples
        ("White Rice (Cooked)", 130, 2.7, 28, 0.3, 0.1),
        ("Chapati / Roti", 297, 10, 57, 3, 0), # Approx for whole wheat
        ("Dal (Cooked Lentils)", 105, 6, 15, 2, 0),
        ("Curd / Yogurt", 60, 3.5, 4.7, 3.3, 4.7),
        
        # Fruits
        ("Banana", 89, 1.1, 22.8, 0.3, 12.2),
        ("Apple", 52, 0.3, 14, 0.2, 10),
        
        # Proteins
        ("Boiled Egg", 155, 13, 1.1, 11, 1.1),
        ("Chicken Breast (Grilled)", 165, 31, 0, 3.6, 0),
        
        # Breakfast
        ("Oats (Cooked)", 71, 2.5, 12, 1.5, 0.5),
        ("Milk (Whole)", 60, 3.2, 4.8, 3.3, 5),
    ]

    # Portion Mapping
    # Format: Food Name keys mapped to list of (Portion Name, Weight in grams)
    portions = {
        "White Rice (Cooked)": [("1 Bowl", 150), ("1 Plate", 250), ("1 Cup", 158)],
        "Chapati / Roti": [("1 Roti (Small)", 30), ("1 Roti (Medium)", 40), ("1 Roti (Large)", 50)],
        "Dal (Cooked Lentils)": [("1 Bowl", 150), ("1 Cup", 200)],
        "Curd / Yogurt": [("1 Cup", 200), ("1 Bowl", 150), ("1 Tablespoon", 15)],
        "Banana": [("1 Small", 100), ("1 Medium", 120), ("1 Large", 140)],
        "Apple": [("1 Small", 150), ("1 Medium", 182), ("1 Large", 220)],
        "Boiled Egg": [("1 Egg", 50), ("2 Eggs", 100)],
        "Chicken Breast (Grilled)": [("1 Piece", 100), ("1 Serving", 150)],
        "Oats (Cooked)": [("1 Bowl", 234), ("1 Cup", 234)],
        "Milk (Whole)": [("1 Cup", 244), ("1 Glass", 250)],
    }

    print("Checking existing data...")
    existing_count = db.query(FoodItem).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} food items. Skipping population.")
        # Optional: Setup logic to update/overwrite if needed, but safe default is skip
        return

    print("Populating food items...")
    
    for fname, cal, prot, carb, fat, sug in foods:
        food = FoodItem(
            name=fname,
            calories_100g=cal,
            protein_100g=prot,
            carbs_100g=carb,
            fat_100g=fat,
            sugar_100g=sug
        )
        db.add(food)
        db.flush() # flush to get the ID

        # Add portions
        if fname in portions:
            for pname, weight in portions[fname]:
                portion = PortionSize(
                    food_id=food.id,
                    portion_name=pname,
                    weight_g=weight
                )
                db.add(portion)
    
    db.commit()
    print("Database populated successfully!")

def main():
    Base.metadata.create_all(bind=engine) # Ensure tables exist
    db = SessionLocal()
    try:
        populate_food_data(db)
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
