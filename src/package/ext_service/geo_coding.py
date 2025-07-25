from typing import Any
from numpy import isnan

import pgeocode as pg

from errors.not_found_error import NotFoundError

class GeoCode():
    nomi=None

    def __init__(self, country_code='US'):
        self.nomi = pg.Nominatim(country_code)

    def fuzzy_name_lookup(self, city: str, state='Virginia'):
        city = city.capitalize().strip()
        state = state.capitalize().strip()

        query = self.nomi.query_location(name=city, fuzzy_threshold=70)
        # Keep rows where state_name is 'Virginia'
        if len(state) == 2:
            query = query[query['state_code'] == state]
        else:
            query = query[query['state_name'] == state]

        if query.empty:
            print(f"City {city} not found in State {state}.")
            raise NotFoundError("City not found.")

        data = { 'lat': query['latitude'].values[0], 'lon': query['longitude'].values[0] }
        return data

    def zipcode_lookup(self, zipcode) -> dict[str, Any]:
        """
        get the lat and long for a given zipcode

        returns a dict{'lat':np_float64, 'lon':np_float64}
        """
        #zipcode = zipcode.strip()
        if not zipcode.isdigit() or len(zipcode) != 5:
            print(f"Invalid zip code: {zipcode}. It should be a 5-digit number.")
            raise ValueError("Zip code must be a 5-digit number.")

        query = self.nomi.query_postal_code(codes=zipcode)
        if query is None or query.empty or isnan(query['latitude']):
            print(f"Zip code {zipcode} not found.")
            raise NotFoundError("Zip code not found.")

        return { 'lat':  query['latitude'], 'lon': query['longitude'] }

if __name__ == "__main__":
    geo = GeoCode()
    lu1 = geo.fuzzy_name_lookup('Vienna')
    lu2 = geo.zipcode_lookup('22314')

    print(f"Fuzzy name lookup: {lu1}")
    print(f"Zip code lookup: {lu2}")
