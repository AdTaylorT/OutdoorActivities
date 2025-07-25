from typing import Any
from numpy import isnan

import pgeocode as pg

from errors.not_found_error import NotFoundError

class GeoCode():
    nomi=None

    def __init__(self, country_code='US'):
        self.nomi = pg.Nominatim(country_code)

    def fuzzy_name_lookup(self, city: str, state='Virginia') -> tuple[Any, Any]:
        """
        find lat/long based on city name, with a filter on state, default to Virginia

        returns a tuple of lat and lon
        """
        city = city.capitalize().strip()

        query = self.nomi.query_location(name=city, fuzzy_threshold=70)
        # Keep rows where state_name is 'Virginia'
        if len(state) == 2:
            state = state.upper().strip()
            query = query[query['state_code'] == state]
        else:
            state = state.capitalize().strip()
            query = query[query['state_name'] == state]

        if query.empty:
            print(f"City {city} not found in State {state}.")
            raise NotFoundError("City not found.")

        return (query['latitude'].values[0], query['longitude'].values[0])

    def zipcode_lookup(self, zipcode: str) -> tuple[Any, Any]:
        """
        get the lat and long for a given zipcode

        returns a tuple of lat and lon
        """
        #zipcode = zipcode.strip()
        if not zipcode.isdigit() or len(zipcode) != 5:
            print(f"Invalid zip code: {zipcode}. It should be a 5-digit number.")
            raise ValueError("Zip code must be a 5-digit number.")

        query = self.nomi.query_postal_code(codes=zipcode)
        if query is None or query.empty or isnan(query['latitude']):
            print(f"Zip code {zipcode} not found.")
            raise NotFoundError("Zip code not found.")

        return (query['latitude'], query['longitude'])

if __name__ == "__main__":
    geo = GeoCode()
    lu1 = geo.fuzzy_name_lookup('Vienna')
    lu2 = geo.zipcode_lookup('22314')
