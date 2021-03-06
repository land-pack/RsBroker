from __future__ import absolute_import

from tornado.options import define
from tornado.options import options

DEFAULT_CONFIG_FILE = 'flowerconfig.py'

define("RPORT", default=23321,
       help="[Room Server] run on the given port", type=int)

define("PORT", default=23322,
       help="[Api Server] run on the given port", type=int)

define("address", default='',
       help="run on the given address", type=str)

define("unix_socket", default='',
       help="path to unix socket to bind", type=str)

define("debug", default=False,
       help="run in debug mode", type=bool)

default_options = options
