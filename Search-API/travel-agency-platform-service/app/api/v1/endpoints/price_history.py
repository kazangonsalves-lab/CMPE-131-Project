from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rapidapi_client import RapidApiError, get_rapidapi_client
from app.schemas.price_history import (
    InsufficientDataResponse,
    PriceComparisonResponse,
    PriceHistoryResponse,
    PriceRangeResponse,
    PriceSnapshotSchema,
)
from app.services.price_history_service import (
    PriceHistoryService,
    extract_calendar_prices,
)
from app.services.rapidapi_service import RapidApiService

router = APIRouter(prefix="/flights", tags=["price history"])


def get_rapidapi_service() -> RapidApiService:
    return RapidApiService(get_rapidapi_client())


def get_price_history_service(db: Session = Depends(get_db)) -> PriceHistoryService:
    return PriceHistoryService(db)


# ─── Existing live-data endpoints ────────────────────────────────────────────

@router.get("/price-calendar", summary="Get oneway price calendar for a route")
async def get_price_calendar(
    origin_sky_id: str = Query(..., description="Origin city/airport code, e.g. LOND, SFO"),
    destination_sky_id: str = Query(..., description="Destination city/airport code, e.g. NYCA, CDG"),
    from_date: str = Query(..., description="Departure date, format: YYYY-MM-DD"),
    market: str = Query("US"),
    currency: str = Query("USD"),
    service: RapidApiService = Depends(get_rapidapi_service),
    history_service: PriceHistoryService = Depends(get_price_history_service),
):
    """
    Returns a calendar of prices for a oneway route across a range of dates.
    Each price point is automatically stored for historical trend tracking.
    """
    try:
        result = service.get_price_calendar(
            origin_sky_id=origin_sky_id,
            destination_sky_id=destination_sky_id,
            from_date=from_date,
            market=market,
            currency=currency,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    records = extract_calendar_prices(result, origin_sky_id, destination_sky_id, currency)
    if records:
        history_service.record_many(records)

    return result


@router.get("/price-calendar-return", summary="Get return trip price calendar for a route")
async def get_price_calendar_return(
    origin_sky_id: str = Query(..., description="Origin city/airport code, e.g. LOND"),
    destination_sky_id: str = Query(..., description="Destination city/airport code, e.g. NYCA"),
    from_date: str = Query(..., description="Outbound departure date, format: YYYY-MM-DD"),
    return_from_date: str = Query(..., description="Return departure date, format: YYYY-MM-DD"),
    market: str = Query("US"),
    currency: str = Query("USD"),
    service: RapidApiService = Depends(get_rapidapi_service),
):
    """
    Returns a calendar of prices for a return trip across a range of date combinations.
    Use this to power a price trend line chart for round trips.
    """
    try:
        return service.get_price_calendar_return(
            origin_sky_id=origin_sky_id,
            destination_sky_id=destination_sky_id,
            from_date=from_date,
            return_from_date=return_from_date,
            market=market,
            currency=currency,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.get("/cheapest-oneway", summary="Get cheapest oneway prices for a month")
async def get_cheapest_oneway(
    origin_sky_id: str = Query(..., description="Origin city/airport code, e.g. LOND"),
    destination_sky_id: str = Query(..., description="Destination city/airport code, e.g. NYCA"),
    month: str = Query(..., description="Target month, format: YYYY-MM"),
    market: str = Query("US"),
    currency: str = Query("USD"),
    service: RapidApiService = Depends(get_rapidapi_service),
):
    """
    Returns the cheapest available oneway prices for each day in the given month.
    Use the lowest price entry to display the 'best time to book' indicator.
    """
    try:
        return service.get_cheapest_oneway(
            origin_sky_id=origin_sky_id,
            destination_sky_id=destination_sky_id,
            month=month,
            market=market,
            currency=currency,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


# ─── Historical data endpoints ────────────────────────────────────────────────

@router.get(
    "/price-history",
    response_model=PriceHistoryResponse,
    summary="Get stored historical price snapshots for a route",
)
async def get_price_history(
    origin_sky_id: str = Query(..., description="Origin code, e.g. SFO"),
    destination_sky_id: str = Query(..., description="Destination code, e.g. CDG"),
    departure_date: date = Query(..., description="Flight departure date, format: YYYY-MM-DD"),
    airline_code: Optional[str] = Query(None, description="Filter by airline code, e.g. AA"),
    from_recorded: Optional[date] = Query(None, description="Include snapshots recorded on or after this date"),
    to_recorded: Optional[date] = Query(None, description="Include snapshots recorded on or before this date"),
    history_service: PriceHistoryService = Depends(get_price_history_service),
):
    """
    Returns all stored price snapshots for a route and departure date.
    Snapshots are recorded automatically when /price-calendar or /flights/search is called.
    Use the returned data to draw a price-over-time line chart.
    """
    rows = history_service.get_history(
        origin=origin_sky_id,
        destination=destination_sky_id,
        departure_date=departure_date,
        airline_code=airline_code,
        from_recorded=from_recorded,
        to_recorded=to_recorded,
    )
    return PriceHistoryResponse(
        origin=origin_sky_id,
        destination=destination_sky_id,
        departure_date=departure_date,
        airline_code=airline_code,
        snapshots=[
            PriceSnapshotSchema(recorded_at=r.recorded_at, price=r.price, currency=r.currency)
            for r in rows
        ],
        data_points=len(rows),
    )


@router.get(
    "/price-range",
    response_model=PriceRangeResponse,
    summary="Get lowest and highest recorded prices for a route",
)
async def get_price_range(
    origin_sky_id: str = Query(..., description="Origin code, e.g. SFO"),
    destination_sky_id: str = Query(..., description="Destination code, e.g. CDG"),
    departure_date: date = Query(..., description="Flight departure date, format: YYYY-MM-DD"),
    from_recorded: Optional[date] = Query(None, description="Range start date"),
    to_recorded: Optional[date] = Query(None, description="Range end date"),
    history_service: PriceHistoryService = Depends(get_price_history_service),
):
    """
    Returns the minimum (best time to book) and maximum (worst time to book) recorded
    prices for a route within an optional date range, along with the date each occurred.
    Returns 404 if no price data has been recorded yet.
    """
    result, count = history_service.get_price_range(
        origin=origin_sky_id,
        destination=destination_sky_id,
        departure_date=departure_date,
        from_recorded=from_recorded,
        to_recorded=to_recorded,
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No price data found for this route and date range. Try calling /price-calendar first.",
        )
    return PriceRangeResponse(
        origin=origin_sky_id,
        destination=destination_sky_id,
        departure_date=departure_date,
        **result,
    )


@router.get(
    "/price-comparison",
    summary="Compare current price to historical average for a route and airline",
)
async def get_price_comparison(
    origin_sky_id: str = Query(..., description="Origin code, e.g. SFO"),
    destination_sky_id: str = Query(..., description="Destination code, e.g. CDG"),
    departure_date: date = Query(..., description="Flight departure date, format: YYYY-MM-DD"),
    airline_code: str = Query(..., description="Airline code to compare, e.g. AA"),
    history_service: PriceHistoryService = Depends(get_price_history_service),
):
    """
    Compares the most recently recorded price against the historical average for a specific
    airline on a route. Returns the percentage difference so users can judge if it is a
    good deal. Returns an 'Insufficient data' message if fewer than 2 snapshots exist.
    Only data for the requested airline is used in the average calculation.
    """
    result, count = history_service.get_comparison(
        origin=origin_sky_id,
        destination=destination_sky_id,
        departure_date=departure_date,
        airline_code=airline_code,
    )
    if result is None:
        return InsufficientDataResponse(
            message="Insufficient data for this time period",
            data_points=count,
        )
    return PriceComparisonResponse(
        origin=origin_sky_id,
        destination=destination_sky_id,
        departure_date=departure_date,
        airline_code=airline_code,
        data_points=count,
        **result,
    )