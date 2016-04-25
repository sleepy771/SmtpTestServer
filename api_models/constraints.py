from abc import ABCMeta, abstractmethod
from utils import load_arg


class Constraint(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_valid(self, value):
        pass

    def __call__(self, *args, **kwargs):
        value = kwargs.pop('value', None)
        if len(args) > 0:
            value = args[0]
        return self.is_valid(value)


class NotNull(Constraint):

    def is_valid(self, value):
        return value is not None


class NotEmpty(Constraint):

    def is_valid(self, value):
        return True if value else False


class InInterval(Constraint):
    OPEN = 'o'
    CLOSED = 'c'
    LEFT_OPEN = 'l'
    RIGHT_OPEN = 'r'

    def __init__(self, *args, **kwargs):
        """
        :param min\_: minimal value (inclusive or exclusive depending on type_)
        :param max\_: maximal value (exclusiveness is dependant on type_ flag)
        if no value or null is provided condition is always true for upper ound
        :type: int|long|float
        """
        max_ = load_arg(1, 'max_', *args, **kwargs)
        min_ = load_arg(0, 'min_', *args, **kwargs)
        type_ = load_arg(2, 'type_', *args, **kwargs)

        self._min = min_
        self._max = max_

        self._lower = InInterval._true
        self._upper = InInterval._true

        if min_ is not None:
            if type_ in [InInterval.LEFT_OPEN, InInterval.OPEN]:
                self._lower = self._lower_exclusive
            else:
                self._lower = self._lower_inclusive
        if max_ is not None:
            if type_ in [InInterval.RIGHT_OPEN, InInterval.OPEN]:
                self._upper = self._upper_exclusive
            else:
                self._upper = self._upper_inclusive

    def is_valid(self, value):
        return self._lower(value) and self._upper(value)

    def _lower_inclusive(self, value):
        return self._min <= value

    def _lower_exclusive(self, value):
        return self._min < value

    def _upper_inclusive(self, value):
        return self._max >= value

    def _upper_exclusive(self, value):
        return self._max > value

    @staticmethod
    def _true(value):
        return True


class InSet(Constraint):

    def __init__(self, *args, **kwargs):

        set_ = load_arg(0, 'set_', *args, **kwargs)

        if not hasattr(set_, '__iter__'):
            set_ = (set_,)

        self._set = set(set_)

    def is_valid(self, value):
        return value in self._set
