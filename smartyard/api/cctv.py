from flask import Blueprint, Response, jsonify, request

from smartyard.utils import (access_verification, generate_video_token,
                             json_verification)

cctv_branch = Blueprint("cctv", __name__, url_prefix="/cctv")


@cctv_branch.route("/all", methods=["POST"])
@access_verification
@json_verification
def all() -> Response:
    strims = ["111111", "222222", "333333"]
    videotoken = generate_video_token(request.environ["USER_PHONE"], strims)
    response = {
        "code": 200,
        "name": "OK",
        "message": "Хорошо",
        "data": [
            {
                "id": 692,
                "name": "Пионерская 5б Вид сверху 2 - Тупик",
                "lat": "52.703267836456",
                "url": "https://vd.axiostv.ru/100001",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.4726675977",
            },
            {
                "id": 693,
                "name": "Пионерская 5б Вид сверху 3 - двор",
                "lat": "52.703500236158",
                "url": "https://fl2.lanta.me:8443/91165",
                "token": "3f627a87d2664f3176c3585cb9561b5a",
                "lon": "41.473222207278",
            },
            {
                "id": 723,
                "name": "Домофон Пионерская 5 б п 1",
                "lat": "52.703248663394",
                "url": "https://fl2.lanta.me:8443/89318",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.473443133291",
            },
            {
                "id": 694,
                "name": "Пионерская 5б Вид сверху 4 - парковка у ТП",
                "lat": "52.703443771131",
                "url": "https://fl2.lanta.me:8443/91171",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.473441666458",
            },
            {
                "id": 724,
                "name": "Домофон Пионерская 5 б п 2",
                "lat": "52.703204679595",
                "url": "https://fl2.lanta.me:8443/91071",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.473222898785",
            },
            {
                "id": 695,
                "name": "Пионерская 5б Въезд в тупик для чтения номеров",
                "lat": "52.703021201666",
                "url": "https://fl3.lanta.me:8443/91172",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.472768306267",
            },
            {
                "id": 725,
                "name": "Домофон Пионерская 5 б п 3",
                "lat": "52.703178916547",
                "url": "https://fl2.lanta.me:8443/91072",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.472994973883",
            },
            {
                "id": 696,
                "name": "Пионерская 5б Въезд во двор для чтения номеров",
                "lat": "52.703308087163",
                "url": "https://fl2.lanta.me:8443/91174",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.473656725138",
            },
            {
                "id": 726,
                "name": "Домофон Пионерская 5 б п 4",
                "lat": "52.703346026911",
                "url": "https://fl2.lanta.me:8443/91073",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.472863964736",
            },
            {
                "id": 697,
                "name": "Пионерская 5б Двор - вдоль проезда на север",
                "lat": "52.703443618763",
                "url": "https://fl2.lanta.me:8443/91176",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.4730289625",
            },
            {
                "id": 727,
                "name": "Домофон Пионерская 5 б п 5",
                "lat": "52.703531471559",
                "url": "https://fl2.lanta.me:8443/91074",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.47279571509",
            },
            {
                "id": 698,
                "name": "Пионерская 5б Двор - парковка у 5-го подъезда",
                "lat": "52.703597281681",
                "url": "https://fl2.lanta.me:8443/91177",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.472968256567",
            },
            {
                "id": 728,
                "name": "Домофон Пионерская 5 б Калитка",
                "lat": "52.703142017842",
                "url": "https://fl2.lanta.me:8443/91078",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.473720762879",
            },
            {
                "id": 699,
                "name": "Пионерская 5б Вид сверху 1 - Пионерская",
                "lat": "52.703042139774",
                "url": "https://fl2.lanta.me:8443/89312",
                "token": "a319639b20342a17c06aa51c12359f2a",
                "lon": "41.473282892257",
            },
        ],
    }

    return jsonify(response)


@cctv_branch.route("/camMap", methods=["POST"])
@access_verification
def cam_map() -> Response:
    return jsonify(
        response={
            "code": 200,
            "name": "OK",
            "message": "Хорошо",
            "data": [
                {
                    "id": "70",
                    "url": "https://fl2.lanta.me:8443/91052",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "75",
                    "url": "https://fl2.lanta.me:8443/91078",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "79",
                    "url": "https://fl2.lanta.me:8443/91072",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "124",
                    "url": "https://fl2.lanta.me:8443/95594",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
                {
                    "id": "131",
                    "url": "https://fl2.lanta.me:8443/91174",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "f",
                },
                {
                    "id": "343",
                    "url": "https://fl2.lanta.me:8443/90753",
                    "token": "acd0c17657395ff3f69d68e74907bb3a",
                    "frs": "t",
                },
            ],
        }
    )


@cctv_branch.route("/overview", methods=["POST"])
@access_verification
@json_verification
def overview() -> str:
    return "Hello, World!"


@cctv_branch.route("/recDownload", methods=["POST"])
@access_verification
@json_verification
def rec_download() -> str:
    return "Hello, World!"


@cctv_branch.route("/recPrepare", methods=["POST"])
@access_verification
@json_verification
def rec_prepare() -> str:
    return "Hello, World!"


@cctv_branch.route("/youtube", methods=["POST"])
@access_verification
@json_verification
def youtube() -> str:
    return "Hello, World!"
