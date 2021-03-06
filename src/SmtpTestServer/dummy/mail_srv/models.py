"""Base mail message models. """
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, ForeignKey
from settings import Base


class Message(Base):
    """Base message model."""

    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    mailbox_id = Column(Integer, ForeignKey('mailboxes.id'))
    sender = Column(String)
    recipients = Column(String)
    subject = Column(String(191))
    source = Column(LargeBinary),
    size = Column(Integer),
    date_created = Column(DateTime)


class MessagePart(Base):
    """Message part model"""

    __tablename__ = 'message_part'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, null=False)
    cid = Column(String)
    part_type = Column(String)
    is_attachement = Column(Integer)
    file_name = Column(String)
    charset = Column(String(8))
    body = Column(LargeBinary)
    size = Column(Integer)
    created_at = Column(DateTime)


class MailBox(Base):
    __tablename__ = 'mailboxes'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=191), nullable=False)
    description = Column(String, nullable=True)
