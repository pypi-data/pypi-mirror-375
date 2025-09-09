import json
import logging
import os

from fastapi import status

from app.config import API_DB_JSON_FILENAME
from app.handlers.commons import convert_csv_bytes_to_json, to_kebabCase
from app.handlers.exceptions import APIException
from app.handlers.resources import get_id_attr
from app.handlers.validators import (
    validate_id_name_for_resource,
    validate_id_on_data,
    validate_resource_name,
)
from app.models.db_json_content import (
    DB_RESOURCE_ID_NONEXISTENT,
    DB_RESOURCE_ID_NOT_FOUND,
    DB_RESOURCE_NOT_FOUND,
    JsonContentModel,
)

logger = logging.getLogger("uvicorn")


class ResourcesController:
    json_content_mdl: JsonContentModel
    page: int = 1
    limit: int = 10

    def __init__(self):
        self.json_content_mdl: JsonContentModel = JsonContentModel(API_DB_JSON_FILENAME)

    def get_resources_list(self):
        resources_list = self.json_content_mdl.get_resources_list()
        return resources_list

    def get_resource_data(self, resource, page, limit):
        result: dict = self.json_content_mdl.get_data_by_resource_name(
            resource, page, limit
        )
        if not result:
            message = f"Resource ({resource}) not found."
            logger.error(message)
            raise APIException(status_code=status.HTTP_404_NOT_FOUND, message=message)

        return result

    def retrieve_resources_by_id(self, resource, id: int | str):
        result = self.json_content_mdl.get_data_resource_by_id(resource, id)
        if result is DB_RESOURCE_NOT_FOUND:
            message = f"Resource ({resource}) not found."
            logger.error(message)
            raise APIException(status_code=status.HTTP_404_NOT_FOUND, message=message)

        if result is DB_RESOURCE_ID_NONEXISTENT:
            message = f"The {resource} resource has not an 'id' like attribute."
            logger.error(message)
            raise APIException(status_code=status.HTTP_404_NOT_FOUND, message=message)

        if not result:
            message = f"Data with id {id} not found for the {resource} resource."
            logger.error(message)
            raise APIException(status_code=status.HTTP_404_NOT_FOUND, message=message)

        return result

    def put_resources_data_by_id(self, resource: str, id: int | str, new_data: dict):
        id_key = get_id_attr(new_data)
        validate_resource_name(resource)
        validate_id_name_for_resource(id)
        validate_id_on_data(new_data, id)

        logger.warning(
            "Using ID-like '{}' to update the resource '{}'s data.".format(
                json.dumps({id_key: id}), resource
            )
        )

        result = self.json_content_mdl.save_data_resource(
            resource, id_key, id, new_data
        )

        logger.info(
            "JSON DB file updated for resource {} {} ID.".format(
                json.dumps({id_key: id}), resource
            )
        )

        return result

    def delete_resource_id(self, resource: str, id: int | str):
        validate_resource_name(resource)
        validate_id_name_for_resource(id)

        result = self.json_content_mdl.delete_resource_data_by_id(resource, id)
        if result is DB_RESOURCE_NOT_FOUND:
            message = f"Resource ({resource}) not found."
            logger.error(message)
            raise APIException(status_code=status.HTTP_404_NOT_FOUND, message=message)

        if result is DB_RESOURCE_ID_NONEXISTENT:
            message = f"The {resource} resource has not an 'id' like attribute."
            logger.error(message)
            raise APIException(status_code=status.HTTP_404_NOT_FOUND, message=message)

        if result is DB_RESOURCE_ID_NOT_FOUND:
            message = f"ID {id} not found for the {resource} resource."
            logger.error(message)
            raise APIException(status_code=status.HTTP_404_NOT_FOUND, message=message)

        return {"message": "Deleted data for the id resource.", "data": result}

    async def update_db_json_from_csv(self, csv_file):
        resource = csv_file.filename
        csv_data_bytes = await csv_file.read()
        await csv_file.close()

        resource = resource[:-4] if ".csv" in resource else resource
        resource = " ".join(resource.split("_"))
        resource = to_kebabCase(resource)

        obj_json: list[dict] = convert_csv_bytes_to_json(csv_data_bytes)
        db_json_data = {
            f"{resource}": obj_json,
        }

        os.makedirs(os.path.dirname(API_DB_JSON_FILENAME), exist_ok=True)

        with open(API_DB_JSON_FILENAME, mode="w+", encoding="utf-8") as jsonfile:
            json.dump(db_json_data, jsonfile, indent=4)

        self.json_content_mdl.set(db_json_data)

        return {
            "message": "Updated DB JSON ({}) from the {} content.".format(
                API_DB_JSON_FILENAME, csv_file.filename
            ),
            f"{resource}": obj_json[:5],
        }
