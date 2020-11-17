import requests
import base64
import ast
from typing import Union, Tuple
import time

endpoints = {
    "create_invitation": "/connections/create-invitation",
    "receive_invitation": "/connections/receive-invitation"
}

states = {
    "request": 0,
    "active": 1,
    "invitation": 2
}


class ApiHandler:
    def __init__(self, api_url: str, port: int):
        self.__api_url = f"http://{api_url}:{port}"

    @staticmethod
    def format_bool(x):
        return str(x).lower() if isinstance(x, bool) else x

    def create_invitation(self, alias: str, multi_use: bool, auto_accept: bool) -> Tuple[str, dict]:
        params = {"alias": alias, "auto_accept": f"{self.format_bool(auto_accept)}", "multi_use": f"{self.format_bool(multi_use)}"}
        response = requests.post(f"{self.__api_url}{endpoints['create_invitation']}", params=params).json()
        # Return the connection id and decoded invitation url
        return response["connection_id"], ast.literal_eval(base64.b64decode(response["invitation_url"].split("c_i=")[1]).decode('utf-8'))

    def receive_invitation(self, invitation_url: dict, alias: str, auto_accept: bool) -> str:
        params = {"alias": alias, "auto_accept": f"{self.format_bool(auto_accept)}"}
        response = requests.post(f"{self.__api_url}{endpoints['receive_invitation']}", params=params, json=invitation_url)
        return response.json()["connection_id"]

    def get_connection_state(self, connection_id: str) -> int:
        response = requests.get(f"{self.__api_url}/connections/{connection_id}").json()
        return states[response["state"]]

    def create_schema(self, schema_name: str, attributes: list) -> str:
        schema = {
            "attributes": attributes,
            "schema_name": schema_name,
            "schema_version": "1.0"
        }
        response = requests.post(f"{self.__api_url}/schemas", json=schema)
        return response.json()["schema_id"]

    def create_credential_definition(self, schema_id: str, schema_tag: str, support_revocation: bool = True) -> str:
        cred_def = {
            "revocation_registry_size": 1000,
            "schema_id": schema_id,
            "support_revocation": self.format_bool(support_revocation),
            "tag": schema_tag
        }
        response = requests.post(f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        # retry creating credential definition if response code is not 200
        # because of weird ACA-PY error 400 bug
        while response.status_code != 200:
            response = requests.post(f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        return response.json()["credential_definition_id"]


if __name__ == "__main__":
    # Create handler instances for both mobile and desktop
    mobile = ApiHandler("localhost", 7003)
    desktop = ApiHandler("localhost", 7001)

    # Create a auto-accept invitation on the mobile ACA-PY
    conn_id, invitation = mobile.create_invitation(alias="Desktop_conn", multi_use=False, auto_accept=True)

    # receive and auto accept the invitation on the desktop
    desktop_conn_id = desktop.receive_invitation(invitation_url=invitation, alias="Mobile_conn", auto_accept=True)
    # Check the connection state
    while desktop.get_connection_state(desktop_conn_id) != states["active"]:
        print("Connection state is not active...")
        time.sleep(1)
    print("Connection state is active")
    # Create schema
    test_schema_id = desktop.create_schema(schema_name="Test schema", attributes=["score", "high_score"])
    print(f"Schema created id: {test_schema_id}")
    # Create cred definition with test schema id
    credential_id = desktop.create_credential_definition(schema_id=test_schema_id, schema_tag="test_cred10")
    print(f"Credential id: {credential_id}")
