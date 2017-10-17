from .. import app
from . import index
from . import user

app.register_blueprint(user.user_page, url_prefix='/user')
