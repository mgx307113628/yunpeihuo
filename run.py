import yphapp
import os


if __name__ == "__main__":
    app = yphapp.create_app('development')
    app.run(host='0.0.0.0', port=443)
else:
    app = yphapp.create_app(os.getenv('YPH_FLASK_CONFIG_MOD') or 'development')#TODO 上线改为production
