import sys, platform
import traceback
from django.core.management.base import BaseCommand
import riak
import pprint

class Command(BaseCommand):
  help = "Riak Tools"

  def print_usage(self):
    print("usage: manage.py riak_tools action bucket_type_name bucket_name")

  def add_arguments(self, parser):
    parser.add_argument('action', type=str)
    parser.add_argument('bucket_type_name', type=str)
    parser.add_argument('bucket_name', type=str)

  def handle(self, *args, **options):

    available_actions = ["delete", "reindex", "select"]

    if options['action'] == None or options['bucket_type_name'] == None or options['bucket_name'] == None:
      print("argument error. invalid size")
      self.print_usage()
      return

    print('riak tools: start')

    action = options['action']
    if not action in available_actions:
      print("argument error. action delete or reindex or select")
      return

    bucket_type_name = options['bucket_type_name']
    bucket_name = options['bucket_name']

    try:
      client = riak.RiakClient()
      bucket = client.bucket_type(bucket_type_name).bucket(bucket_name)

      if action == "delete":
        keys = bucket.get_keys()
        key_size = len(keys)
        print("key size={0}".format(key_size))
        objs = bucket.multiget(keys)
        for i, obj in enumerate(objs):
          obj.delete()
          print("{0}/{1}".format(i+1, key_size))

      elif action == "reindex":
        keys = bucket.get_keys()
        key_size = len(keys)
        print("key size=".format(len(keys)))
        objs = bucket.multiget(keys)
        for i, obj in enumerate(objs):
          obj.store()
          print("{0}/{1}".format(i+1, key_size))

      elif action == "select":
        pp = pprint.PrettyPrinter(indent=2)
        keys = bucket.get_keys()
        print("key size=".format(len(keys)))
        objs = bucket.multiget(keys)
        for i, obj in enumerate(objs):
          pp.pprint(obj.data)

      elif action == "export":
        cnt = 0
        data_directory = "./"

        keys = client.stream_keys(bucket)
        for key in keys:
          obj = bucket.get(key)

          if (obj.encoded_data is not None):
            f = open(data_directory + key[0], 'w')
            f.write(obj.encoded_data)
            f.close()

            cnt = cnt + 1

          if (cnt % 500) == 0:
            print('{} 件 実行'.format(cnt))

        keys.close()
        print('{} 件 完了'.format(cnt))

      elif action == "import":
        pass

    except ConnectionRefusedError as err:
      print("Riak Connection error. please check riak instance")
      print("Message:{}".format(err))
    except riak.RiakError as err:
      print("Riak error. please check message from riak")
      print("Message:{}".format(err))

    print("riak tools: completed.")
