import requests
import base64
import ast
import time
from typing import Tuple

endpoints = {
    "create_invitation": "/connections/create-invitation",
    "receive_invitation": "/connections/receive-invitation",
    "issue_credential": "/issue-credential/create"
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
        params = {"alias": alias,
                  "auto_accept": f"{self.format_bool(auto_accept)}", "multi_use": f"{self.format_bool(multi_use)}"}
        response = requests.post(
            f"{self.__api_url}{endpoints['create_invitation']}", params=params).json()
        # Return the connection id and decoded invitation url
        return response["connection_id"], ast.literal_eval(
            base64.b64decode(response["invitation_url"].split("c_i=")[1]).decode('utf-8'))

    def receive_invitation(self, invitation_url: dict, alias: str, auto_accept: bool) -> str:
        params = {"alias": alias,
                  "auto_accept": f"{self.format_bool(auto_accept)}"}
        response = requests.post(
            f"{self.__api_url}{endpoints['receive_invitation']}", params=params, json=invitation_url)
        return response.json()["connection_id"]

    def get_connection_state(self, connection_id: str) -> int:
        response = requests.get(
            f"{self.__api_url}/connections/{connection_id}").json()
        return states[response["state"]]

    def create_schema(self, schema_name: str, attributes: list) -> dict:
        schema = {
            "attributes": attributes,
            "schema_name": schema_name,
            "schema_version": "1.0"
        }
        response = requests.post(f"{self.__api_url}/schemas", json=schema)
        return response.json()["schema"]

    def create_credential_definition(self, schema_id: str, schema_tag: str, support_revocation: bool = True) -> str:
        cred_def = {
            "revocation_registry_size": 1000,
            "schema_id": schema_id,
            "support_revocation": self.format_bool(support_revocation),
            "tag": schema_tag
        }
        response = requests.post(
            f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        # retry creating credential definition if response code is not 200
        # because of weird ACA-PY error 400 bug
        while response.status_code != 200:
            response = requests.post(
                f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        return response.json()["credential_definition_id"]

    def create_issue_credential(self, conn_id: str, cred_def_id: str, attributes: list, schema):
        # TODO: SEND DID THE NORMAL WAY
        did = cred_def_id.split(":")[0]
        credential = {
            "auto_remove": "true",
            "comment": "string",
            # "connection_id": conn_id,
            "cred_def_id": cred_def_id,
            "credential_proposal": {
                "@type": "issue-credential/1.0/credential-preview",
                "attributes": attributes
            },
            "issuer_did": did,
            "schema_id": schema["id"],
            "schema_issuer_did": did,
            "schema_name": schema["name"],
            "schema_version": schema["version"],
            "trace": "false"
        }
        response = requests.post(f"{self.__api_url}{endpoints['issue_credential']}", json=credential)
        return response.json()


if __name__ == "__main__":
    # Create handler instances for both mobile and desktop
    mobile = ApiHandler("localhost", 7003)
    desktop = ApiHandler("localhost", 7001)

    # Create a auto-accept invitation on the mobile ACA-PY
    conn_id, invitation = mobile.create_invitation(
        alias="Desktop_conn", multi_use=False, auto_accept=True)

    # receive and auto accept the invitation on the desktop
    desktop_conn_id = desktop.receive_invitation(
        invitation_url=invitation, alias="Mobile_conn", auto_accept=True)

    # Check the connection state
    while desktop.get_connection_state(desktop_conn_id) != states["active"]:
        print("Connection state is not active...")
        time.sleep(1)
    print("Connection state is active")

    # Create schema
    schema = desktop.create_schema(
        schema_name="schema 2", attributes=["score", "high_score"])
    print(f"Schema created id: {schema['id']}")

    # Create cred definition with test schema id
    cred_def_id = desktop.create_credential_definition(
        schema_id=schema["id"], schema_tag="test_cred10")
    print(f"Credential id: {cred_def_id}")

    # create an ?issuable? credential
    credential = desktop.create_issue_credential(conn_id=conn_id, cred_def_id=cred_def_id, attributes=[
        {"mime-type": "text/plain", "name": "score", "value": "12"},
        {"mime-type": "text/plain", "name": "high_score", "value": "30"}], schema=schema)
    print(f"Credential exchange id: {credential['credential_exchange_id']}")
