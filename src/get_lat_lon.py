import psycopg2
import time
import random
from geopy.geocoders import Nominatim, options
from geopy.adapters import RequestsAdapter
from requests.packages.urllib3.util.retry import Retry

from DubuqueData.src.dubuquedb import DubuqueDB
from DubuqueData.src.errors import SchemaNotSet

retry_strategy = Retry(
    total=10,
    # status_forcelist=[429, 500, 502, 503, 504],
    # method_whitelist=["HEAD", "GET", "OPTIONS"],
    backoff_factor=1
)


class RequestsAdapterMoreRetries(RequestsAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(proxies=options.default_proxies,
                         ssl_context=options.default_ssl_context,
                         pool_connections=10,
                         pool_maxsize=10,
                         max_retries=retry_strategy,
                         pool_block=False)

adapter_factory_new = next(adapter_cls
                           for adapter_cls in (RequestsAdapterMoreRetries,)
                           if adapter_cls.is_available)


class DubuqueGIS(DubuqueDB):
    def __init__(self, user_agent=None, adaptor_factory_new=None, **kwargs):
        self.user_agent = user_agent
        self.geolocator = Nominatim(user_agent=user_agent, adapter_factory=adaptor_factory_new)

        super().__init__(**kwargs)

    def create_lat_lon_table(self, table_name: str) -> None:
        """
        creates new table in database to store lat lon coordinates
        :param table_name:
        :return:
        """
        if not self.check_schema():
            raise SchemaNotSet('schema has not been set')

        self.cursor.execute(f'drop table if exists "{table_name}";')
        self.conn.commit()
        self.cursor.execute(
            f'create table "{table_name}"(parcel_number int,latitude double precision,longitude double precision);')
        self.conn.commit()

    def download_lat_lons(self,
                          lat_lon_table:str,
                          address_table: str,
                          address_column: str,
                          parcel_number_column: str) -> None:

        self.cursor.execute(f'select distinct on ("{parcel_number_column}") "{address_column}", "{parcel_number_column}" from "{address_table}";')
        addresses = self.cursor.fetchall()

        count = 0
        print(len(addresses))
        for addr, parcel_number in addresses:
            print(count)
            addr_tmp = addr.replace('\'', '').strip().split(',')[0]
            addr_full = ','.join([addr_tmp, ' Dubuque, IA'])
            print(addr_full, parcel_number)
            location = self.geolocator.geocode(addr_full)
            if location:
                insert_string = f"({parcel_number}, {location.latitude},{location.longitude})"
            else:
                insert_string = f"({parcel_number}, 0.0, 0.0)"
            count += 1

            insert_expression = f'INSERT INTO "{lat_lon_table}" VALUES {insert_string};'
            print(insert_expression)

            self.cursor.execute(insert_expression)
            self.conn.commit()
