import geoip2
from geoip2.database import Reader

from utils.paths import BASE_DIR


def get_country_from_ip(ip_address):
    reader = Reader(BASE_DIR + "\\utils\\GeoLite2-Country.mmdb")

    try:
        response = reader.country(ip_address)
        country_name = response.country.name
        return country_name
    except geoip2.errors.AddressNotFoundError:
        return None
