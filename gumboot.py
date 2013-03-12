import feedparser
import hashlib
import json
import sys
import irc.client
from time import sleep, mktime
from datetime import datetime

CONFIG = {}
CACHE_FILE = None
CACHE = set([])

def load_config(filename):
    with open(filename,'r') as f:
        confstr = f.read()
        config = json.loads(confstr) # No validation for now

    global CONFIG
    CONFIG = config

def hashed(s):
    return hashlib.md5(s.encode('UTF-8')).hexdigest()

def read_cache_file(filename):
    try:
        global CACHE_FILE
        global CACHE
        CACHE_FILE = open(filename,'rw')
        for l in CACHE_FILE:
            if not l.strip():
                continue
            cache_entry =l.split()[0]
            CACHE.add(cache_entry)
    except IOError: # no cache file
        CACHE_FILE = open(filename,'w')
        CACHE_FILE.flush()
        return
    except:
        print 'Malformed cache file'
        sys.exit(1)

    CACHE_FILE.close() # use r+ ?
    CACHE_FILE = open(filename,'a')


def seen_before(entry):
    return hashed(entry.title) in CACHE

def add_to_cache_file(entry): # only add to cache file after successfully sent to IRC
    global CACHE_FILE
    he = hashed(entry.title)
    if he not in CACHE:
        CACHE_FILE.write('%s %s\n' % (he, entry.title.encode('UTF-8')))
        CACHE_FILE.flush()
        CACHE.add(he)

def connect_and_join(client):
    connection = client.server().connect(CONFIG['irc_server'], CONFIG['irc_port'], CONFIG['irc_nick'])
    chan = CONFIG['irc_channel']
    sleep(10)
    connection.join(chan)
    connection.privmsg(chan, 'Hello from Gumboot')
    return connection

def dance(connection):
    rss_url = CONFIG['rss_url']
    feed = feedparser.parse(rss_url)
    chan = CONFIG['irc_channel']
    notifiers = ' '.join([nick for nick in CONFIG['nicks']])

    for ent in  feed['entries'].__reversed__():
        if not seen_before(ent):
            formatted_time = str(datetime.fromtimestamp(mktime(ent.updated_parsed)))
            connection.privmsg(chan, '%s : %s %s (%s)' % (notifiers, ent.title, ent.links[0].href, formatted_time))
            add_to_cache_file(ent)
            sleep(0.4)

if __name__ == '__main__':
    if len(sys.argv) != 3 or '--help' in sys.argv or 'help' in sys.argv or '-h' in sys.argv:
        print 'Usage: %s <config_file> <title_cache_file>' % sys.argv[0]
        print '\t<config_file> : JSON encoded config dictionary'
        print '\t<title_cache_file> : A file to store md5sums of titles to avoid duplicates on restart'
        sys.exit(1)
    load_config(sys.argv[1])
    read_cache_file(sys.argv[2])
    client = irc.client.IRC()
    c = connect_and_join(client)
    c.execute_every(CONFIG['poll_interval'], dance, (c,))
    client.process_forever()
