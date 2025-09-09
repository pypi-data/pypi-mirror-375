import json
import os

from app.config import API_DB_JSON_FILENAME
from app.handlers.resources import get_id_attr
from app.handlers.singleton import Singleton

DB_RESOURCE_NOT_FOUND = 0
DB_RESOURCE_ID_NONEXISTENT = 1
DB_RESOURCE_ID_NOT_FOUND = 2


class JsonContentModel(metaclass=Singleton):
    _json_data: dict

    def __init__(self, db_json_filename: str):
        self._db_json_filename = db_json_filename
        self._retrieve_db_json_content()

    def _init_db_json(self):

        db_sample_if_not_exists = {
            "yetAnotherJsonServerSample": [
                {
                    "companyId": 1,
                    "company": "Miller and Sons",
                    "city": "Johnborough",
                    "country": "New Caledonia",
                    "postcode": 5184,
                    "pricetag": 682668.58,
                },
                {
                    "companyId": 2,
                    "company": "Pitts LLC",
                    "city": "Frederickfurt",
                    "country": "Jamaica",
                    "postcode": 69412,
                    "pricetag": 248.23,
                },
                {
                    "companyId": 3,
                    "company": "Nguyen and Sons",
                    "city": "Yolandaside",
                    "country": "Cocos (Keeling) Islands",
                    "postcode": 58911,
                    "pricetag": 48859.55,
                },
                {
                    "companyId": 153,
                    "company": "Sullivan-Lynch",
                    "city": "South David",
                    "country": "Norway",
                    "postcode": 59906,
                    "pricetag": 48.75,
                },
                {
                    "companyId": 157,
                    "company": "Oconnell-Sullivan",
                    "city": "New Allisonfort",
                    "country": "Dominican Republic",
                    "postcode": 63476,
                    "pricetag": 348.79,
                },
            ],
            "posts": [{"id": 1, "title": "json-server", "author": "typicode"}],
            "comments": [{"id": 1, "body": "some comment", "postId": 1}],
            "products": [
                {
                    "id": 7,
                    "title": "Jeans",
                    "brand": "Gucci",
                    "price": 37,
                    "reviewScore": 1.3567503747,
                    "color": "White",
                    "size": "XL",
                    "image": "http://products.net/img/",
                },
                {
                    "productId": 375,
                    "title": "Dress",
                    "brand": "Adidas",
                    "price": 40,
                    "reviewScore": 1.0431592108,
                    "color": "Black",
                    "size": "XL",
                    "image": "http://products.net/img/",
                },
            ],
            "stoke-exchange": [
                {
                    "company": "Chuchu e Melão S/A",
                    "city": "Belo Horizonte",
                    "ceoUserId": "99273502-9448-4197-abc4-422d4c792264",
                    "state": "Minas Gerais",
                    "id": 17,
                    "country": "Brasil",
                    "postcode": 40256,
                    "idProduct": 19,
                    "priceTag": "45,593,820",
                    "shareValue": "617.00",
                }
            ],
        }

        if not os.path.exists(API_DB_JSON_FILENAME):
            os.makedirs(name=os.path.dirname(API_DB_JSON_FILENAME), exist_ok=True)
            with open(API_DB_JSON_FILENAME, mode="w+") as jsonfile:
                json.dump(db_sample_if_not_exists, jsonfile, indent=4)

    def get_resources_list(self):
        resources = self._json_data.keys()

        result = [{resource: len(self._json_data[resource])} for resource in resources]

        return result

    def get_data_by_resource_name(self, resource, page, limit):
        if resource not in self._json_data:
            return {}
        result = self._json_data[resource]

        low_limit = page * limit - limit
        high_limit = page * limit
        result = result[low_limit:high_limit]

        return result

    def get_data_resource_by_id(
        self, resource: str, id: int | str
    ) -> bool | None | dict:
        """
        Returns:
            - bool | None | dict: _Returns `RESOURCE_NOT_FOUND` if resource not found or
                `RESOURCE_ID_NONEXISTENT` if resource has not an ID-like attribute._
        """
        if resource not in self._json_data:
            return DB_RESOURCE_NOT_FOUND
        # Get the keys with the ID like in it, to get the first one,
        # e.g: 'id', 'idProduct', or 'productId'
        id_idx_zero = get_id_attr(self._json_data[resource][0])
        if not id_idx_zero:
            return DB_RESOURCE_ID_NONEXISTENT

        resource_data = self._json_data[resource]
        result = (
            list(filter(lambda r: r[id_idx_zero] == id, resource_data))
            if isinstance(id, str) and not id.isdigit()
            else list(filter(lambda r: r[id_idx_zero] == int(id), resource_data))
        )

        return result

    def set(self, json_data):
        self._json_data = json_data

    def _retrieve_db_json_content(self):
        if not os.path.exists(self._db_json_filename):
            self._init_db_json()
        with open(self._db_json_filename, mode="r") as db_json:
            self._json_data: dict[list[dict]] = json.load(db_json)

        return self._json_data

    def save_data_resource(
        self, resource: str, id_key: str, id: int | str, new_data: dict
    ) -> bool | None | dict:
        result = self.get_data_resource_by_id(resource, id)
        if result is DB_RESOURCE_NOT_FOUND:
            self._json_data[resource] = [new_data]
        else:
            r_index = None
            for index, r_data in enumerate(self._json_data[resource]):
                if str(r_data.get(id_key)) == str(id):
                    r_index = index
                    break

            if r_index is not None:
                self._json_data[resource][r_index] = new_data
            else:
                self._json_data[resource].append(new_data)

        result = self.get_data_resource_by_id(resource, id)

        self._write_db_json_content()

        return result

    def delete_resource_data_by_id(self, resource: str, id: int | str):
        result = []

        if resource not in self._json_data:
            return DB_RESOURCE_NOT_FOUND
        else:
            r_index = None
            if len(self._json_data[resource]) > 0:
                id_key = get_id_attr(self._json_data[resource][0])
                for index, r_data in enumerate(self._json_data[resource]):
                    if str(r_data.get(id_key)) == str(id):
                        r_index = index
                        break

            if r_index is not None:
                result = self._json_data[resource][r_index]
                self._json_data[resource].pop(r_index)

                if len(self._json_data[resource]) == 0:
                    self._json_data.pop(resource)

                self._write_db_json_content()
            else:
                return DB_RESOURCE_ID_NOT_FOUND

        return result

    def _write_db_json_content(self):
        with open(self._db_json_filename, mode="w", encoding="utf8") as db_json:
            json.dump(self._json_data, db_json, ensure_ascii=False, indent=2)
