import riak
from riak.datatypes import Counter
from django.conf import settings
from _datetime import datetime
import isbnlib
import msgpack
from app_search.helpers.date_helper import DateHelper
from app_search.helpers.solr_helper import SolrHelper

class Manifestation:
    CounterBucketName = "manifestations"

    def __init__(self, meta = None, key = None, bucket = None, riak_obj = None):
        self.meta = meta
        self.key = key
        self.bucket = bucket
        self.client = riak.RiakClient()
        self.riak_obj = riak_obj

    # TODO: string型のクラスにもっていきたい
    def isbn_normalizer(self, isbn):
        isbn = isbn.replace("-","")
        isbn = isbn.upper()
        if isbnlib.is_isbn10(isbn):
            isbn = isbnlib.to_isbn13(isbn)
            isbn = isbn.replace("-","") #TODO: ハイフンは消したい

        return isbn

    def prepare_stored(self):
        meta = self.meta

        isbn = ""
        issn = ""
        identifiers_ts = []
        creators_ts = []
        publishers_ts = []
        ndc = ""
        ndc_types = ["ndc","ndc9","ndc8"]

        # isbn/issn/identifiers_ts
        for k, v in meta['identifiers'].items():
            if  k.lower() == "isbn":
                print("@@@")
                v = self.isbn_normalizer(v)
                isbn = v

            if  k.lower() == "issn":
                #TODO: issn normalize
                v = v

            identifiers_ts.append("{0}:{1}".format(k, v))

        # creators_ts
        for c in meta['creators']:
            creators_ts.append(c['full_name'])

        # publishers_ts
        for c in meta['publishers']:
            creators_ts.append(c['full_name'])
            creators_ts.append(c['full_name_transcription'])

        # languages　(key lower)
        languages = {}
        if 'languages' in meta:
            for k, v in meta['languages'].items():
                languages[k.lower()] = v.lower()


        # titles
        titles_ts = []
        titles_ts.append(meta['title'])
        if 'title_transcription' in meta:
            titles_ts.append(meta['title_transcription'])
        if 'series_title' in meta:
            titles_ts.append(meta['series_title'])
        if 'series_title_transcription' in meta:
            titles_ts.append(meta['series_title_transcription'])

        meta["languages"] = languages
        meta["isbn"] = isbn
        meta["issn"] = issn

        meta["creators_ja"] = " ".join(creators_ts)
        meta["identifiers_ja"] = " ".join(identifiers_ts)
        meta["publishers_ja"] = " ".join(publishers_ts)
        meta["titles_ja"] = " ".join(titles_ts)

        # pub_date
        pub_date_from = None
        pub_date_to = None
        if meta["pub_date"]:
            df = DateHelper.expand_date(meta["pub_date"])
            dt = DateHelper.expand_date(meta["pub_date"], { "mode": 'to' })

            if df and dt:
                meta["pub_date_from_tdt"] = SolrHelper.date2solrtime(df)
                meta["pub_date_to_tdt"] = SolrHelper.date2solrtime(dt)

        self.meta = meta
        return self.meta

    def store(self):
        print("store")
        update_flag = False
        now_str = SolrHelper.datetime2solrtime(datetime.utcnow())

        if self.key and self.riak_obj:
            if self.riak_obj.exists:
                update_flag = True

        if update_flag:
            # update
            print("update")
            self.riak_obj.data.update(self.meta)
            self.riak_obj.data["updated_at"] = now_str

        else:
            # insert
            # TODO: ほんとうのunique番号の生成方法（現状だと同時アクセス時にconflictする）
            # TODO: 採番クラス用意する。
            counter_bucket = self.client.bucket_type(settings.RIAK["COUNTER_BUCKET_TYPE"]).bucket(settings.RIAK["COUNTER_BUCKET"])
            counter = Counter(counter_bucket, Manifestation.CounterBucketName)
            counter.increment()
            counter.store()
            self.key = str(counter.value)
            print("new record: generate key=%s" % (str(self.key)))

            self.meta["record_identifier"] = self.key

            self.bucket = self.client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(settings.RIAK["STORE_BUCKET"])
            self.riak_obj = self.bucket.new(self.key, self.meta)
            self.riak_obj.data["created_at"] = now_str
            self.riak_obj.data["updated_at"] = now_str
        #
        meta = self.prepare_stored()

        riak_obj = self.riak_obj.store()

        # replicator
        # msgpack

        return riak_obj

