from flask import Flask
from flask_cors import CORS
import os
from functools import wraps
from flask import Flask, request, json, jsonify
from fake_real_news_dectector import detect_real_or_fake_news
from werkzeug.exceptions import BadRequest
from jsonschema import validate, ValidationError

app = Flask(__name__)
cors = CORS(app)


def response_config(data, status_code, mime_type):
    return app.response_class(
        response=json.dumps(data), status=status_code, mimetype=mime_type
    )


app.config["JSON_SCHEMA"] = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "number", "minimum": 0},
            "text": {"type": "string", "minLength": 1},
            "class": {"type": "string"},
        },
        "required": ["id", "text"],
    },
}


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            request.json
        except BadRequest as e:
            data = {"Message": "400 Bad Request: Payload must be a valid json"}
            return response_config(data, 400, "application/json")
        return f(*args, **kw)

    return wrapper


def validate_schema(schema_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            try:
                validate(request.json, app.config[schema_name])
            except ValidationError as e:
                data = {"Message": str(e.message)}
                return response_config(data, 400, "application/json")
            return f(*args, **kw)

        return wrapper

    return decorator


@app.route("/api/detect-news-validation", methods=["POST"])
@validate_json
@validate_schema("JSON_SCHEMA")
def get_text():
    try:
        content = request.json

        res = detect_real_or_fake_news(content)

        return response_config(res, 200, "application/json")

    except Exception as e:
        app.logger.error("Error : ", str(e))
        data = {"Message": str(e)}
        return response_config(data, 500, "application/json")


if __name__ == "__main__":
    app.run(port=8000, debug=False)
