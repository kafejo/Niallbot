import requests


class Attachment:
    def __init__(self, title, fields, color='#2a80b9'):
        self.title = title
        self.fields = fields
        self.color = color


class AttachmentField:
    def __init__(self, title, value, is_short):
        self.title = title
        self.value = value
        self.is_short = is_short


class Slacker:

    def __init__(self, response_url, bot_token, is_debug=False):
        self.response_url = response_url
        self.bot_token = bot_token
        self.is_debug = is_debug

    def send(self, text, attachments=[]):
        payload_dictionary = {
           "text": text,
           "mrkdwn_in": [
               "text"
           ]
        }

        attchs = []

        for attachment in attachments:
            fields = []

            for field in attachment.fields:
                f = {
                        "title": field.title,
                        "value": field.value,
                        "short": field.is_short
                    }
                fields.append(f)

            attch = {
                "title": attachment.title,
                "fields": fields,
                "color": attachment.color,
                "mrkdwn_in": [
                    "title",
                ]
            }

            attchs.append(attch)

        payload_dictionary['attachments'] = attchs
        payload_dictionary['response_type'] = 'in_channel'

        if self.is_debug:
            print(payload_dictionary)
        else:
            headers = {
                'Authorization': 'Bearer ' + self.bot_token,
                'Content-Type': 'application/json; charset=utf-8'
            }

            requests.post(self.response_url, json=payload_dictionary, headers=headers)
