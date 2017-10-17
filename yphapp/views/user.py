from flask import Blueprint

user_page = Blueprint('usr', __name__) 

@user_page.route('/<int:userid>', methods=['GET'])
def user_show(userid):
    return "User ID: %d"%userid
