import json
from os import stat
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = "mk-bike-system.us.auth0.com"
ALGORITHMS = ["RS256"]
API_AUDIENCE = "bikes"

## Define standard AuthError


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header


def get_token_auth_header():
    """Gets the token from the authorization header"""

    auth = request.headers.get("Authorization", None)

    # if no authorization present in header return 401
    if not auth:
        raise AuthError(
            {
                "code": "authorization_header_missing",
                "description": "Authorization header is expected",
            },
            401,
        )

    # Split token and check for bearer type, if not bearer return 401
    auth_parts = auth.split()
    if auth_parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must be bearer",
            },
            401,
        )
    # if the split of token only resulted in a list with len of 1 (part of auth is missing) return 401
    elif len(auth_parts) == 1:
        raise AuthError(
            {"code": "invalid_header", "description": "Token not found"}, 401
        )
    # if the split of token results in a list with len more than 2 (extra parts) return 401
    elif len(auth_parts) > 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization must be baerer token",
            },
            401,
        )

    # select token from auth
    token = auth_parts[1]

    return token


def check_permissions(permission, payload):
    """Checks for valid permissions"""

    # check for permissions list included in payload otherwise return 403
    print(permission)
    print(payload)
    if "permissions" not in payload:
        raise AuthError(
            {
                "code": "invalid_claims",
                "description": "Permissions not included in JWT",
            },
            403,
        )

    # check that permission in payload required to perform request is allowed otherwise return 403
    if permission not in payload["permissions"]:
        raise AuthError(
            {
                "code": "invalid_claims",
                "description": "Not permitted",
            },
            403,
        )
    return True


def verify_decode_jwt(token):
    """Decodes and parse jwt"""

    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwts = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    if "kid" not in unverified_header:
        raise AuthError(
            {"code": "invalid_header", "description": "Authorization malformed"}, 401
        )

    # loop over keys in jwts and parse parts
    for key in jwts["keys"]:

        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

        if rsa_key:
            # if jwt is decodeable return payload
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer=f"https://{AUTH0_DOMAIN}/",
                )
                return payload
            # if jwt is expired return 401
            except jwt.ExpiredSignatureError:
                raise AuthError(
                    {"code": "token_expired", "description": "token expired"}, 401
                )

            # if jwt looks for incorrect audience return 401
            except jwt.JWTClaimsError:
                raise AuthError(
                    {
                        "code": "invalid_claims",
                        "description": "Incorrect Claims. Please check audience and issuer.",
                    },
                    401,
                )

            # catch other jwt parsing error
            except Exception as e:
                print(e)
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Unable to parse authorization token",
                    },
                    400,
                )

        # if no keys are found raise error
        raise AuthError(
            {
                "code": "invalid_headers",
                "description": "unable to find the appropriate key",
            },
            400,
        )


### Create decorator to authorize certain actions on requests in app
def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # get token
            token = get_token_auth_header()
            # decode token
            payload = verify_decode_jwt(token)
            # validate permissions for token
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
