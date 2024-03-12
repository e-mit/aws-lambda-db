from datetime import datetime

from sqlmodel import SQLModel, create_engine, select

from sql_model import CarbonIntensity, CarbonIntensityTable

engine = create_engine("sqlite:///database.db")

# Create database and/or table(s) if not already existing:
SQLModel.metadata.create_all(engine)

carb = CarbonIntensity(rating="high", forecast=10, actual=400,
                       time=datetime.now())

CarbonIntensityTable.add_from_db_model(engine, carb)

statement = select(CarbonIntensityTable).where(
                   CarbonIntensityTable.rating == "high")
carb2 = CarbonIntensityTable.read_first(engine, statement)
print(carb)
print(carb2)
