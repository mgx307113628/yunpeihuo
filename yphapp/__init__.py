from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config

app = None
db = SQLAlchemy()

def create_app(config_name, crtdb=False):
    global app
    app = Flask(__name__)

    #配置
    cfg = config.CONFIG_CLASS[config_name]
    app.config.from_object(cfg)
    cfg.init_app(app)
    #额外配置
    app.config.from_envvar('YPH_FLASK_CONFIG_EX', True)

    #读取数据
    from . import data
    data.load_outter_data()

    #数据库
    db.init_app(app)
    from . import models

    #注册view
    from . import views
    from .views import order
    if not crtdb:
        with app.app_context():
            order.OrderPool().init_pool()

    return app
