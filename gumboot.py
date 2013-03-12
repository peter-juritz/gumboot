import feedparser
import hashlib
import json
import sys

CONFIG = {}
CACHE_FILE = None
CACHE = set([])

def load_config(filename):
    with open(filename) as f:
        confstr = f.read()
        config = json.loads(confstr) # No validation for now

    global CONFIG
    CONFIG = config
    global CACHE_FILE

def hashed(s):
    return hashlib.md5(s).hexdigest()

def read_cache_file(filename):
    global CACHE_FILE
    global CACHE
    CACHE_FILE = open(filename,'rw')
    for l in CACHE_FILE:
        if not l.strip():
            continue
        cache_entry = hashed(l.split()[0])
        CACHE.add(cache_entry)

def seen_before(entry):
    return hashed(entry.title) in CACHE

def add_to_cache_file(entry): # only add to cache file after successfully sent to IRC
    he = hashed(entry.title)
    CACHE_FILE.write('%s %s\n' % (he, entry.title))
    CACHE.add(he)

def dance():
    rss_url = CONFIG['rss_url']
    feed = feedparser.parse(rss_url)

    for ent in  feed['entries']:
        print ent.title, hashlib.md5(ent.title).hexdigest()
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: %s <config_file> <title_cache_file>' % sys.argv[0]
        print '\t<config_file> : JSON encoded config dictionary'
        print '\t<title_cache_file> : A file to store md5sums of titles to avoid duplicates on restart'
        sys.exit(1)
    load_config(sys.argv[1])
    read_cache_file(sys.argv[2])
    dance()
