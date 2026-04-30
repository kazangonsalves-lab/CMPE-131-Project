from app.core.rapidapi_client import RapidApiClient

class RapidApiService:
    def __init__(self, rapidapi_client: RapidApiClient) -> None:
        self.rapidapi = rapidapi_client

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
        return self.rapidapi.search_attractions(
            start_date=start_date,
            end_date=end_date,
            dest_id=dest_id,
            locale=locale,
            page_number=page_number,
            currency=currency,
            order_by=order_by,
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
        return self.rapidapi.search_hotels(
            dest_id=dest_id,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            adults_number=adults_number,
            room_number=room_number,
            locale=locale,
            filter_by_currency=filter_by_currency,
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
        return self.rapidapi.search_flights(
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

    def search_rental_cars(
        self,
        pick_up_date: str,
        drop_off_date: str,
        pick_up_time: str,
        drop_off_time: str,
    ):
        return self.rapidapi.search_rental_cars(
            pick_up_date=pick_up_date,
            drop_off_date=drop_off_date,
            pick_up_time=pick_up_time,
            drop_off_time=drop_off_time,
        )