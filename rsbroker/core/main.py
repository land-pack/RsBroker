from __future__ import absolute_import

import socket
import ujson
from tornado import ioloop
from rsbroker.core.user import UserManager
from rsbroker.core.upstream import RTCWebSocketClient
from rsbroker.events.user import UserServerDispatch

dispatcher = UserServerDispatch()


class BrokerManager(RTCWebSocketClient, UserManager):
    _node_id = -1

    def dispatch(self, message):
        print 'message is..... ', message
        try:
            data = ujson.loads(message)
            print 'data', data
        except ValueError:
            raise ValueError("Invalid message!")

        else:
            if isinstance(data, dict):
                method = data.get("method")
                getattr(dispatcher, method, getattr(dispatcher, 'default'))(self, data)
            else:
                getattr(dispatcher, 'ping')(self, data)

    def connect(self, url, auto_reconnet=True, reconnet_interval=10):
        self.url_template = url
        ws_url = url % self._node_id
        super(BrokerManager, self).connect(url=ws_url)

    def reconnect(self):
        self.ws_url = self.url_template % self._node_id
        super(BrokerManager, self).reconnect()

    def run(self, rs_host='127.0.0.1:2332'):
        url_template = 'ws://%s/ws?' % (rs_host)
        ws_url = url_template + "&node=%s"
        # ws_url = 'ws://echo.websocket.org'
        self.connect(ws_url, auto_reconnet=True, reconnet_interval=10)


if __name__ == '__main__':
    bmanager = BrokerManager()
    bmanager.run()
    io_loop = ioloop.IOLoop.current().instance()
    io_loop.start()
