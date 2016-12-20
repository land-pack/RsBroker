from __future__ import absolute_import

from rsbroker.core.upstream import RTCWebSocketClient


class BaseUserManager(object):
    room_to_uid = {}
    uid_to_handler = {}
    websocket_connect = None

    @classmethod
    def register(cls, obj):
        raise NotImplementedError

    @classmethod
    def unregister(cls, obj):
        raise NotImplementedError


class UserManager(BaseUserManager, ):
    @classmethod
    def register(cls, obj):
        room = obj.room
        uid = obj.uid

        if room in cls.room_to_uid:
            cls.room_to_uid[room].add(uid)
        else:
            cls.room_to_uid[obj.room] = set()

        cls.uid_to_handler[uid] = obj

    @classmethod
    def unregister(cls, obj):
        room = obj.room
        uid = obj.uid

        if room in cls.room_to_uid:
            cls.room_to_uid[room].remove(uid)

        if uid in cls.uid_to_handler:
            del cls.uid_to_handle[uid]
