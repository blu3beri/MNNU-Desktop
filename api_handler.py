import requests
import base64
import ast
from typing import Tuple

endpoints = {
    "create_invitation": "/connections/create-invitation",
    "receive_invitation": "/connections/receive-invitation",
    "base_connections": "/connections/",
    "accept_invitation":"/accept-invitation",
    "accept_request":"/accept-request",
    "issue_credential": "/issue-credential/send",
    "create_registry": "/revocation/create-registry",
    "get_credentials": "/credentials",
    "send_proposal": "/present-proof/send-request",
    "base_proof": "/present-proof/records/",
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
        params = {
            "alias": alias,
            "auto_accept": f"{self.format_bool(auto_accept)}",
            "multi_use": f"{self.format_bool(multi_use)}"
        }
        response = requests.post(
            f"{self.__api_url}{endpoints['create_invitation']}", params=params).json()
        # Return the connection id and decoded invitation url
        return response['connection_id'], ast.literal_eval(
            base64.b64decode(response['invitation_url'].split("c_i=")[1]).decode('utf-8'))

    def receive_invitation(self, invitation_url: dict, alias: str, auto_accept: bool) -> str:
        params = {"alias": alias,
                  "auto_accept": f"{self.format_bool(auto_accept)}"
                  }
        response = requests.post(
            f"{self.__api_url}{endpoints['receive_invitation']}", params=params, json=invitation_url)
        return response.json()['connection_id']

    def accept_invitation(self, conn_id: str) -> dict:
        requests.post(f"{self.__api_url}{endpoints['base_connections']}{conn_id}{endpoints['accept_invitation']}")

    def accept_request(self, conn_id: str) -> dict:
        requests.post(f"{self.__api_url}{endpoints['base_connections']}{conn_id}{endpoints['accept_request']}")

    def get_connection_state(self, connection_id: str) -> int:
        response = requests.get(
            f"{self.__api_url}/connections/{connection_id}").json()
        return states[response['state']]

    def create_schema(self, schema_name: str, schema_version: str, attributes: list) -> dict:
        schema = {
            "attributes": attributes,
            "schema_name": schema_name,
            "schema_version": schema_version
        }
        response = requests.post(f"{self.__api_url}/schemas", json=schema)
        return response.json()['schema']

    def create_credential_definition(self, schema_id: str, schema_tag: str, support_revocation: bool = True) -> str:
        cred_def = {
            "schema_id": schema_id,
            "tag": schema_tag,
        }
        if support_revocation:
            cred_def["revocation_registry_size"] = 1000
            cred_def["support_revocation"] = "true"
        response = requests.post(
            f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        # retry creating credential definition if response code is not 200
        # because of weird ACA-PY error 400 bug
        while response.status_code != 200:
            response = requests.post(
                f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        return response.json()["credential_definition_id"]

    def create_revocation_registry(self, cred_def_id: str) -> None:
        registry = {
            "credential_definition_id": cred_def_id,
            "max_cred_num": 1000
        }
        requests.post(f"{self.__api_url}{endpoints['create_registry']}", json=registry)
        return None

    def issue_credential(self, conn_id: str, cred_def_id: str, attributes: list, schema) -> dict:
        did = cred_def_id.split(":")[0]
        credential = {
            "auto_remove": "false",
            "comment": "string",
            "connection_id": conn_id,
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

    def get_credentials(self) -> dict:
        response = requests.get(f"{self.__api_url}{endpoints['get_credentials']}")
        return response.json()

    def send_proof_request(self, conn_id: str, requested_attributes: dict, requested_predicates: dict) -> str:
        proposal = {
                "comment": "Ik wil proof",
                "connection_id": conn_id,
                "proof_request": {
                    "name": "Het AIVD wil je locatie weten",
                    "requested_attributes": requested_attributes,
                    "requested_predicates": requested_predicates,
                    "version": "1.0"
                },
                "trace": "false"
        }
        
        response = requests.post(f"{self.__api_url}{endpoints['send_proposal']}",
                             json=proposal)        
        return response.json()['presentation_exchange_id']

    def get_pres_exchange_id(self):
        return requests.get(
            f"{self.__api_url}{endpoints['base_proof']}").json()['results'][0]['presentation_exchange_id']

    def send_presentation(self, pres_ex_id: str, requested_attributes: dict, requested_predicates: dict) -> dict:
        presentation = {
            "requested_attributes": requested_attributes,
            "requested_predicates": requested_predicates,
            "self_attested_attributes": {},
            "trace": "false",
        }
        response = requests.post(f"{self.__api_url}{endpoints['base_proof']}{pres_ex_id}/send-presentation", json=presentation)
        return response.json()


