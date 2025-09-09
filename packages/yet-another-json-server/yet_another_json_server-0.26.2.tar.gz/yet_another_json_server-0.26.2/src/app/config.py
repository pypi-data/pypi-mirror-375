from dotenv import dotenv_values

_CONFIG = dotenv_values(".env")

if "APP_JSON_FILENAME" not in _CONFIG:
    _CONFIG["APP_JSON_FILENAME"] = "data/db.json"

if "APP_PORT" not in _CONFIG:

    _CONFIG["APP_PORT"] = "8000"

API_DB_JSON_FILENAME = _CONFIG["APP_JSON_FILENAME"]
API_PORT = int(_CONFIG["APP_PORT"])
