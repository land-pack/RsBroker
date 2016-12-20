import time
import logging

try:
    from util.tools import Log
except ImportError:
    logger = logging.getLogger(__name__)
else:
    logger = Log().getLog()


class TTLManager(object):
    """
    Set some thing during a time check it whether timeout!
    """

    def __init__(self, timeout=20, key_prefix='hb'):
        self._key_hash_time = {}
        self._id_hash_handler = {}
        self.timeout = timeout
        self.key_prefix = key_prefix

    def update(self, key):
        str_key = self.key_prefix + str(id(key))
        self._key_hash_time[str_key] = time.time()
        self._id_hash_handler[str_key] = key

    def is_expire(self, key):
        distance = time.time() - self._key_hash_time[key]
        if distance > self.timeout:
            return 'expire'
        else:
            return distance

    def clean_expire(self):
        del_key = []
        for key in self._key_hash_time:
            distance = self.is_expire(key)
            logger.debug("Loop [%s] check if any uid has expire [%s]-[%s], checking key [%s]", id(self), self.timeout,
                         distance, key)
            if distance is 'expire':
                handler = self._id_hash_handler[key]
                del_key.append(key)
                handler.clean_if_expire()
                logger.debug("the uid [%s]has  expire!", handler.uid)

        for key in del_key:
            self._remove(key)

    def _remove(self, key):
        del self._key_hash_time[key]
        del self._id_hash_handler[key]

    def remove(self, handler):
        str_key = self.key_prefix + str(id(handler))
        self._remove(str_key)
