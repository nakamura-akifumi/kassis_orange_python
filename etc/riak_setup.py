#!/usr/bin/env python

import shlex, subprocess
import riak


#cmd = ["sed -e 's/search = off/search = on/' -i.back app/riak/etc/riak.conf"
#riak restart

cmd = ["riak-admin", "bucket-type", "create", "counters", '{"props":{"datatype":"counter"}}']
subprocess.call(cmd)

cmd = ["riak-admin", "bucket-type", "activate", "counters"]
subprocess.call(cmd)

client = riak.RiakClient()
f = open('etc/solr/_yz_default.xml')
content = f.read()
f.close()
schema_name = '_yz_default'
client.create_search_schema(schema_name, content)
client.create_search_index('kassis_index','_yz_default')

cmd = ["riak-admin", "bucket-type", "create", "kassis_index", '{"props":{"search_index":"kassis_index"}}']
subprocess.call(cmd)

cmd = ["riak-admin", "bucket-type", "activate", "kassis_index"]
subprocess.call(cmd)
