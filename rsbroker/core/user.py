from __future__ import absolute_import

import ujson
from rsbroker.core.upstream import RTCWebSocketClient


class BaseUserManager(object):
    room_to_uid = {}
    uid_to_handler = {}

    def register(self, obj):
        """
        Dispatch all resource which user need!
        :param obj:
        :return:
        """
        raise NotImplementedError

    def unregister(self, obj):
        """
        Release all resource if user out!
        :param obj:
        :return:
        """
        raise NotImplementedError

    def send(self, request):
        """
        Send news to room-server by web socket!
        :param request: a dict type
        Example:
            {
                'method': 'check_in',
                'uid': uid
            }
        :return: a dict type
        Example:
            {
                'status': '100',
                'mid': '1001',
                'body': {'info':'check in failure'}
            }
        """
        raise NotImplementedError


class UserManager(BaseUserManager):
    """
    Implementation all declare method from parent class!
    """

    def register(self, obj):
        room = obj.room
        uid = obj.uid
        request = {'method': 'check_in', 'uid': uid}
        response = self.send(request)
        data = ujson.loads(response)
        mid = data.get("mid")
        if mid == "1001":
            # check in failure
            raise ValueError("Check in failure, no source for uid [%s]" % uid)
        else:
            if room in self.room_to_uid:
                self.room_to_uid[room].add(uid)
            else:
                self.room_to_uid[obj.room] = set()

            self.uid_to_handler[uid] = obj

    def unregister(self, obj):
        room = obj.room
        uid = obj.uid

        request = {'method': 'check_in', 'uid': uid}
        response = self.send(request)
        data = ujson.loads(response)
        mid = data.get("mid")
        if mid == '1003':
            raise ValueError("Check out failure, the user may already check out!")
        else:
            if room in self.room_to_uid:
                self.room_to_uid[room].remove(uid)

            if uid in self.uid_to_handler:
                del self.uid_to_handle[uid]
