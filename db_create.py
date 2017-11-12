import os
import sys
from yphapp import db, create_app

if __name__ == '__main__':
    mode = os.getenv('YPH_FLASK_CONFIG_MOD') or 'development'#TODO上线改为production
    app = create_app(mode, True)
    if len(sys.argv) == 2 and sys.argv[1] == 'dropall':
        db.drop_all(app=app)
    else:
        db.create_all(app=app)
