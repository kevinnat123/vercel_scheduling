from flask import Blueprint, render_template, jsonify
from dao.first import get_data

main_routes = Blueprint('main_routes', __name__)

@main_routes.route("/")
def home():
    # Ambil data dari database
    data = get_data()
    return render_template("index.html")

@main_routes.route('/user', methods=["POST"])
def user():
    # Ambil data dari database
    data = get_data()
    return jsonify({ 'data': data })
