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
    def check_in(self, handler, body):
        uid = body.get("uid")
        if UserManager.check_in(uid):
            self.write(100, 1000, {'info': 'check in success'})
        else:
            UserManager.check_in(uid)
            self.write(100, 1001, {'info': 'check in failure'})

    def check_out(self, handler, body):
        uid = body.get("uid")
        UserManager.check_out(uid)
        self.write(100, 1002, {})

    def ping(self, handler, body):
        # TODO update heart beat ttl
        print 'recv ping'

    def default(self, handler, body):
        pass
