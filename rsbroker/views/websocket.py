from __future__ import absolute_import

import logging
import ujson
from tornado import websocket
from rsbroker.events.user import UserServerDispatch
from rsbroker.core.user import UserManager

logger = logging.getLogger(__name__)
broker_server_dispatch = UserServerDispatch()


class BrokerServerHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        """
        ws://127.0.0.1:3223/api/ws?ip=192.168.1.11&port=9001&node=-1&room=0&uid=123456
        :return:
        """
        setattr(self, 'room', self.get_argument("room"))
        setattr(self, 'uid', self.get_argument("uid"))
        ni = UserManager.register(self)
        self.write_message(ujson.dumps({'method': 'connect', 'node': ni.node}))

    def on_message(self, message):
        """
        :param message: A dict type, as below example:
        {
            "method": "check_in",
            "body":{}
        }
        :return: write thing back
        """
        try:
            data = ujson.loads(message)
            method = data.get("method")
            body = data.get("body")
            getattr(broker_server_dispatch, method, getattr(broker_server_dispatch, "default"))(body)
            response = broker_server_dispatch.response
        except TypeError:
            response = 'p'
        self.write_message(response)

    def on_close(self):
        UserManager.unregister(self)
