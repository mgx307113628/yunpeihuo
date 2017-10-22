############################### MethodView sample #################################
from flask.views import MethodView

class UserAPI(MethodView):

    def get(self, user_id):
        if user_id is None:
            # 返回一个包含所有用户的列表
            pass
        else:
            # 显示一个用户
            pass

    def post(self):
        # 创建一个新用户
        pass

    def delete(self, user_id):
        # 删除一个用户
        pass

    def put(self, user_id):
        # update a single user
        pass
############################### Blueprint sample #################################
from flask import Blueprint

user_page = Blueprint('usr', __name__) 

@user_page.route('/<int:userid>', methods=['GET'])
def user_show(userid):
    return "User ID: %d"%userid

############################### jsonity sample #################################
from flask import json, request, jsonify
from .. import app

@app.route('/')
def hello_world():
    data = request.get_json(True)
    return jsonify(code='Hello World!')

############################### views.__init__.py sample #################################
from .. import app

def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])
from . import index

from . import user
app.register_blueprint(user.user_page, url_prefix='/user')

from . import order
register_api(order.OrderAPI, 'user_api', '/users/', pk='user_id')
