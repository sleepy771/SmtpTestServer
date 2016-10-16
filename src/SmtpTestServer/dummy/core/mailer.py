from datetime import datetime
from abc import ABCMeta, abstractmethod
from __init__ import tuplify


class Constraints(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, value):
        pass

    @abstractmethod
    def cast(self, value):
        pass

    @abstractmethod
    def is_assignable(self, value):
        pass

    @abstractmethod
    def needs_cast(self, value):
        pass

    @abstractmethod
    def parse(self, value):
        pass

    @abstractmethod
    def create_error_message(self, value):
        pass

    @abstractmethod
    def zero(self):
        pass


class Parseable(object):

    def __init__(self):
        self._values = dict()
        self._non_empty = False

    def __new__(cls, *args, **kwargs):
        pass

    def __setattr__(self, key, value):
        self._set_value(key, value)

    def __getattr__(self, item):
        return self._get_value(name=item)

# override __set__ and __get__
    def _set_value(self, name, value):
        constraints = self.__class__._constraints(name)
        if not constraints:
            raise Exception('Invalid field name %s' % name)
        parsed_value = constraints.parse(value)
        if not constraints.is_assignable(parsed_value):
            raise Exception('Value %s is not assignable to %s' % (str(parsed_value), name))
        casted_value = parsed_value
        if constraints.needs_cast(parsed_value):
            casted_value = constraints.cast(parsed_value)
        if not constraints.validate(casted_value):
            raise ValueError('Invalid value:\n%s' % constraints.create_error_message(casted_value))
        self._values[name] = casted_value

    def _get_value(self, name):
        constraints = self.__class__._constraints(name)
        if not constraints:
            raise Exception('Invalid field name %s' % name)
        if name not in self._values:
            return constraints.zero()
        return self._values[name]

    def _is_assigned(self, name):
        constraint = self.__class__._constraints(name)
        if not constraint:
            raise Exception('Invalid field name %s' % name)
        return name in self._values

    @property
    def only_assigned(self):
        return self._non_empty

    @only_assigned.setter()
    def only_assigned(self, value):
        if type(value) is bool:
            self._non_empty = value
        raise ValueError('Invalid type')

    def __iter__(self):
        return ((name, self._get_value(name)) for name, constraint in self.__dict__.iteritems()\
            if isinstance(constraint, Constraints) and (not self.only_assigned or self._is_assigned(name)))

    @classmethod
    def _constraints(cls, name):
        if name not in cls.__dict__:
            raise Exception('Key %s does not exist in class')
        if not isinstance(cls.__dict__[name], Constraints):
            return None
        return cls.__dict__[name]


class StringList(Constraints):

    def __init__(self, validators=None, parser=str):
        self._validators = tuplify(validators)
        self._parser = parser

    def validate(self, value):
        value = tuplify(value)
        for val in value:
            if type(val) is not str:
                return False
            for validator in self._validators:
                if not validator(val):
                    return False
        return True


    def needs_cast(self, value):
        return False

    def cast(self, value):
        return value

    def is_assignable(self, value):
        return type(value) is str

    def zero(self):
        return ("",)

    def create_error_message(self, value):
        return value

    def parse(self, value):
        return self._parser(value)


class String(Constraints):

    def validate(self, value):
        return True

    def needs_cast(self, value):
        return type(value) is not str

    def cast(self, value):
        return value

    def is_assignable(self, value):
        return type(value) is str

    def zero(self):
        return ""

    def create_error_message(self, value):
        return value

    def parse(self, value):
        return str(value)
