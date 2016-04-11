

class Importer(object):

    def __init__(self, convention):
        self._imports = {}
        self._convention = convention

    def get(self, module):
        if hasattr(module, '__iter__'):
            mod_list = []
            for m in module:
                mod_name, model_name = m.rsplit('.', 1)
                module_name = '%s.%s' % (mod_name, self._convention)
                if not self.imported(module_name):
                    mod_list.append(module_name)
            self._import_all(mod_list)
            imps = []



    def _import_all(self, mod_list):
        mods = map(__import__, mod_list)
        if len(mods) != len(mod_list):
            raise Exception('Imports failed')
        for k in xrange(0, len(mods)):
            self._imports[mod_list[k]] = mods[k]