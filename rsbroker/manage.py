from rsbroker.app import RsBroker
from options import options
from rsbroker.urls import settings
from rsbroker.urls import handlers

if __name__ == '__main__':
    rsbroker = RsBroker(options=options, handlers=handlers, **settings)
    rsbroker.start()
