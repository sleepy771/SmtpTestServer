from abc import ABCMeta, abstractmethod


class _Marshaller(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def marshall(self, value):
        pass

    @abstractmethod
    def unmarshall(self, value):
        pass


class MarshallerProvider(_Marshaller):
    __metaclass__ = ABCMeta
    __MARSHALLER_DICT__ = {}

    @classmethod
    def get(cls):
        if cls not in MarshallerProvider.__MARSHALLER_DICT__:
            marshaller = cls()
            MarshallerProvider.__MARSHALLER_DICT__[cls] = marshaller
        return MarshallerProvider.__MARSHALLER_DICT__[cls]

    @classmethod
    def remove(cls):
        if cls not in MarshallerProvider.__MARSHALLER_DICT__:
            return
        del MarshallerProvider.__MARSHALLER_DICT__

    @staticmethod
    def get_for(cls):
        if hasattr(cls, 'get_marshaller'):
            return cls.get_marshaller().get()
        raise Exception('Undefined marshaller')