from .. import app

def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])

from . import user
app.register_blueprint(user.bp_user, url_prefix='/user')

from . import order
app.register_blueprint(order.bp_order, url_prefix='/order')

#if app.config['DEBUG'] == True: #TODO 上线删除
#    from . import sample
