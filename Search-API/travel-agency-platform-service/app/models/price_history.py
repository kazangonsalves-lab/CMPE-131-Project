from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Float, DateTime
from app.core.database import Base


class PriceHistory(Base):
    __tablename__ = "Price_History"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin_sky_id = Column(String, nullable=False, index=True)
    destination_sky_id = Column(String, nullable=False, index=True)
    airline_code = Column(String, nullable=True, index=True)
    departure_date = Column(Date, nullable=False, index=True)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")