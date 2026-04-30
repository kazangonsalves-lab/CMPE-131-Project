from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory

MIN_COMPARISON_POINTS = 2


def extract_calendar_prices(
    data: dict,
    origin: str,
    destination: str,
    currency: str,
) -> list[dict]:
    """Extract per-day price records from a Skyscanner price-calendar response."""
    records = []
    try:
        days = data.get("data", {}).get("flights", {}).get("days", [])
        now = datetime.utcnow()
        for day_data in days:
            day_str = day_data.get("day")
            price = day_data.get("price")
            if day_str and price is not None:
                try:
                    records.append({
                        "origin_sky_id": origin,
                        "destination_sky_id": destination,
                        "departure_date": date.fromisoformat(day_str),
                        "recorded_at": now,
                        "price": float(price),
                        "currency": currency,
                    })
                except (ValueError, TypeError):
                    continue
    except Exception:
        pass
    return records


def extract_flight_prices(
    data: dict,
    origin: str,
    destination: str,
    departure_date_str: str,
    currency: str,
) -> list[dict]:
    """Extract per-itinerary price records from a Skyscanner flight-search response."""
    records = []
    try:
        itineraries = data.get("data", {}).get("itineraries", [])
        now = datetime.utcnow()
        dep_date = date.fromisoformat(departure_date_str)
        for itin in itineraries:
            price = itin.get("price", {}).get("raw")
            airline_code = None
            try:
                legs = itin.get("legs", [])
                if legs:
                    marketing = legs[0].get("carriers", {}).get("marketing", [])
                    if marketing:
                        airline_code = marketing[0].get("alternateId")
            except Exception:
                pass
            if price is not None:
                records.append({
                    "origin_sky_id": origin,
                    "destination_sky_id": destination,
                    "departure_date": dep_date,
                    "recorded_at": now,
                    "price": float(price),
                    "airline_code": airline_code,
                    "currency": currency,
                })
    except Exception:
        pass
    return records


class PriceHistoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record_many(self, records: list[dict]) -> None:
        for r in records:
            self.db.add(PriceHistory(**r))
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()

    def get_history(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        airline_code: Optional[str] = None,
        from_recorded: Optional[date] = None,
        to_recorded: Optional[date] = None,
    ) -> list[PriceHistory]:
        q = self.db.query(PriceHistory).filter(
            PriceHistory.origin_sky_id == origin,
            PriceHistory.destination_sky_id == destination,
            PriceHistory.departure_date == departure_date,
        )
        if airline_code:
            q = q.filter(PriceHistory.airline_code == airline_code)
        if from_recorded:
            q = q.filter(PriceHistory.recorded_at >= datetime(from_recorded.year, from_recorded.month, from_recorded.day))
        if to_recorded:
            q = q.filter(PriceHistory.recorded_at <= datetime(to_recorded.year, to_recorded.month, to_recorded.day, 23, 59, 59))
        return q.order_by(PriceHistory.recorded_at).all()

    def get_price_range(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        from_recorded: Optional[date] = None,
        to_recorded: Optional[date] = None,
    ) -> tuple[Optional[dict], int]:
        rows = self.get_history(origin, destination, departure_date, from_recorded=from_recorded, to_recorded=to_recorded)
        if not rows:
            return None, 0
        min_row = min(rows, key=lambda r: r.price)
        max_row = max(rows, key=lambda r: r.price)
        return {
            "min_price": min_row.price,
            "min_recorded_at": min_row.recorded_at,
            "max_price": max_row.price,
            "max_recorded_at": max_row.recorded_at,
            "currency": rows[0].currency,
        }, len(rows)

    def get_comparison(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        airline_code: str,
    ) -> tuple[Optional[dict], int]:
        rows = self.get_history(origin, destination, departure_date, airline_code=airline_code)
        if len(rows) < MIN_COMPARISON_POINTS:
            return None, len(rows)
        current = rows[-1].price
        avg = sum(r.price for r in rows) / len(rows)
        diff = current - avg
        diff_pct = (diff / avg) * 100 if avg else 0
        return {
            "current_price": current,
            "historical_average": round(avg, 2),
            "difference": round(diff, 2),
            "difference_pct": round(diff_pct, 2),
            "currency": rows[-1].currency,
        }, len(rows)