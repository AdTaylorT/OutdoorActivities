import pgeocode as pg
import pandas as pd 

class myGeoCode():
    nomi=None

    def __init__(self, country_code='US'):
        self.nomi = pg.Nominatim(country_code)

    def fuzzy_name_lookup(self, name, state='Virginia'):        
        q2 = self.nomi.query_location(name=name, fuzzy_threshold=70)
        # Keep rows where state_name is 'Virginia'
        q2 = q2[q2['state_name'] == state]

        data = { 'lat': q2['latitude'].values[0], 'lon': q2['longitude'].values[0] }
        return data
    
    def zipcode_lookup(self, zipcode):
        q2 = self.nomi.query_postal_code(codes=zipcode)
        q2.to_dict()

        if q2.empty:
            print(f"Zip code {zipcode} not found.")
            # TODO return some default value or raise an exception?
            return pd.DataFrame(columns=['latitude', 'longitude'])

        data2 = { 'lat': q2['latitude'], 'lon': q2['longitude'] }
        return data2

if __name__ == "__main__":
    geo = myGeoCode()
    lu1 = geo.fuzzy_name_lookup('Vienna')
    lu2 = geo.zipcode_lookup('22314')

    #data = { 'lat': lu1['latitude'].values[0], 'lon': lu1['longitude'].values[0] }
    #data2 = { 'lat': lu2['latitude'], 'lon': lu2['longitude'] }
    print(f"Fuzzy name lookup: {lu1}")
    print(f"Zip code lookup: {lu2}")
