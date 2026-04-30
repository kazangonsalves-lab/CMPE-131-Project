from functools import lru_cache
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import get_settings


class RapidApiError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class RapidApiClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search_attractions(
        self,
        start_date: str,
        end_date: str,
        dest_id: str,
        locale: str = "en-us",
        page_number: int = 0,
        currency: str = "USD",
        order_by: str = "attr_book_score",
    ):
        querystring = {
            "start_date": start_date,
            "end_date": end_date,
            "locale": locale,
            "page_number": str(page_number),
            "currency": currency,
            "order_by": order_by,
            "dest_id": dest_id,
        }

        return self._get(
            host="booking-com.p.rapidapi.com",
            path="v1/attractions/search",
            params=querystring,
        )

    def search_hotels(
        self,
        page_number: int,
        dest_type: str,
        dest_id: str,
        units: str,
        children_number: int,
        locale: str,
        include_adjacency: bool,
        filter_by_currency: str,
        order_by: str,
        checkin_date: str,
        checkout_date: str,
        room_number: int,
        adults_number: int,
        categories_filter_ids: str | None = None,
        children_ages: str | None = None,
    ):
        querystring = {
            "page_number": str(page_number),
            "dest_type": dest_type,
            "dest_id": dest_id,
            "units": units,
            "locale": locale,
            "include_adjacency": str(include_adjacency).lower(),
            "filter_by_currency": filter_by_currency,
            "order_by": order_by,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "room_number": str(room_number),
            "adults_number": str(adults_number),
        }

        if categories_filter_ids:
            querystring["categories_filter_ids"] = categories_filter_ids

        if children_number is not None and children_number >= 1:
            querystring["children_number"] = str(children_number)
            if children_ages:
                querystring["children_ages"] = children_ages

        return self._get(
            host="booking-com.p.rapidapi.com",
            path="v1/hotels/search",
            params=querystring,
        )

    def search_rental_cars(
        self,
        pick_up_date: str,
        drop_off_date: str,
        pick_up_time: str,
        drop_off_time: str,
    ):
        querystring = {
            "pick_up_latitude": "40.6397018432617",
            "pick_up_longitude": "-73.7791976928711",
            "drop_off_latitude": "40.6397018432617",
            "drop_off_longitude": "-73.7791976928711",
            "pick_up_date": pick_up_date,
            "drop_off_date": drop_off_date,
            "pick_up_time": pick_up_time,
            "drop_off_time": drop_off_time,
            "driver_age": "30",
            "currency_code": "USD",
            "location": "US",
        }
        return self._get(
            host="booking-com15.p.rapidapi.com",
            path="api/v1/cars/searchCarRentals",
            params=querystring,
        )

    def search_flights(
        self,
        depart_date: str,
        from_code: str,
        to_code: str,
        adults: int,
        locale: str = "en-us",
        page_number: int = 0,
        currency: str = "USD",
        order_by: str = "BEST",
        flight_type: str = "ONEWAY",
        cabin_class: str = "ECONOMY",
        children_ages: str | None = None,
        return_date: str | None = None,
    ):
        querystring = {
            "depart_date": depart_date,
            "from_code": from_code,
            "to_code": to_code,
            "adults": str(adults),
            "locale": locale,
            "page_number": str(page_number),
            "currency": currency,
            "order_by": order_by,
            "flight_type": flight_type,
            "cabin_class": cabin_class,
        }

        if children_ages:
            querystring["children_ages"] = children_ages

        if return_date:
            querystring["return_date"] = return_date

        return self._get(
            host="booking-com.p.rapidapi.com",
            path="v1/flights/search",
            params=querystring,
        )

    def _get(self, host: str, path: str, params: dict[str, str]):
        request = Request(
            f"https://{host}/{path}?{urlencode(params)}",
            headers={
                "x-rapidapi-host": host,
                "x-rapidapi-key": self.api_key,
                "Content-Type": "application/json",
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RapidApiError(error.code, detail or str(error)) from error
        except URLError as error:
            raise RapidApiError(500, "Failed to connect to RapidAPI.") from error


@lru_cache(maxsize=1)
def get_rapidapi_client() -> RapidApiClient:
    settings = get_settings()
    if not settings.rapidapi_key:
        raise RapidApiError(500, "RAPIDAPI_KEY is not configured.")

    return RapidApiClient(api_key=settings.rapidapi_key)