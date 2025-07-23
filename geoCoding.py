import pgeocode as pg
import pandas as pd
from NotFoundError import NotFoundError

class myGeoCode():
    nomi=None

    def __init__(self, country_code='US'):
        self.nomi = pg.Nominatim(country_code)

    def fuzzy_name_lookup(self, city, state='Virginia'):
        city = city.capitalize().strip()
        state = state.lower().strip()

        query = self.nomi.query_location(name=city, fuzzy_threshold=70)        
        # Keep rows where state_name is 'Virginia'
        if len(state) == 2:
            query = query[str(query['state_code']).lower() == state]
        else:
            query = query[str(query['state_name']).lower() == state]

        if query.empty:
            print(f"City {city} not found in State {state}.")
            raise NotFoundError("City not found.")
        
        data = { 'lat': query['latitude'].values[0], 'lon': query['longitude'].values[0] }
        return data
    
    def zipcode_lookup(self, zipcode):
        zipcode = zipcode.strip()
        if not zipcode.isdigit() or len(zipcode) != 5:
            print(f"Invalid zip code: {zipcode}. It should be a 5-digit number.")
            raise ValueError("Zip code must be a 5-digit number.")
        
        q2 = self.nomi.query_postal_code(codes=zipcode)
        q2.to_dict()

        if q2.empty:
            print(f"Zip code {zipcode} not found.")
            raise NotFoundError("Zip code not found.")

        data2 = { 'lat': q2['latitude'], 'lon': q2['longitude'] }
        return data2

if __name__ == "__main__":
    geo = myGeoCode()
    lu1 = geo.fuzzy_name_lookup('Vienna')
    lu2 = geo.zipcode_lookup('22314')

    print(f"Fuzzy name lookup: {lu1}")
    print(f"Zip code lookup: {lu2}")
