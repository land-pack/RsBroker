from __future__ import absolute_import

import logging

from functools import partial
import tornado.web
from concurrent.futures import ThreadPoolExecutor

from tornado import ioloop
from tornado.httpserver import HTTPServer

logger = logging.getLogger(__name__)


class RsBroker(tornado.web.Application):
    pool_executor_cls = ThreadPoolExecutor
    max_workers = 4

    def __init__(self, options=None, io_loop=None, handlers=None, **kwargs):
        kwargs.update(handlers=handlers)
        super(RsBroker, self).__init__(**kwargs)
        self.options = options
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.started = False
        self.debug = True

    def start(self):
        self.pool = self.pool_executor_cls(max_workers=self.max_workers)
        if not self.options.unix_socket:
            self.listen(self.options.RPORT, address=self.options.address)
        else:
            from tornado.netutil import bind_unix_socket
            server = HTTPServer(self)
            socket = bind_unix_socket(self.options.unix_socket)
            server.add_socket(socket)
        # ioloop.PeriodicCallback(RoomManager.loop_check_ttl, 1000).start()
        self.started = True
        self.io_loop.start()

    def stop(self):
        if self.started:
            self.pool.shutdown(wait=False)
            self.started = False

    def delay(self, method, *args, **kwargs):
        return self.pool.submit(partial(method, *args, **kwargs))
