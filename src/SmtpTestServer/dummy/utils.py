from abc import ABCMeta, abstractmethod, abstractproperty


def singleton(cls):
    SINGLETONS = {}

    def create_or_get(*args, **kwargs):
        if cls not in SINGLETONS:
            SINGLETONS[cls] = cls(*args, **kwargs)
        return SINGLETONS[cls]

    return create_or_get


def tuplify(elem):
    if hasattr(elem, '__iter__'):
        return tuple(elem)
    return tuple((elem,))


__EMPTY__ = object()


def load_arg(idx, name, default_=None, *args, **kwargs):
    arg = kwargs.pop(name, __EMPTY__)
    if len(args) > idx:
        if arg is __EMPTY__:
            arg = args[idx]
        else:
            raise Exception('Argument %s on index %d defined more than once' % (name, idx))
    if arg is __EMPTY__:
        return default_
    return arg


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


class _IP(object):
    __metaclass__ = ABCMeta

    def __init__(self, item):
        self._item = item

    @abstractmethod
    def get(self):
        pass

    @abstractproperty
    def is_class(self):
        pass

    @property
    def item(self):
        return self._item


class _MetaIP(_IP):

    def __init__(self, cls):
        super(_MetaIP, self).__init__(cls)

    @property
    def is_class(self):
        return True

    def get(self):
        inj = Injector.get()
        if self.item in inj:
            return inj.instantiate()
        return self.item()


class _InstanceIP(_IP):

    def __init__(self, instance):
        super(_InstanceIP, self).__init__(instance)

    @property
    def is_class(self):
        return False

    def get(self):
        return self.item


class Injector(object):
    __metaclass__ = ABCMeta
    __INSTANCE__ = None

    class _Builder(object):

        def __init__(self, cls):
            self._meta_ = cls

        def add_arg_class(self, cls):
            pass

        def add_arg_instance(self, obj):
            pass

    def __init__(self):
        self._bounds = {}
        self.bind()

    def create_bound(self, cls):
        pass


    def instantiate(self):
        pass


    @abstractmethod
    def bind(self):
        pass

    @classmethod
    def create(cls):
        if Injector.__INSTANCE__ is not None:
            raise Exception('Can not instantiate multiple Injector classes')
        Injector.__INSTANCE__ = cls()

    @staticmethod
    def get():
        if Injector.__INSTANCE__ is None:
            raise Exception('Injector not instantiated')
        return Injector.__INSTANCE__


def inject(cls):
    pass

