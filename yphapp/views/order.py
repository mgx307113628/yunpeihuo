from flask.views import MethodView

class OrderAPI(MethodView):

    def get(self, order_id):
        if order_id is None:
            # 返回一个包含所有用户的列表
            pass
        else:
            # 显示一个用户
            pass

    def post(self):
        # 创建一个新用户
        pass

    def delete(self, order_id):
        # 删除一个用户
        pass

    def put(self, order_id):
        # update a single user
        pass

