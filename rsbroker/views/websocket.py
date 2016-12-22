from __future__ import absolute_import

import logging
import traceback
import ujson
from tornado import websocket
from tornado import ioloop
from rsbroker.events.user import UserServerDispatch
from rsbroker.core.main import BrokerManager
from rsbroker.core.utils import TTLManager

logger = logging.getLogger(__name__)
broker_server_dispatch = UserServerDispatch()
broker_manager = BrokerManager()

ttl_user_behaviour = TTLManager(timeout=120, key_prefix='hv')
ioloop.PeriodicCallback(ttl_user_behaviour.clean_expire, 5000).start()

ttl_heart_beat = TTLManager(timeout=20, key_prefix='hb')
ioloop.PeriodicCallback(ttl_heart_beat.clean_expire, 1000).start()


class BrokerServerHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        """
        ws://127.0.0.1:3223/api/ws?node=-1&room=0&uid=123456
        :return:
        """
        print 'remote ip', self.request.remote_ip
        print 'remote host', self.request.host
        setattr(self, 'room', self.get_argument("room"))
        setattr(self, 'uid', self.get_argument("uid"))
        try:
            ni = broker_manager.register(obj=self)
        except (ValueError, TypeError):
            self.on_close()
        else:
            self.write_message(ujson.dumps({'method': 'connect', 'node': ni.node}))
            ttl_heart_beat.update(self)
            ttl_user_behaviour.update(self)
            setattr(self, 'ttl', ttl_user_behaviour)

    def on_message(self, message):
        """
        :param message: A dict type, as below example:
        {
            "method": "check_in",
            "body":{}
        }
        :return: write thing back
        """
        print 'message is>>>>', message
        try:
            data = ujson.loads(message)
            method = data.get("method")
            body = data.get("body")
        except TypeError:
            if 'p' in message:
                ttl_heart_beat.update(self)
                response = 'q'
            else:
                raise ValueError("Invalid request")
        else:
            getattr(broker_server_dispatch, method, getattr(broker_server_dispatch, "default"))(body)
            response = broker_server_dispatch.response
        finally:
            self.write_message(response)

    def on_close(self):
        try:
            broker_manager.unregister(obj=self)
        except (KeyError, TypeError):
            logger.info('websocket close!')
        else:
            ttl_heart_beat.remove(self)
            ttl_user_behaviour.remove(self)
        finally:
            self.close()

    def clean_if_expire(self):
        logger.debug("Clean Bad Websocket connect")
        try:
            response = {"messagetype": "kick_off", "messageid": "2016", "body": {}}
            self.write_message(ujson.dumps(response))
            self.on_close()
        except Exception as ex:
            logger.error(traceback.format_exc())
