import ujson
from rsbroker.core.user import UserManager


class DispatchResponse(object):
    def write(self, status, mid, body):
        """
        :param status: request status code (100 ok)
        :param mid: request message id
        :param body: request body
        :return: write to `response` property!
        """
        response = {"status": str(status), "mid": str(mid), "body": body}
        self.response = ujson.dumps(response)


class UserServerDispatch(DispatchResponse):
    def ping(self, handler, body):
        # TODO update heart beat ttl
        print 'recv ping'

    def default(self, handler, body):
        pass
