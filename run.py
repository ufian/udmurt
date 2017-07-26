# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

__author__ = 'ufian'

import os
import re
import time
import logging
import random
from slackclient import SlackClient

logger = logging.getLogger(__name__)

def _is_bot_mention(sc, event):
    bot_user_name = sc.server.login_data['self']['id']
    if re.search("@{}".format(bot_user_name), event.get('text', '')):
        return True
    else:
        return False
    
def _is_direct_message(sc, event):
    return event.get('channel').startswith('D')


def message_leave(event):
    return u"<@{0}> так и не узнал что такое логарифм".format(event['user'])

def message_join(event):
    return u"<@rosnovsky> запиши подкаст! А то <@{0}> вряд ли узнает, что такое интеграл.".format(event['user'])

def message_event(sc, event):
    msg = event['text']
    msg_lower = msg.lower()
    
    if 'методичк' in msg_lower or 'metodichka' in msg_lower:
        return "Официальная методичка яндекса тут https://yandex.ru/company/press_releases"
    if _is_bot_mention(sc, event) or _is_direct_message(sc, event):
        return random.choice([
            u"Зачем это?",
            u"И где в этом дух приключений?"
        ])


def handle(sc, events):
    for event in events:
        logging.info('Event: {0}'.format(event))
        event_type = event.get('type', 'None')
        if event_type == 'message':
            reply = handle_message(sc, event)
            
            if reply is not None:
                sc.rtm_send_message(
                  channel=event.get('channel'),
                  message=reply,
                )
        
def handle_message(sc, event):
    subtype = event.get('subtype', '')
    
    reply = None
    
    if 'join' in subtype:
        reply = message_join(event)
    elif 'leave' in subtype:
        reply = message_leave(event)
    else:
        reply = message_event(sc, event)
        
    return reply


def main():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)
    
    slack_token = os.getenv("SLACK_TOKEN", "")
    logging.info("token: {}".format(slack_token))
    sc = SlackClient(slack_token)
    

    if sc.rtm_connect():
        while True:
            try:
                handle(sc, sc.rtm_read())
            except:
                logging.exception('Problem')
            time.sleep(1)
    else:
        logging.error("Connection Failed, invalid token?")


if __name__ == "__main__":
    main()
