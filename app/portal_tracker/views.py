from flask import jsonify, request, Blueprint, render_template
import pandas as pd

tracker_endpoint = Blueprint("tracker", __name__)

@tracker_endpoint.route("/tracker", methods=['GET'])
def handler_tracker():

    return "futuro portal"

