from pymongo import MongoClient
from bson.codec_options import CodecOptions

from globals_ import env

codec_options = CodecOptions(tz_aware=True)


class CustomMongoClient(MongoClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __del__(self):
        try:
            self.close()
        except ImportError:
            pass


class DBConnection(CustomMongoClient):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class AppDB(DBConnection):

    def __new__(cls):
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        if not hasattr(self, "_app_initialized"):
            super().__init__(env.APP_MONGO_URL, maxPoolSize=1)
            self._database = env.APP_DB_NAME
            self.IOCs = self[self._database].get_collection(
                "iocs", codec_options
            )
            self.IOCSources = self[self._database].get_collection(
                "ioc_sources", codec_options
            )
            self.GeoLocation = self[self._database].get_collection(
                "location", codec_options
            )
            self.ASNRecords = self[self._database].get_collection(
                "asn", codec_options
            )
            self.Networks = self[self._database].get_collection(
                "network", codec_options
            )
            self.Organizations = self[self._database].get_collection(
                "organization", codec_options
            )
            
