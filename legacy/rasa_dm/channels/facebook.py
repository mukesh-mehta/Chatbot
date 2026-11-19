from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from flask import Blueprint, request, jsonify
from pymessenger.bot import Bot

from rasa_dm.channels.channel import UserMessage, OutputChannel
from rasa_dm.channels.rest import HttpInputComponent


logger = logging.getLogger(__name__)


class MessengerBot(Bot, OutputChannel):
    """A bot that uses fb-messenger to communicate."""

    def __init__(self, access_token):
        super(MessengerBot, self).__init__(access_token)

    def send_text_with_buttons(self, recipient_id, text, buttons, **kwargs):
        # buttons is a list of tuples: [(option_name,payload)]
        if len(buttons) > 3:
            logger.warn("Facebook API currently allows only up to 3 buttons. If you add more, all will be ignored.")
            return self.send_text_message(recipient_id, text)
        else:
            self._add_postback_info(buttons)
            return self.send_button_message(recipient_id, text, buttons)

    def _add_postback_info(self, buttons):
        for button in buttons:
            button['type'] = "postback"

    def send_custom_message(self, recipient_id, elements):
        #for element in elements:
            #self._add_postback_info(element['buttons'])
        return self.send_generic_message(recipient_id, elements)
    def send_custom_list_message(self, recipient_id, elements,button):
        
        return self.send_list_message(recipient_id, elements,button)    

    def send_itinerary(self,recipient_id,payload):
        return self.send_airline_itinerary(recipient_id,payload)    

    def send_fb_message(self,recipient_id,message):

        return self.send_message(recipient_id,message)

    def get_user_details(self,recipient_id):

        return self.get_user_info(recipient_id)

    def send_img_url(self,recipient_id,image_url):
        return self.send_image_url(recipient_id,image_url)


class FacebookInput(HttpInputComponent):
    def __init__(self, fb_verify, fb_secret, fb_tokens, debug_mode):
        self.fb_verify = fb_verify
        self.fb_secret = fb_secret
        self.debug_mode = debug_mode
        self.fb_tokens = fb_tokens

    def blueprint(self, on_new_message):
        from pymessenger.utils import validate_hub_signature

        fb_webhook = Blueprint('fb_webhook', __name__)

        @fb_webhook.route("/", methods=['GET'])
        def health():
            return jsonify({"status": "ok"})

        @fb_webhook.route("/webhook", methods=['GET', 'POST'])
        def hello():
            if request.method == 'GET':
                if request.args.get("hub.verify_token") == self.fb_verify:
                    return request.args.get("hub.challenge")
                else:
                    return "failure, invalid token"
            if request.method == 'POST':

                output = request.json          
                page_id = output['entry'][0]['id']
                event = output['entry'][0]['messaging']
                #print(event)
                for x in event:
                    if x.get('message') and x['message'].get('text') and not x['message'].get("is_echo"):
                        text=x['message']['text']  
                    elif x.get('message') and x['message'].get('attachments'):
                        attach = x['message']['attachments'][0]
                        if attach['type'] == 'audio':
                            text = attach['payload']['url']
                        else:
                            text = ""
                    elif x.get('postback') and x['postback'].get('payload'):
                        text = x['postback']['payload']
                    else:
                        continue
                    try:
                        sender = x['sender']['id']
                        if page_id in self.fb_tokens:
                            on_new_message(UserMessage(text, MessengerBot(self.fb_tokens[page_id]), sender))
                        else:
                            raise Exception("Unknown page id '{}'. ".format(page_id) +
                                        "Make sure to add a page token in the config.")
                    except Exception as e:
                        logger.error("Exception when trying to handle message.{0}".format(e))
                        if self.debug_mode:
                            raise
                        pass
                return "success"
        return fb_webhook
