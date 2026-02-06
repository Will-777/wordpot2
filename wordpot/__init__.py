#/usr/bin/env python3

try:
    from flask import Flask
except ImportError:
    print ("\n[X] Please install Flask:")
    print ("   $ pip install flask\n")
    exit()

import argparse 
from wordpot.logger import * 
from werkzeug.routing import BaseConverter 
from wordpot.plugins_manager import PluginsManager 
import os

# ---------------
# Regex Converter
# ---------------

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

# -------
# Options
# -------

REQUIRED_OPTIONS = {
        'HOST':  '127.0.0.1',
        'PORT':  '80',
        'THEME': 'twentyeleven',
        'BLOGTITLE': 'Random Rambling',
        'AUTHORS': ['admin']
        }


def parse_options():
    description = "Wordpot2 - Honeypot WordPress moderne"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--host', dest='HOST', help='Host address')
    parser.add_argument('--port', dest='PORT', help='Port number')
    parser.add_argument('--title', dest='BLOGTITLE', help='Blog title')
    parser.add_argument('--theme', dest='THEME', help='Default theme name')
    parser.add_argument('--plugins', dest='PLUGINS', help='Fake installed plugins (comma-separated)')
    parser.add_argument('--themes', dest='THEMES', help='Fake installed themes (comma-separated)')
    parser.add_argument('--ver', dest='VERSION', help='Wordpress version')
    parser.add_argument('--server', dest='SERVER', help='Custom "Server" header')

    options = parser.parse_args()
    
    for opt, val in options.__dict__.items():
        if val is not None:
            if opt in ['PLUGINS', 'THEMES']:
                val = [ v.strip() for v in val.split(',') ] 
            app.config[opt] = val


def check_options():
    #for k, v in REQUIRED_OPTIONS.iteritems():
    for k, v in REQUIRED_OPTIONS.items():
        if k not in app.config:
            LOGGER.error('%s was not set. Falling back to default: %s', k, v)
            app.config[k] = v

# -------------------
# Building the Logger
# -------------------

logging_setup()

# ------------
# Building app
# ------------

app = Flask('wordpot', static_url_path='')
app.url_map.converters['regex'] = RegexConverter

# Import config from file
conffile = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../wordpot.conf')
LOGGER.info('Loading conf file: %s', conffile) # %s doesn't work with python3
try:
    app.config.from_pyfile(conffile)
except Exception as e:
    LOGGER.error("Can't load conf file: %s", str(e))
check_options()

if app.config['HPFEEDS_ENABLED']:
    import hpfeeds
    print ('Connecting to hpfeeds broker {}:{}'.format(app.config['HPFEEDS_HOST'], app.config['HPFEEDS_PORT']))
    app.config['hpfeeds_client'] = hpfeeds.new(
        app.config['HPFEEDS_HOST'], 
        app.config['HPFEEDS_PORT'], 
        app.config['HPFEEDS_IDENT'], 
        app.config['HPFEEDS_SECRET']
    )
    app.config['hpfeeds_client'].s.settimeout(0.01)
else:
    LOGGER.warning('hpfeeds is disabled')


# ------------------------
# Add Custom Server Header
#-------------------------

@app.after_request
def add_server_header(response):
    if app.config['SERVER']:
        response.headers['Server'] = app.config['SERVER']

    return response

# ----------------------------
# Building the plugins manager
# ----------------------------

pm = PluginsManager()
pm.load()

import wordpot.views
