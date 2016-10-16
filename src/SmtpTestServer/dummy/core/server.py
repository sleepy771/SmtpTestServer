#!/usr/bin/env python3

from smtplib import SMTPServer


class DummyServer(SMTPServer):

    def __init__(self, *args, **kwargs):
        pass


