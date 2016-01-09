import http.client
import json
import sys
import urllib.parse


class TelegramBotException(Exception): pass


class TelegramBot(object):
    def __init__(self, token):
        self.server = 'api.telegram.org'
        self.url_base = '/bot' + token

    def _make_request(self, action, params=None):
        if action.startswith('/'):
            action = action[1:]
        
        url = '%s/%s' % (self.url_base, action)
        if params:
            params = urllib.parse.urlencode(params)
        headers = { 'Content-type': 'application/x-www-form-urlencoded' }
        
        conn = http.client.HTTPSConnection(self.server)
        conn.request('POST', url, params, headers)
        response = conn.getresponse()
        data = self._check_response(response)
        conn.close()
        return data
    
    def _check_response(self, response):
        #if response.status != 200:
        #    raise TelegramBotException
        if response.status >= 500:
            raise TelegramBotException('Internal server error')
        
        raw_data = response.read()
        data = json.loads(raw_data.decode('utf-8'))

        if not data['ok']:
            raise TelegramBotException(data['description'])
        
        return data['result']
        
    def _parse_extra(self, data):
        return json.dumps(data, indent=0).replace('\n','')
    
    def get_me(self):
        action = 'getMe'
        return self._make_request(action)
    
    def get_updates(self, offset=None, limit=None, timeout=None):
        action = 'getUpdates'
        params = {}
        if offset:
            params['offset'] = offset
        if limit:
            params['limit'] = limit
        if timeout:
            params['timeout'] = timeout
        return self._make_request(action, params=params)

    def send_message(self, id, text, reply_markup=None, reply_to_message_id=None):
        action = 'sendMessage'
        msg = { 'chat_id': id, 'text': text }
        if reply_markup:
            msg.update({ 'reply_markup': self._parse_extra(reply_markup) })
        if reply_to_message_id:
            msg.update({ 'reply_to_message_id': reply_to_message_id })
        return self._make_request(action, msg)

    def send_location(self, id, latitude, longitude, reply_markup=None, reply_to_message_id=None):
        action = 'sendLocation'
        msg = { 'chat_id': id, 'latitude': latitude, 'longitude': longitude }
        if reply_markup:
            msg.update({ 'reply_markup': self._parse_extra(reply_markup) })
        if reply_to_message_id:
            msg.update({ 'reply_to_message_id': reply_to_message_id })
        return self._make_request(action, msg)

    def set_webhook(self, url):
        action = 'setWebhook'
        webhook = { 'url': url }
        return self._make_request(action, webhook)
