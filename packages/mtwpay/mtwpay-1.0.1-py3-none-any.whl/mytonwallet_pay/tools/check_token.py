import ssl
from typing import TYPE_CHECKING
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import certifi
import requests

from mytonwallet_pay.methods import getMe
from mytonwallet_pay.types.Project import Project
from mytonwallet_pay.types.base import Response
from mytonwallet_pay.types.error import APIError

if TYPE_CHECKING:
    import mytonwallet_pay

def token_validate(mtw_pay: "mytonwallet_pay.MTWPay"):
    method = getMe.getMeMethod.__api_method__
    url = f"https://pay.mytonwallet.io/api/v1/{method}"

    data = {
        "accessToken": mtw_pay._token,
        "projectId": mtw_pay._project_id,
    }

    headers = {
        "X-Project-Api-Key": mtw_pay._token,
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=data, headers=headers, verify=certifi.where())
    except requests.RequestException as e:
        raise APIError(message=f"Request failed: {e}")

    try:
        resp = resp.text
    except HTTPError as e:
        resp = e.read()

    response = Response[Project].model_validate_json(
        resp,
        context={"client": mtw_pay},
    )
    if not response.ok:
        error = response.message
        raise APIError(message=error)
    return response.result
