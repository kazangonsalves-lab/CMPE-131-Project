from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rapidapi_client import RapidApiError, get_rapidapi_client
from app.services.price_history_service import PriceHistoryService, extract_flight_prices
from app.services.rapidapi_service import RapidApiService

router = APIRouter(prefix="", tags=["rapidapi"])


def get_rapidapi_service() -> RapidApiService:
    return RapidApiService(get_rapidapi_client())


@router.get("/attractions/search")
async def search_attractions(
    start_date: str = Query(..., description="Format: YYYY-MM-DD"),
    end_date: str = Query(..., description="Format: YYYY-MM-DD"),
    dest_id: str = Query(..., description="Destination ID, e.g. 20088325"),
    locale: str = Query("en-us"),
    page_number: int = Query(0, ge=0),
    currency: str = Query("USD"),
    order_by: str = Query("attr_book_score"),
    service: RapidApiService = Depends(get_rapidapi_service),
):
    try:
        return service.search_attractions(
            start_date=start_date,
            end_date=end_date,
            dest_id=dest_id,
            locale=locale,
            page_number=page_number,
            currency=currency,
            order_by=order_by,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.get("/hotels/search")
async def search_hotels(
    dest_id: str = Query(..., description="Example: 27539733"),
    checkin_date: str = Query(..., description="Format: YYYY-MM-DD"),
    checkout_date: str = Query(..., description="Format: YYYY-MM-DD"),
    adults_number: int = Query(2, ge=1),
    room_number: int = Query(1, ge=1),
    locale: str = Query("US", description="Examples: American English = en-us, British English = en-gb"),
    filter_by_currency: str = Query("USD", description="Examples: US dollars: USD, UAE Dirham = AED"),
    service: RapidApiService = Depends(get_rapidapi_service),
):
    try:
        return service.search_hotels(
            dest_id=dest_id,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            adults_number=adults_number,
            room_number=room_number,
            locale=locale,
            filter_by_currency=filter_by_currency,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.get("/flights/search")
async def search_flights(
    origin_sky_id: str = Query(..., description="Example: SFO"),
    origin_entity_id: str = Query(..., description="Example: 27544008"),
    destination_sky_id: str = Query(..., description="Example: LHR"),
    destination_entity_id: str = Query(..., description="Example: 27544008"),
    date: str = Query(..., description="Format: YYYY-MM-DD"),
    adults: int = Query(1, ge=1),
    children: int = Query(0, ge=0),
    infants: int = Query(0, ge=0),
    cabin_class: str = Query("economy"),
    currency: str = Query("USD"),
    market: str = Query("en-US"),
    return_date: str | None = Query(None, description="Format: YYYY-MM-DD"),
    service: RapidApiService = Depends(get_rapidapi_service),
    db: Session = Depends(get_db),
):
    try:
        result = service.search_flights(
            origin_sky_id=origin_sky_id,
            origin_entity_id=origin_entity_id,
            destination_sky_id=destination_sky_id,
            destination_entity_id=destination_entity_id,
            date=date,
            adults=adults,
            children=children,
            infants=infants,
            cabin_class=cabin_class,
            currency=currency,
            market=market,
            return_date=return_date,
        )
    except RapidApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    records = extract_flight_prices(result, origin_sky_id, destination_sky_id, date, currency)
    if records:
        PriceHistoryService(db).record_many(records)

    return result