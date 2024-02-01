
import jwt
MY_SECRET_KEY = "mykeyconstant"
ALGORIHKEY = "HS256"


def create_token(data: dict):
    token: str = jwt.encode(payload=data, key=MY_SECRET_KEY, algorithm=ALGORIHKEY)
    return token


def validate_token(token: str) -> dict:
    try:
        data: dict = jwt.decode(token, key=MY_SECRET_KEY, algorithms=ALGORIHKEY)
        return data
    except Exception:
        return {}
