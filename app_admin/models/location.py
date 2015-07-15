import riak
from django.conf import settings
from app_search.helpers.date_helper import DateHelper
from app_search.helpers.solr_helper import SolrHelper
from riak.datatypes import Counter
from _datetime import datetime

class Location(object):
    CounterBucketName = "locations"
    BucketName = "locations"

    def __init__(self, meta = None, key = None, riak_obj = None):
        self.meta = meta
        self.key = key
        self.client = riak.RiakClient()
        self.bucket = self.client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(Location.BucketName)
        self.riak_obj = riak_obj

    @classmethod
    def all(cls):
        client = riak.RiakClient()
        bucket = client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(Location.BucketName)
        list = bucket.get_keys()
        locations = []
        for l in list:
            ll = bucket.get(l)
            locations.append(ll.data)

        return locations

    @classmethod
    def find(cls, pk):
        client = riak.RiakClient()
        bucket = client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(Location.BucketName)

        return bucket.get(pk)

    def store(self):
        print("store")
        update_flag = False
        now_str = SolrHelper.datetime2solrtime(datetime.utcnow())

        if self.key and self.riak_obj:
            if self.riak_obj.exists:
                update_flag = True

        update_flag = False
        if update_flag:
            print("update")

        else:
            # insert
            # TODO: ほんとうのunique番号の生成方法（現状だと同時アクセス時にconflictする）
            # TODO: 採番クラス用意する。
            counter_bucket = self.client.bucket_type(settings.RIAK["COUNTER_BUCKET_TYPE"]).bucket(Location.CounterBucketName)
            #counter_bucket.update_counter()
            counter = Counter(counter_bucket, Location.CounterBucketName)
            counter.increment()
            counter.store()
            self.key = str(counter.value)
            print("new record: generate key=%s" % (str(self.key)))

            self.meta["record_identifier"] = self.key

            self.bucket = self.client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(Location.BucketName)
            self.riak_obj = self.bucket.new(self.key, self.meta)
            self.riak_obj.data["created_at"] = now_str
            self.riak_obj.data["updated_at"] = now_str
        #
        #meta = self.prepare_stored()

        riak_obj = self.riak_obj.store()

        # replicator
        # msgpack

        return riak_obj

