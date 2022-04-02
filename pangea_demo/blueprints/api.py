import io

from flask import (
    request,
    Blueprint,
    send_file,
    jsonify,
)
from pangea_demo.point_tools import fit_points, render_points, Point

api = Blueprint(
    "api",
    __name__,
    template_folder="templates",
    static_url_path="",
    static_folder="static",
)


@api.route("/render/", methods=["POST"])
def render_data():
    try:
        dims = (320, 320)
        req_data = request.json
        points = req_data.get("points", [])
        points = [Point(*p) for p in points]
        fit_params = req_data.get("params", {})
        img = render_points(points, fit_params, dims=dims)
        data = io.BytesIO()
        img.save(data, "PNG")
        data.seek(0)
    except Exception as e:
        return jsonify(error=str(e)), 400
    return send_file(data, mimetype="image/png")


@api.route("/fit/", methods=["POST"])
def fit_data():
    try:
        req_data = request.json
        points = req_data.get("points", [])
        if points:
            fit_params = fit_points(points)
        else:
            raise Exception("Error: No point data provided")
    except Exception as e:
        return e, 400
    return fit_params  # TODO: fix serialization
