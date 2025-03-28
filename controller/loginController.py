from flask import Blueprint, render_template, jsonify
from dao.loginDao import First

main_routes = Blueprint('main_routes', __name__)
first_model = First()

@main_routes.route("/")
def home():
    return render_template("signin/index.html")

@main_routes.route('/user', methods=["POST"])
def user():
    # Ambil data dari database
    data = first_model.get_data()
    if data['status'] == True:
        print('output controller', data['data'])
        return jsonify({ 'data': data['data']['data'] })
