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
        locale: str = "US",
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
            host="skyscanner-flights-travel-api.p.rapidapi.com",
            path="api/v1/attractions/search",
            params=querystring,
        )

    def search_hotels(
        self,
        dest_id: str,
        checkin_date: str,
        checkout_date: str,
        adults_number: int,
        room_number: int,
        locale: str,
        filter_by_currency: str,
    ):
        querystring = {
            "entityId": dest_id,
            "checkIn": checkin_date,
            "checkOut": checkout_date,
            "adults": str(adults_number),
            "rooms": str(room_number),
            "market": locale,
            "currency": filter_by_currency,
        }

        return self._get(
            host="skyscanner-flights-travel-api.p.rapidapi.com",
            path="hotels/searchHotels",
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
            host="skyscanner-flights-travel-api.p.rapidapi.com",
            path="api/v1/cars/searchCarRentals",
            params=querystring,
        )

    def search_flights(
        self,
        origin_sky_id: str,
        origin_entity_id: str,
        destination_sky_id: str,
        destination_entity_id: str,
        date: str,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        cabin_class: str = "economy",
        currency: str = "USD",
        market: str = "US",
        return_date: str | None = None,
    ):
        querystring = {
            "originSkyId": origin_sky_id,
            "originEntityId": origin_entity_id,
            "destinationSkyId": destination_sky_id,
            "destinationEntityId": destination_entity_id,
            "date": date,
            "adults": str(adults),
            "childrens": str(children),
            "infants": str(infants),
            "cabinClass": cabin_class,
            "currency": currency,
            "market": market,
        }

        if return_date:
            querystring["return_date"] = return_date

        return self._get(
            host="skyscanner-flights-travel-api.p.rapidapi.com",
            path="flights/searchFlights",
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
        except Exception as error:
            raise RapidApiError(500, f"Unexpected error: {type(error).__name__}: {str(error)}")


@lru_cache(maxsize=1)
def get_rapidapi_client() -> RapidApiClient:
    settings = get_settings()
    if not settings.rapidapi_key:
        raise RapidApiError(500, "RAPIDAPI_KEY is not configured.")

    return RapidApiClient(api_key=settings.rapidapi_key)