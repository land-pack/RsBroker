import time
import logging
import ujson
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket

try:
    from util.tools import Log
except ImportError:
    logger = logging.getLogger(__name__)
else:
    logger = Log().getLog()

APPLICATION_JSON = 'application/json'
DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


class WebSocketClient(object):
    """Base for web socket clients.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    connect_timeout = DEFAULT_CONNECT_TIMEOUT
    request_timeout = DEFAULT_REQUEST_TIMEOUT

    _io_loop = ioloop.IOLoop.current()

    _ws_connection = None
    _connect_status = DISCONNECTED
    _node_id = -1

    @classmethod
    def connect(cls, url):
        """Connect to the server.
        :param str url: server URL.
        """
        cls._connect_status = cls.CONNECTING
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=cls.connect_timeout,
                                         request_timeout=cls.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(cls._io_loop, request)
        ws_conn.connect_future.add_done_callback(cls._connect_callback)

    @classmethod
    def send(cls, data):
        """Send message to the server
        :param str data: message.
        """
        if cls._ws_connection:
            cls._ws_connection.write_message(ujson.dumps(data))

    @classmethod
    def close(cls, reason=''):
        """Close connection.
        """

        if cls._connect_status != cls.DISCONNECTED:
            cls._connect_status = cls.DISCONNECTED
            cls._ws_connection and cls._ws_connection.close()
            cls._ws_connection = None
            cls.on_connection_close(reason)

    @gen.coroutine
    @classmethod
    def _connect_callback(cls, future):
        if future.exception() is None:
            cls._connect_status = cls.CONNECTED
            cls._ws_connection = future.result()
            cls.on_connection_success()
            cls._read_messages()
        else:
            cls.close(future.exception())

    @classmethod
    def is_connected(cls):
        return cls._ws_connection is not None

    @classmethod
    def _read_messages(cls):
        while True:
            msg = yield cls._ws_connection.read_message()
            if msg is None:
                cls.close()
                break
            cls.on_message(msg)

    @classmethod
    def on_message(cls, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """
        pass

    @classmethod
    def on_connection_success(cls):
        """This is called on successful connection ot the server.
        """
        pass

    @classmethod
    def on_connection_close(cls, reason):
        """This is called when server closed the connection.
        """
        pass


class RTCWebSocketClient(WebSocketClient):
    hb_msg = {'command': 'ping'}  # hearbeat
    message = ''
    heartbeat_interval = 3
    ws_url = None
    auto_reconnet = False
    last_active_time = 0
    pending_hb = None

    @classmethod
    def connect(cls, url, auto_reconnet=True, reconnet_interval=10):
        # cls.url_template = url
        # cls.ws_url = url % cls._node_id
        cls.ws_url = url
        cls.auto_reconnet = auto_reconnet
        cls.reconnect_interval = reconnet_interval
        super(RTCWebSocketClient, cls).connect(cls.ws_url)

    @classmethod
    def send(cls, msg):
        super(RTCWebSocketClient, cls).send(msg)
        cls.last_active_time = time.time()

    @classmethod
    def on_message(cls, msg):
        cls.last_active_time = time.time()
        cls.dispatch(msg)

    @classmethod
    def on_connection_success(cls):
        logger.info('Connect ...')
        cls.last_active_time = time.time()
        cls.send_heartbeat()

    @classmethod
    def on_connection_close(cls, reason):
        logger.warning('Connection closed reason=%s' % (reason,))
        cls.pending_hb and cls._io_loop.remove_timeout(cls.pending_hb)
        cls.reconnect()

    @classmethod
    def reconnect(self):
        logger.info('Reconnect')
        # TODO when reconnect the room server has trigger,
        # TODO the url should has new param ~~
        # self.ws_url = self.ws_recovery_url % self._nod_id
        logger.info("Send node id [%s] to remote server" % self._node_id)
        # self.ws_url = self.url_template % self._node_id
        if not self.is_connected() and self.auto_reconnet:
            self._io_loop.call_later(self.reconnect_interval,
                                     super(RTCWebSocketClient, self).connect, self.ws_url)

    @classmethod
    def send_heartbeat(self):
        if self.is_connected():
            now = time.time()
            if (now > self.last_active_time + self.heartbeat_interval):
                self.last_active_time = now
                self.send(self.hb_msg)

            self.pending_hb = self._io_loop.call_later(self.heartbeat_interval, self.send_heartbeat)

    @classmethod
    def dispatch(self, message):
        """
        You must  override this method!
        """
        # raise NotImplementedError
        print 'message', message


def main():
    io_loop = ioloop.IOLoop.instance()
    client = RTCWebSocketClient
    # ws_url = 'ws://127.0.0.1:8888/ws?ip=127.0.0.1&port=9001&mode=1'
    ws_url = 'ws://echo.websocket.org'
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
