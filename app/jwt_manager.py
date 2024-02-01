from jwt import encode, decode

MY_SECRET_KEY = "mykeyconstant"
ALGORIHKEY = "HS256"


def create_token(data: dict):
    token: str = encode(payload=data, key=MY_SECRET_KEY, algorithm=ALGORIHKEY)
    return token


def validate_token(token: str) -> dict:
    try:
        data: dict = decode(token, key=MY_SECRET_KEY, algorithms=ALGORIHKEY)
        return data
    except Exception:
        return {}
