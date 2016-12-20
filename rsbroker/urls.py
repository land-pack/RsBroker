from __future__ import absolute_import

import os

from tornado.web import StaticFileHandler

from rsbroker.views import websocket
from rsbroker.views.error import NotFoundErrorHandler

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static")
)

handlers = [
    # Http api

    # Events WebSocket API
    (r"/api/ws", websocket.BrokerServerHandler),

    # Static
    (r"/static/(.*)", StaticFileHandler),

    # Error
    (r".*", NotFoundErrorHandler)
]
