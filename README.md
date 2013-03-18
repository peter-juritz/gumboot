gumboot
=======

An IRC bot to relay gumtree RSS feeds to IRC. An example config file is in example_config.json.

Installation
============
Requires the python modules:
* irc
* feedparser
* hgtools (required by irc)


Running
=======
    Usage: gumboot.py <config_file> <title_cache_file>
        <config_file> : JSON encoded config dictionary
        <title_cache_file> : A file to store md5sums of titles to avoid duplicates on restart

