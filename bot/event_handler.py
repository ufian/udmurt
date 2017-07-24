# -*- encoding: utf-8 -*-
import json
import logging
import re

logger = logging.getLogger(__name__)


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer):
        self.clients = slack_clients
        self.msg_writer = msg_writer

    def handle(self, event):

        if 'type' in event:
            try:
                self._handle_by_type(event['type'], event)
            except:
                pass

    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events
        #logger.warning('Handle type {0} {1}'.format(event_type, event)
        if 'channel' not in event:
            event['chanel'] = None
        if event_type == 'error':
            # error
            self.msg_writer.write_error(event['channel'], json.dumps(event))
        elif event_type == 'message':
            # message was sent to channel
            self._handle_message(event)
        elif event_type == 'channel_joined' or event_type=='team_join':
            logging.debug('channel or team: {0} {1}'.format(event_type, event))
            # you joined a channel
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            logging.debug('group: {0} {1}'.format(event_type, event))
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself, and from non-users (eg. webhooks)
        if ('user' in event) and (not self.clients.is_message_from_me(event['user'])):
            logging.debug('message: {0}'.format(event))

            msg_txt = event['text']
            #name = event.get('user_profile', {}).get('name', 'noname')

            if 'leave' in event.get('subtype', ''):
                self.msg_writer.write_leave(event['channel'], event['user'])
            
            if 'join' in event.get('subtype', ''):
                self.msg_writer.write_join(event['channel'],event['user'])

            if self.clients.is_bot_mention(msg_txt) or self._is_direct_message(event['channel']):
                # e.g. user typed: "@pybot tell me a joke!"
                if 'help' in msg_txt:
                    self.msg_writer.write_help_message(event['channel'])
                elif u'методичк' in msg_txt.lower() or 'metodichka' in msg_txt:
                    self.msg_writer.write_ya(event['channel'], event['user'])
                elif re.search('hi|hey|hello|howdy', msg_txt):
                    self.msg_writer.write_greeting(event['channel'], event['user'])
                elif 'joke' in msg_txt:
                    self.msg_writer.write_joke(event['channel'])
                elif 'attachment' in msg_txt:
                    self.msg_writer.demo_attachment(event['channel'])
                elif 'echo' in msg_txt:
                    self.msg_writer.send_message(event['channel'], msg_txt)
                else:
                    self.msg_writer.write_prompt(event['channel'])

    def _is_direct_message(self, channel):
        """Check if channel is a direct message channel

        Args:
            channel (str): Channel in which a message was received
        """
        return channel.startswith('D')
