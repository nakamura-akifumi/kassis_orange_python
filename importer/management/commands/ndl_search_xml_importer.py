import sys, platform
import traceback
from django.core.management.base import BaseCommand
import riak
from importer.models import ndl_search_opensearch
from os.path import join, relpath
from glob import glob
from django.conf import settings

class Command(BaseCommand):
  def handle(self, *args, **options):
    print('loader (import from ndl search xml file)')

    client = riak.RiakClient()
    bucket = client.bucket_type(settings.RIAK["STORE_BUCKET_TYPE"]).bucket(settings.RIAK["STORE_BUCKET"])

    # all delete
    keys = bucket.get_keys()
    key_size = len(keys)
    print("delete key size={0}".format(key_size))
    objs = bucket.multiget(keys)
    for i, obj in enumerate(objs):
      obj.delete()
      print("delete {0}/{1}".format(i+1, key_size))

    path = '/Users/nakamura/IdeaProjects/kassis_orange/tmp/'
    files = glob(join(path, '*.xml'))
    for file in files:
      ndl_search_opensearch.NdlHelper.import_from_file(file)


