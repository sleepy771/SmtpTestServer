from datetime import datetime

from abc import ABCMeta, abstractmethod, abstractproperty
from constraints import InInterval, InSet, NotEmpty, NotNull
from utils import load_arg, tuplify


class Property(object):
    __metaclass__ = ABCMeta

    def __init__(self, type_, *args, **kwargs):
        name = load_arg(0, 'name', *args, **kwargs)
        getter = load_arg(1, 'get', *args, **kwargs)
        setter = load_arg(2, 'set', *args, **kwargs)

        self._constraints = kwargs.pop('constraints', default=tuple())
        self._name = name
        self._type = type_
        self._getter = getter
        self._setter = setter

    @abstractmethod
    def check_type(self, value):
        pass

    @abstractproperty
    def is_simple(self):
        return True

    @property
    def has_getter(self):
        return self._getter is not None

    @property
    def has_setter(self):
        return self._setter is not None

    @property
    def use_name(self):
        return True if self._name else False

    @property
    def name(self):
        return self._name

    def is_valid(self, value):
        if self.check_type(value):
            for constraint in self._constraints:
                if not constraint.is_valid(value):
                    return False
            return True
        return False


class SimpleProperty(Property):
    def __init__(self, type_, *args, **kwargs):
        constraints = []
        if type_ in (int, float, long):
            _max = load_arg(4, 'max_', *args, **kwargs)
            _min = load_arg(3, 'min_', *args, **kwargs)
            if _max or _min:
                interval_constraint = InInterval(max_=_max, min_=_min, type_=InInterval.CLOSED)
                constraints.append(interval_constraint)
        in_set = load_arg(5, 'in_', *args, **kwargs)
        if in_set:
            _set_constraint = InSet(set_=in_set)
            constraints.append(_set_constraint)
        _empty = load_arg(6, 'empty', default_=False, *args, **kwargs)
        if not _empty and type_ in (str, list, tuple, dict, set):
            empty_constraint = NotEmpty()
            constraints.append(empty_constraint)
        _null = load_arg(7, 'nullable', default_=True, *args, **kwargs)
        if not _null:
            null_constraint = NotNull()
            constraints.append(null_constraint)
        _custom_constraints = load_arg(8, 'constraints', default_=tuple(), *args, **kwargs)
        constraints.extend(_custom_constraints)
        kwargs['constraints'] = constraints
        super(SimpleProperty, self).__init__(type_, *args, **kwargs)

    def check_type(self, value):
        return type(value) is self._type

    def is_simple(self):
        return True


class MarshallableProperty(Property):

    def __init__(self, type_, *args, **kwargs):
        constraints = []
        _marshaller = load_arg(3, 'marshaller', *args, **kwargs)
        if not _marshaller:
            raise Exception('Can not create marshaller property without marshaller')
        if type(_marshaller) is not type or issubclass(_marshaller, MarshallableProperty):
            raise Exception('Expected marshaller type is subclass of MarshallerProvider')
        self._marshaller = _marshaller
        _null = load_arg(4, 'nullable', default_=True *args, **kwargs)
        if not _null:
            constraints.append(NotNull())
        _in_set = load_arg(5, 'in_', default_=tuple(), *args, **kwargs)
        if _in_set:
            constraints.append(InSet(set_=_in_set))
        _custom_constraints = load_arg(6, 'constraints', *args, **kwargs)
        if _custom_constraints:
            constraints.extend(tuplify(_custom_constraints))
        kwargs['constraints'] = constraints
        super(MarshallableProperty, self).__init__(type_, *args, **kwargs)

    def unmarshall(self, value):
        return self._marshaller.get().unmarshall(value)

    def marshall(self, value):
        return self._marshaller.get().marshall(value)

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
        super(ModelProperty, self).__init__(type_, constraints=constraints or tuple())

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
    def __init__(self, type_, *args, **kwargs):
        if not issubclass(type_, ApiModel):
            raise Exception('Only ApiModels could be ModelProperty types')
        super(ListOfModelsProperty, self).__init__(type_, *args, **kwargs)

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
        """
        :returns: defined model properties
        :rtype: __generator<[str, Property]>
        """
        return ((name, prop) for name, prop in cls.__dict__.iteritems() if isinstance(prop, Property))

    @classmethod
    def load(cls, dct):
        unmarshalled = cls()
        for name, prop in cls._properties():
            if prop.use_name:
                name = prop.name
            if name not in dct:
                raise Exception('Property does not exist')
            if not prop.is_simple:
                prop.convert(dct, name)
            if prop.is_valid(dct[name]):
                raise Exception('Invalid property value')
            if prop.has_setter:
                setter = getattr(unmarshalled, prop.setter)
                setter(dct[name])
            else:
                setattr(unmarshalled, name, dct[name])
        return unmarshalled

    @classmethod
    def dumps(cls, obj):
        if not isinstance(obj, cls):
            raise Exception('Invalid type')
        marshaled = {}
        for name, prop in cls._properties():
            if prop.use_name:
                name = prop.name
            value = getattr(obj, name, ApiModel.__EMPTY__)
            if value is ApiModel.__EMPTY__ and not prop.is_nullable:
                raise Exception('Undefined property %s' % name)
            marshaled[name] = value
            if not prop.is_valid(value):
                raise Exception('Invalid value for property %s' % name)
            if not prop.is_simple:
                prop.to_dict(marshaled, name)
        return marshaled
