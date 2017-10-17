from flask import Flask
import os
import config

app = Flask(__name__)

#配置
cfg = config.CONFIG_CLASS[os.getenv('YPH_FLASK_CONFIG_MOD') or 'development']
app.config.from_object(cfg)
cfg.init_app(app)
#额外配置
app.config.from_envvar('YPH_FLASK_CONFIG_EX', True)

#注册views
from . import views
