from flask import Blueprint, send_from_directory
from flask import current_app as app

apispec_bp = Blueprint('apispec', __name__)


@apispec_bp.route('/')
def rapidoc():
    return send_from_directory(app.static_folder, 'rapidoc.html')


@apispec_bp.route('/js/')
def rapi_js():
    return send_from_directory(app.static_folder, 'rapidoc-min.js')
