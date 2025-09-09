import logging

from fastapi import status

from app.handlers.errors import APIErrorDetails, APIException
from app.handlers.resources import get_id_attr
from app.models.db_json_content import DB_RESOURCE_ID_NONEXISTENT

logger = logging.getLogger("uvicorn")


def validate_resource_name(resource: str):
    if not resource.replace("-", "_").isidentifier():
        message = "The resource name should be valid as an URI path."
        logger.error(message)
        raise APIException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
        )
    return True


def validate_id_name_for_resource(id: int | str):

    if (not id.isnumeric()) and (not (id[0] + id[1:].replace("-", "Z")).isalnum()):
        message = "The ID value must be a valid integer or alphanumeric string, even with '-' in it."
        logger.error(message)
        raise APIException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message=message
        )
    return True


def validate_id_on_data(new_data: dict, id: int | str):

    id_key = get_id_attr(new_data)
    if id_key is None:
        message = "The data structure has not an ID-like attribute."
        logger.error(message)
        raise APIException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message=message
        )

    if str(new_data.get(id_key)) != str(id):
        message = "Value for the ID-like ({}) should match the param ID value.".format(
            id_key
        )
        logger.error(message)
        details = [
            APIErrorDetails(
                field=str(id_key),
                issue="Param ID ({}) and the new ID data ({}) values must be equals.".format(
                    new_data.get(id_key), id
                ),
                location="params",
            )
        ]
        raise APIException(
            status_code=status.HTTP_409_CONFLICT, message=message, details=details
        )
    return True
