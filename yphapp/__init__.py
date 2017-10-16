from flask import Flask

app = Flask(__name__)


from . import views
#print(views.index)
import yphapp
#print(yphapp.views.index)
