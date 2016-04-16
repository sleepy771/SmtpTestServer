from datetime import datetime

from abc import ABCMeta, abstractmethod, abstractproperty


class Property(object):
    __metaclass__ = ABCMeta

    def __init__(self, type_, *args, **kwargs):
        constraints = kwargs.pop('constraints', None)
        name = kwargs.pop('name', None)
        if not constraints:
            if len(args) > 0:
                constraints = args[0]
        if not name:
            if len(args) > 1:
                name = args[1]
        nullable = kwargs.pop('nullable', None)

        self._constraints = constraints or tuple()
        self._name = name
        self._type = type_

    @abstractmethod
    def check_type(self, value):
        pass

    @abstractproperty
    def is_simple(self):
        return True

    def is_valid(self, value):
        if self.check_type(value):
            for constraint in self._constraints:
                if not constraint.is_valid(value):
                    return False
            return True
        return False

    def convert(self, dct, name):
        return dct

    def to_dict(self, dct, name):
        return dct


class SimpleProperty(Property):

    def __init__(self, type_, constraints=None, name=None):
        super(SimpleProperty, self).__init__(type_, constraints, name)

    def check_type(self, value):
        return type(value) is self._type

    def is_simple(self):
        return True


class MarshallableProperty(Property):
    __metaclass__ = ABCMeta

    def __init__(self, type_, constraints=None):
        super(MarshallableProperty, self).__init__(type_, constraints)

    @abstractmethod
    def unmarshall(self, value):
        pass

    @abstractmethod
    def marshall(self, value):
        pass

    def convert(self, dct, name):
        value = dct[name]
        dct[name] = self.unmarshall(value)
        return dct

    def to_dict(self, dct, name):
        value = dct[name]
        dct[name] = self.marshall(value)
        return dct

    def check_type(self, value):
        return isinstance(value, self._type)

    def is_simple(self):
        return False


class ModelProperty(Property):

    def __init__(self, type_, constraints=None):
        if not issubclass(type_, ApiModel):
            raise Exception('Only ApiModels could be ModelProperty types')
        super(ModelProperty, self).__init__(type_, constraints)

    def check_type(self, value):
        return isinstance(value, self._type)

    def convert(self, dct, name):
        value = dct[name]
        if self.check_type(value):
            return True
        if type(value) is not dict:
            raise Exception('Property have to be dict type in order to unmarshall it')
        obj = self._type.load(value)
        dct[name] = obj
        return dct

    def to_dict(self, dct, name):
        value = dct[name]
        model_dct = self._type.load(value)
        dct[name] = model_dct
        return dct

    def is_simple(self):
        return False


class DateTimeProperty(MarshallableProperty):
    def __init__(self, format_, constraints=None):
        super(DateTimeProperty, self).__init__(format_, constraints)
        self._format = format_

    def marshall(self, value):
        return datetime.strftime(self._format)

    def unmarshall(self, value):
        return datetime.strptime(value, self._format)


class ListOfModelsProperty(Property):

    def __init__(self, type_, constraints=None):
        if not issubclass(type_, ApiModel):
            raise Exception('Only ApiModels could be ModelProperty types')
        super(ListOfModelsProperty, self).__init__(type_, constraints)

    def check_type(self, values):
        if type(values) is not list:
            return False
        for value in values:
            if not isinstance(value, self._type):
                return False
        return True

    def convert(self, dct, name):
        values = dct[name]
        if values is not list:
            raise Exception('Expected list property')
        if self.check_type(values):
            return dct
        unmarshaled = []
        for value in values:
            if type(value) is not dict:
                raise Exception('Property have to be dict type in order to unmarshall it')
            obj = self._type.load(value)
            unmarshaled.append(obj)
        dct[name] = unmarshaled
        return dct

    def to_dict(self, dct, name):
        marshaled = []
        values = dct[name]
        if values is None:
            return None
        for value in values:
            marshaled_obj = self._type.dumps(value)
            marshaled.append(marshaled_obj)
        dct[name] = marshaled
        return dct

    def is_simple(self):
        return False


class ApiModel(object):
    __metaclass__ = ABCMeta
    __EMPTY__ = object()

    @classmethod
    def _properties(cls):
        return ((name, prop) for name, prop in cls.__dict__.iteritems() if isinstance(prop, Property))

    @classmethod
    def load(cls, dct):
        unmarshalled = cls()
        for name, prop in cls._properties():
            if name not in dct:
                raise Exception('Property does not exist')
            if not prop.is_simple:
                prop.convert(dct)
            if prop.is_valid(dct[name]):
                raise Exception('Invalid property value')
            setattr(unmarshalled, name, dct[name])
        return unmarshalled

    @classmethod
    def dumps(cls, obj):
        if not isinstance(obj, cls):
            raise Exception('Invalid type')
        marshaled = {}
        for name, prop in cls._properties():
            value = getattr(obj, name, ApiModel.__EMPTY__)
            if value is ApiModel.__EMPTY__:
                raise Exception('Value never assigned')
            marshaled[name] = value
            if not prop.is_valid(value):
                raise Exception('Invalid value')
            if not prop.is_simple:
                prop.to_dict(marshaled, name)
        return marshaled