# """Base module with controllers"""
from settings import app, Session
from models import Message
from email.utils import formataddr
from StringIO import StringIO
import json


@app.route('/inbox/')
def list_messages():
    """Return list of recieved mail messages"""
    session = Session()
    messages = session.query(Message).all()
    msg_lst = []
    for message in messages:
        msg_lst.append(create_message(message))
    return msg_lst


@app.route('/inbox/<int:id>', methods=['GET'])
def show_message(id):
    """
    Return message selected by id
    """
    session = Session()
    message = session.query(Message).filter_by(id=id).one()
    msg_dct = create_message(message)
    msg_dct["size"] = message.size
    msg_dct["recipients"] = create_recipients(message.recipients)
    return msg_dct


def create_message(message):
    """
    Create json message object, based on model.
    :arg message: database model
    :type: models.Message
    :return: return json compatible message
    :rtype: dict
    """
    return {
        "id": message.id,
        "from": message.sender,
        "preview": create_preview(message),
        "subject": message.subject,
        "date": message.date_created,
    }


def create_recipients(rcp_list):
    """
    Create recipient mailaddresses from string
    :return: list of recipients
    :rtype: list
    """
    out_addrs = {}
    addresses = json.load(StringIO(rcp_list))
    headers = ('to', 'cc', 'bcc')
    for header in headers:
        out_addrs[header] = []
        for name, email in addresses[header]:
            out_addrs[header].append((name, email))
    return out_addrs


def create_preview(message):
    """
    Create preview of message
    :arg message: database model
    :type: models.Message
    :return: Return message preview as string
    :rtype: str
    """
