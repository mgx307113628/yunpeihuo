from flask import Flask
import config

app = None

def create_app(config_name):
    global app
    app = Flask(__name__)

    #配置
    cfg = config.CONFIG_CLASS[config_name]
    app.config.from_object(cfg)
    cfg.init_app(app)
    #额外配置
    app.config.from_envvar('YPH_FLASK_CONFIG_EX', True)

    #注册view
    from . import views

    return app
