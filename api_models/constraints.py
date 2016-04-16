from abc import ABCMeta, abstractmethod


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


class NonZero(Constraint):

    def is_valid(self, value):
        return True if value else False


class InInterval(Constraint):
    OPEN = 'o'
    CLOSED = 'c'
    LEFT_OPEN = 'l'
    RIGHT_OPEN = 'r'

    def __init__(self, *args, **kwargs):
        max_ = kwargs.pop('max', None)
        min_ = kwargs.pop('min', None)
        type_ = kwargs.pop('type_', InInterval.CLOSED)

        if len(args) > 0:
            min_ = args[0]
        if len(args) > 1:
            max_ = args[1]
        if len(args) > 2:
            type_ = args[3]

        self._min = min_
        self._max = max_

        self._lower = self._true
        self._upper = self._true

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

    def _true(self, value):
        return True

class InSet(Constraint):

    def __init__(self, *args, **kwargs):

        set_ = kwargs.pop('set_', None)

        if len(args) > 0:
            set_ = args[0]

        if not hasattr(set_, '__iter__'):
            set_ = (set_,)

        self._set = set(set_)

    def is_valid(self, value):
        return value in self._set