from email import message_from_string, message_from_file
from email.message import Message
from email.utils import getaddresses

from abc import ABCMeta, abstractmethod


class RouteSelector(object):
    ___metaclass__ = ABCMeta

    @abstractmethod
    def get_route(self, message, to, from_):
        pass


class Route(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def send(self, message, from_, to):
        pass


class Router(object):

    def __init__(self, route_selector):
        self._route_selector = route_selector

    def on_receive(self, message):
        msg_type = type(message)
        if msg_type is str:
            msg = message_from_string(message)
        elif msg_type is file:
            msg = message_from_file(message)
        elif msg_type is Message:
            msg = message
        else:
            raise Exception('Unsupported message type')
        from_ = getaddresses(msg.get_all('from'))
        recipients = []
        for header in ('to', 'cc', 'bcc'):
            for name, email in getaddresses(msg.get_all(header)):
                recipients.append(email)
        for recipient in recipients:
            self.route(msg, recipient, from_)

    def route(self, message, to, from_):
        route = self._route_selector.get_route(message, to, from_)
        route.send(message, from_, to)


class SourceException(Exception):
    pass


class _Source(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._sink = None

    def connect(self, sink):
        if isinstance(sink, _Sink):
            self._sink = sink

    def send(self, message, from_, to):
        try:
            message = self.prepare(message, from_, to)
            if self._sink:
                self._sink.receive(message, from_, to)
        except SourceException as e:
            print e.message # log zis

    @abstractmethod
    def prepare(self, message, from_, to):
        pass


class _Sink(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def receive(self, message, from_, to):
        pass


class _Handler(_Sink, _Source):
    __metaclass__ = ABCMeta

    @abstractmethod
    def prepare(self, message, from_, to):
        pass

    def receive(self, message, from_, to):
        self.send(message, from_, to)