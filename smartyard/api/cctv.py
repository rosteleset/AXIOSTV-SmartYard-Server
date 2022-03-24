from flask import Blueprint, Response, abort, jsonify, request

from smartyard.utils import access_verification

cctv_branch = Blueprint("cctv", __name__, url_prefix="/cctv")


@cctv_branch.route("/all", methods=["POST"])
def all() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@cctv_branch.route("/camMap", methods=["POST"])
def cam_map() -> Response:
    access_verification(request.headers)
    return jsonify(
        {
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": [
                {
                    "id": "70",
                    "url": "https:\/\/fl2.lanta.me:8443\/91052",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "75",
                    "url": "https:\/\/fl2.lanta.me:8443\/91078",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "79",
                    "url": "https:\/\/fl2.lanta.me:8443\/91072",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "124",
                    "url": "https:\/\/fl2.lanta.me:8443\/95594",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "131",
                    "url": "https:\/\/fl2.lanta.me:8443\/91174",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "f",
                },
                {
                    "id": "343",
                    "url": "https:\/\/fl2.lanta.me:8443\/90753",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
            ],
        }
    )


@cctv_branch.route("/overview", methods=["POST"])
def overview() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@cctv_branch.route("/recDownload", methods=["POST"])
def rec_download() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@cctv_branch.route("/recPrepare", methods=["POST"])
def rec_prepare() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"


@cctv_branch.route("/youtube", methods=["POST"])
def youtube() -> str:
    access_verification(request.headers)

    request_data = request.get_json() or {}
    if not request_data:
        abort(
            422,
            {
                "code": 422,
                "name": "Unprocessable Entity",
                "message": "Необрабатываемый экземпляр",
            },
        )

    return "Hello, World!"
