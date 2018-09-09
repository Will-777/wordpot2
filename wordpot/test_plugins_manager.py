# yes it is !
import os
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
