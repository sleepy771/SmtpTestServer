from api.models import ApiModel, SimpleProperty, DateTimeProperty, ListOfModelsProperty


class MessagePart(ApiModel):
    id = SimpleProperty(int)
    part_type = SimpleProperty(str)
    is_attachment = SimpleProperty(int)
    file_name = SimpleProperty(str)
    charset = SimpleProperty(str)  # create options property
    body = SimpleProperty(str)
    size = SimpleProperty(int)
    created = DateTimeProperty("Y/M/d H:m:s")


class Message(ApiModel):
    id = SimpleProperty(int)
    from_ = SimpleProperty(str, name='from')
    preview = SimpleProperty(str)
    subject = SimpleProperty(str)
    date = DateTimeProperty("Y/M/d H:m:s")  # create format
    size = SimpleProperty(int)
    recipients = SimpleProperty(dict)
    parts = ListOfModelsProperty(MessagePart)
