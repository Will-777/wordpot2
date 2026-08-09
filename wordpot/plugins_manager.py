#!/usr/bin/env python

from flask import request
from wordpot.logger import *
from datetime import datetime, timezone
import json
import os
import configparser # ConfigParser has been renamed configparser

try:
    from user_agents import parse as parse_user_agent
except ImportError:
    # Logging must never be the reason the honeypot goes quiet: without the lib we
    # still emit every field, the parsed User-Agent ones just stay empty.
    parse_user_agent = None

CURRENTPATH = os.path.abspath(os.path.dirname(__file__))

class PluginsManager():
    def __init__(self):
        self.plugins_path = os.path.join(CURRENTPATH, 'plugins/') 

        self.plugins_loaded             = {}
        self.plugins_loaded['plugins']  = []
        self.plugins_loaded['themes']   = []
        self.plugins_loaded['admin']    = []
        self.plugins_loaded['commons']  = []
        return

    def _import_plugin(self, name):
        mod = __import__(name)
        components = name.split('.')
        for c in components[1:]:
            mod = getattr(mod, c)
        return (mod)

    def load(self):
        for root, dirs, files in os.walk(self.plugins_path):
            for file in files:
                if file[-3:] == '.py' and file != '__init__.py':
                    modname = 'wordpot.plugins.' + file[:-3]
                    plugin = self._import_plugin(modname).Plugin() 
                    plugin._load_config(file[:-3])

                    # Add to loaded list organized by categories
                    for h in plugin.hooks: 
                        self.plugins_loaded[h].append(plugin)

    def hook(self, hook):
        return (self.plugins_loaded[hook])
                    
class BasePlugin(object):
    def __init__(self, slug=None):
        self.name           = None
        self.author         = None
        self.link           = None  
        self.description    = None
        self.version        = None
        
        self.slug           = None
        self.hooks          = None
        
        self.request        = None

        self.inputs         = {}
        self.outputs        = {}

    def _load_config(self, slug=None):
        self.slug = slug
        try:
            config = configparser.ConfigParser()
            plugin_config = os.path.join(CURRENTPATH, 'plugins/%s.ini' % self.slug)

            config.read(plugin_config)

            self.name = config.get('plugin', 'name')
            self.author = config.get('plugin', 'author')
            self.link = config.get('plugin', 'link')
            self.description = config.get('plugin', 'description')
            self.version = config.get('plugin', 'version')

            self.hooks = [v.strip() for v in config.get('plugin', 'hooks').split(',')]
        except Exception as e:
            pass
    
    def start(self, **kwargs):
        # First flush previous inputs/outputs
        self.inputs = {}
        self.outputs = {}

        # Parse arguments 
        for k, v in kwargs.items():
            self.inputs[k] = v
        try:
            self.run()
        except Exception as e:
            LOGGER.error('Unable to run plugin: %s\n%s', self.name, str(e))

    def run(self):
        return

    def to_json_log(self, **kwargs):
        req = self.inputs['request']
        raw_ua = req.user_agent.string

        # Scanners send malformed and hand-crafted User-Agents, so the raw string is
        # kept alongside the parsed fields rather than replaced by them.
        ua = {
            'browser_family': '',
            'browser_version': '',
            'os_family': '',
            'os_version': '',
            'device_family': '',
        }
        if parse_user_agent is not None:
            try:
                parsed = parse_user_agent(raw_ua)
                ua = {
                    'browser_family': parsed.browser.family,
                    'browser_version': parsed.browser.version_string,
                    'os_family': parsed.os.family,
                    'os_version': parsed.os.version_string,
                    'device_family': parsed.device.family,
                }
            except Exception as e:
                LOGGER.error('Unable to parse User-Agent: %s', str(e))

        return json.dumps(dict(kwargs,
            timestamp=datetime.now(timezone.utc).isoformat(),
            src_ip=req.remote_addr,
            src_port=req.environ.get('REMOTE_PORT', '0'),
            dest_ip=req.environ.get('SERVER_NAME', ''),
            dest_port=req.environ.get('SERVER_PORT', ''),
            user_agent=raw_ua,
            url=req.url,
            **ua
        ))

