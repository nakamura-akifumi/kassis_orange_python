import sys
import gc
import time

TIMES = 100000
print(sys.version)
MAJOR_VER = float(sys.version[0:3])

if MAJOR_VER >= 2.4:
    print("PATTERN 1")
    start = time.time()
    buf = ''
    for i in range(0, TIMES):
        buf += "a"
    print (time.time() - start)
    del(buf)
    gc.collect()

print("PATTERN 2")
start = time.time()
L = []
for i in range(0, TIMES):
    L.append("a")
buf = ''.join(L)
print (time.time() - start)
del(L, buf)
gc.collect()

if MAJOR_VER >= 2.4:
    import mmap
    print("PATTERN 3 (slice)")
    start = time.time()
    if MAJOR_VER < 2.6:
        map_ = mmap.mmap(-1, TIMES, mmap.MAP_ANONYMOUS)
    else:
        map_ = mmap.mmap(-1, TIMES)

    for i in range(0, TIMES):
        map_[i] = "a"
    buf = map_.read(TIMES)
    map_.flush()
    map_.close()
    print(time.time() - start)
    del(map_, buf)
    gc.collect()

    import mmap
    print("PATTERN 3 (write)")
    start = time.time()
    if MAJOR_VER < 2.6:
        map_ = mmap.mmap(-1, TIMES, mmap.MAP_ANONYMOUS)
    else:
        map_ = mmap.mmap(-1, TIMES)

    for i in xrange(0, TIMES):
        map_.write("a")
    length = map_.tell()
    map_.seek(0)
    buf = map_.read(length)
    map_.flush()
    map_.close()
    print(time.time() - start)
    del(map_, buf, length)
    gc.collect()

import StringIO
print("PATTERN 4")
start = time.time()
io = StringIO.StringIO()
for i in xrange(0, TIMES):
    io.write('a')
buf = io.getvalue()
io.close()
print(time.time() - start)
del(io, buf)
gc.collect()

import cStringIO
print("PATTERN 5")
start = time.time()
io = cStringIO.StringIO()
for i in xrange(0, TIMES):
    io.write('a')
buf = io.getvalue()
io.close()
print (time.time() - start)
del(io, buf)
gc.collect()


if MAJOR_VER >= 2.6:
    import io
    print("PATTERN 6"),
    start = time.time()
    io_ = io.StringIO()
    for i in xrange(0, TIMES):
        io_.write(u'a')
    buf = io_.getvalue()
    io_.close()
    print(time.time() - start)
    del(io_, buf)
    gc.collect()
