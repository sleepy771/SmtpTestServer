from abc import ABCMeta, abstractmethod


class ConstraintException(Exception):

    def __init__(self, constraint, prop_name, value_str):
        m = "Invalid value %s in property %s, according to constraint %s" % (
            value_str, prop_name, constraint.get_description())
        super(ConstraintException, self).__init__(m)


class PropertyNotFoundException(Exception):

    def __init__(self, property_name):
        message = "Property %s not found in received dict" % property_name
        super(PropertyNotFoundException, self).__init__(message)


class _Property(object):
    __SIMPLE_TYPES = {'int', 'str', 'float'}

    def __init__(self, name, type_, constraints):
        self._name = name
        self._type = type_
        if not hasattr(constraints, '__iter__'):
            constraints = [constraints]
        self._constraints = tuple(constraints)

    def validate(self, value):
        for constraint in self._constraints:
            if not constraint.validate(value):
                raise ConstraintException(constraint, self._name, value)

    @property
    def is_simple(self):
        return self._type in _Property.__SIMPLE_TYPES or (
        self._type.startsWith("list<") and self._type.split("<")[1].trim(">") in _Property.__SIMPLE_TYPES)

    def assign(self, dct, obj):
        if self._name not in dct:
            raise PropertyNotFoundException(self._name)
        if self.is_simple:
            obj.put(self._name, dct[self._name])
        else:
            pass


class Model(object):
    __metaclass__ = ABCMeta

    class Meta(object):

        def __init__(self):
            self._properties = {}
            self.__init_properties()

        def _put(self, prop):
            if prop.name in self._properties:
                raise Exception('Property %s already registered' % prop.name)
            self._properties[prop.name] = prop

        @property
        def list(self):
            return tuple((prop for prop in self._properties.values()))

        def __init_properties(self):
            pass

    @classmethod
    def get_meta(cls):
        if not hasattr(cls, '__META__'):
            cls.__META__ = cls.Meta()
        return cls.__META__

    def __init__(self):
        pass

    def toJson(self):
        pass

    def load(self, json_obj):
        pass


class ModelProvider(object):

    def __init__(self):
        self._models = {}

    def get(self, model):
        """
        :type model: str
        :return: model meta for specified model class
        :rtype: Model.Meta
        """
        if model not in self._models:
            module, model_name = model.rsplit('.', 1)
            load_module = '%s.api.%s' % (module, model_name)
            __import__(load_module)
        pass
