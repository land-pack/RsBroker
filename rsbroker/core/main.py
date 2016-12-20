from __future__ import absolute_import

import socket
import ujson
from tornado import ioloop
from rsbroker.core.user import UserManager
from rsbroker.core.upstream import RTCWebSocketClient
from rsbroker.events.user import UserServerDispatch

dispatcher = UserServerDispatch()


class BrokerManager(RTCWebSocketClient, UserManager):
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

    def run(self, rsp=2332, port=9001, dst='127.0.0.1'):

        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(('www.baidu.com', 0))
        # ip = s.getsockname()[0]
        # url_template = 'ws://%s:%s/ws?ip=%s&port=%s' % (dst, rsp, ip, port)
        # ws_url = url_template + "&node=%s"
        ws_url = 'ws://echo.websocket.org'
        self.connect(ws_url, auto_reconnet=True, reconnet_interval=10)


if __name__ == '__main__':
    bmanager = BrokerManager()
    bmanager.run()
    io_loop = ioloop.IOLoop.current().instance()
    io_loop.start()
