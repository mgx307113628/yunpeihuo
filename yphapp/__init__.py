from flask import Flask

app = Flask(__name__)
app.debug=True


from . import views
app.register_blueprint(views.user.user_page, url_prefix='/user')
