import requests
import base64
import ast
from typing import Tuple, Union

endpoints = {
    "create_invitation": "/connections/create-invitation",
    "receive_invitation": "/connections/receive-invitation",
    "base_connections": "/connections/",
    "accept_invitation": "/accept-invitation",
    "accept_request": "/accept-request",
    "issue_credential": "/issue-credential/send",
    "create_registry": "/revocation/create-registry",
    "get_credentials": "/credentials",
    "send_proposal": "/present-proof/send-request",
    "base_proof": "/present-proof/records",
    "verify_presentation": "/verify-presentation",
    "send_presentation": "/send-presentation"
}

states = {
    "request": 0,
    "active": 1,
    "invitation": 2
}


# TODO: Check if this class can be ran inside a thread so the program doesn't hang when ACA-PY instance is offline
class ApiHandler:
    def __init__(self, api_url: str, port: int):
        """
        ApiHandler constructor
        :param api_url: The ACA-Py instance url as a str
        :param port: The ACA-Py instance port as a int
        """
        self.__api_url = f"http://{api_url}:{port}"

    @staticmethod
    def format_bool(x: bool) -> str:
        """
        Format bool as a str
        :param x: The bool
        :return: The bool as a str
        """
        return str(x).lower() if isinstance(x, bool) else x

    def set_url(self, api_url: str, port: int) -> None:
        """
        Configure the ACA-Py instance url and port
        :param api_url: The url as a str
        :param port: The port as a int
        :return: None
        """
        self.__api_url = f"http://{api_url}:{port}"

    def test_connection(self) -> bool:
        """
        Test the connection with the ACA-Py instance
        :return: True if the connection is successful, False if not
        """
        try:
            response = requests.get(f"{self.__api_url}/status")
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.ConnectionError as e:
            print("connection refused")
            return False

    def create_invitation(self, alias: str, multi_use: bool, auto_accept: bool) -> Tuple[str, str]:
        """
        Create a connection invitation
        :param alias: The alias to give to the connection as a str
        :param multi_use: Can this invite be used multiple times?
        :param auto_accept: Auto accept connection handshake?
        :return: A tuple containing the connection id and base64 encoded invite url
        """
        params = {
            "alias": alias,
            "auto_accept": f"{self.format_bool(auto_accept)}",
            "multi_use": f"{self.format_bool(multi_use)}"
        }
        response = requests.post(f"{self.__api_url}{endpoints['create_invitation']}", params=params).json()
        # Return the connection id and decoded invitation url
        return response['connection_id'], response['invitation_url'].split("c_i=")[1]

    def receive_invitation(self, invitation_url: str, alias: str, auto_accept: bool) -> str:
        """
        Receive invitation url
        :param invitation_url: The base64 encoded invite url str
        :param alias: The alias to give to the connection as a str
        :param auto_accept: Auto accept connection handshake?
        :return: The connection id as a str
        """
        params = {"alias": alias, "auto_accept": f"{self.format_bool(auto_accept)}"}
        decoded_url = ast.literal_eval(base64.b64decode(invitation_url).decode('utf-8'))
        response = requests.post(
            f"{self.__api_url}{endpoints['receive_invitation']}", params=params, json=decoded_url)
        return response.json()['connection_id']

    def accept_invitation(self, conn_id: str) -> None:
        """
        Accept the invitation of the given conn id
        This needs to be done when auto-accept is disabled and only needs to be done by the receiver of the invitation
        :param conn_id: The connection id of the connection to accept
        :return: None
        """
        requests.post(f"{self.__api_url}{endpoints['base_connections']}{conn_id}{endpoints['accept_invitation']}")

    def accept_request(self, conn_id: str) -> None:
        """
        Accept the connection request of the given conn id
        This needs to be done when auto-accept is disabled and only needs to be done by the invitation creator
        :param conn_id: The connection id of the connection to accept
        :return: None
        """
        requests.post(f"{self.__api_url}{endpoints['base_connections']}{conn_id}{endpoints['accept_request']}")

    def get_connection_state(self, connection_id: str) -> int:
        """
        Get the connection state of a given connection id
        :param connection_id: The connection id
        :return: The state (see states dict)
        """
        response = requests.get(f"{self.__api_url}/connections/{connection_id}").json()
        return states[response['state']]

    def get_agent_name(self) -> str:
        """
        Get the ACA-Py agent name
        :return: The agent name as a str
        """
        return requests.get(f"{self.__api_url}/status").json()["label"]

    def get_connections(self, alias: str = None, state: str = None) -> dict:
        """
        Get connection(s) by: alias, state or if both are left empty every connection
        :param alias: The alias to retrieve (optional)
        :param state: The state the connection needs to be in (optional), see states dict for possible options
        :return: A dict with the requested connections
        """
        params = {}
        if alias:
            params["alias"] = alias
        if state:
            params["state"] = state
        return requests.get(f"{self.__api_url}/connections", params=params).json()

    def get_connection_id(self, alias: str) -> str:
        """
        Get the connection id of a given alias
        :param alias: The requested connection id alias as a str
        :return: The connection id as a str
        """
        return self.get_connections(alias=alias)["results"][0]["connection_id"]

    def get_active_connection_aliases(self) -> list:
        """
        Retrieve the aliases of all active connections
        :return: The aliases inside a list
        """
        aliases = []
        # If there is no active connection, return an empty list
        if not self.test_connection():
            return aliases
        connections = self.get_connections(state="active")["results"]
        for connection in connections:
            # Check if the connection actually has an alias
            if "alias" not in connection:
                continue
            else:
                aliases.append(connection["alias"])
        return aliases

    def get_alias_by_conn_id(self, conn_id: str) -> Union[str, None]:
        """
        Get the alias of the given connection id
        :param conn_id: The connnection id where the alias needs to be retreived from
        :return: The alias as a str if found, None if not
        """
        connections = self.get_connections(state="active")["results"]
        for i in connections:
            if conn_id == i["connection_id"]:
                return i["alias"]
        return None

    def get_pending_connections(self) -> list:
        """
        Retrieve all pending connections
        :return: All pending connections (state=invitation) inside a list
        """
        pending = []
        connections = self.get_connections(state="invitation")["results"]
        for connection in connections:
            # If there is no alias then we skip it
            if "alias" not in connection:
                continue
            pending.append({
                "alias": connection["alias"],
                "created_at": connection["created_at"].split(".")[0],
                "connection_id": connection["connection_id"]
            })
        return pending

    def delete_connection(self, conn_id: str) -> bool:
        """
        Delete the connection with a given connection id
        :param conn_id: The connection id to delete
        :return: True if deletion is successful, False if not
        """
        # TODO: Check if there are any left over present-proof records corresponding to this connecton id
        #  (and possible other records)
        response = requests.delete(f"{self.__api_url}{endpoints['base_connections']}{conn_id}")
        if response.status_code == 200:
            return True
        return False

    def create_schema(self, schema: dict) -> dict:
        """
        Create a schema on the ACA-Py instance
        :param schema: The schema to create
        :return: The created schema as a dict
        """
        response = requests.post(f"{self.__api_url}/schemas", json=schema)
        return response.json()['schema']

    def get_schemas(self) -> list:
        """
        Get all schema's that are available on the ACA-Py instance
        :return: The schema's a a list
        """
        response = requests.get(f"{self.__api_url}/schemas/created").json()['schema_ids']
        return response

    def create_credential_definition(self, schema_id: str, schema_tag: str, support_revocation: bool = False) -> str:
        """
        Create a credential definition with the given schema id and schema tag, with optional revocation support
        NOTE: This function takes some time to execute might look like program is hanging
        :param schema_id: The schema id as a str
        :param schema_tag: The schema tag as a str
        :param support_revocation: Support credential revocation?
        :return: The created credential definition id
        """
        cred_def = {
            "schema_id": schema_id,
            "tag": schema_tag,
        }
        if support_revocation:
            cred_def["revocation_registry_size"] = 1000
            cred_def["support_revocation"] = "true"
        response = requests.post(f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        # retry creating credential definition if response code is not 200
        # because of weird ACA-PY error 400 bug
        while response.status_code != 200:
            response = requests.post(f"{self.__api_url}/credential-definitions", json=cred_def, timeout=60)
        return response.json()["credential_definition_id"]

    def issue_credential(self, conn_id: str, cred_def_id: str, attributes: list, schema: dict, comment: str = "") -> dict:
        """
        Issue a credential
        :param conn_id: The connection id to issue the credential to
        :param cred_def_id: The credential definition id
        :param attributes: The list of attributes, format: [{"name": "score", "value": "12"},...]
        :param schema: The corresponding schema of the credential you wish to issue
        :param comment: Optional comment to send with the credential
        :return: The issue credential json response
        """
        # Might cause issues if you want to use someone else's cred definition
        did = cred_def_id.split(":")[0]
        credential = {
            "auto_remove": "false",
            "comment": comment,
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
        return requests.post(f"{self.__api_url}{endpoints['issue_credential']}", json=credential).json()

    def get_credentials(self) -> dict:
        """
        Get the credentials of the ACA-Py instance
        :return: The credentials inside a dict
        """
        response = requests.get(f"{self.__api_url}{endpoints['get_credentials']}")
        return response.json()

    def send_proof_request(self, conn_id: str, requested_attributes: dict, requested_predicates: dict, name: str, comment: str) -> str:
        """
        Send a request for proof
        :param conn_id: The connection id of the connection where you wish to send the request to
        :param requested_attributes: The requested attributes where you want proof for
        :param requested_predicates: The requests predicates where you want proof for (optional, supply empty dict)
        :param name: The name of the proof request
        :param comment: Additional information
        :return: The send proof request json response
        """
        proposal = {
            "comment": "",
            "connection_id": conn_id,
            "proof_request": {
                "name": f"{name}:{comment}",
                "requested_attributes": requested_attributes,
                "requested_predicates": requested_predicates,
                "version": "1.0"
            },
            "trace": "false"
        }
        response = requests.post(f"{self.__api_url}{endpoints['send_proposal']}", json=proposal)
        return response.json()['presentation_exchange_id']

    def get_pending_proof_requests_send(self) -> list:
        """
        Get a list of pending proof requests that have been send
        :return: A list containing the pending proof requests
        """
        pending_req = []
        params = {"role": "verifier", "state": "request_sent"}
        response = requests.get(f"{self.__api_url}{endpoints['base_proof']}", params=params).json()["results"]
        for i in response:
            pending_req.append({
                "name": i["presentation_request"]["name"],
                "connection_id": i["connection_id"],
                "presentation_exchange_id": i["presentation_exchange_id"],
                "date_created": i["created_at"]
            })
        return pending_req

    def get_verified_proof_records(self, conn_id: str) -> dict:
        """
        Get a dict of verified proof records
        :param conn_id: The connection id where the proof records originated from
        :return: A dict with all the proof records from a given connection id
        """
        records = {}
        params = {
            "connection_id": conn_id,
            "state": "verified",
            "role": "verifier"
        }
        response = requests.get(f"{self.__api_url}{endpoints['base_proof']}", params=params).json()["results"]
        for result in response:
            name = result["presentation_request"]["name"].split(":")[0]
            revealed_attrs = result["presentation"]["requested_proof"]["revealed_attrs"]
            attributes = {}
            for key, value in revealed_attrs.items():
                attributes[key] = value["raw"]
            records[name] = attributes
        return records

    def get_proof_records(self, state: str, role: str = "verifier") -> list:
        """
        Get all proof records with a certain state
        :param state: The state of the proof record
        :param role: The role of our client default = verifier
        :return: The list of proof records with that state
        """
        records = []
        params = {
            "state": state,
            "role": role
        }
        response = requests.get(f"{self.__api_url}{endpoints['base_proof']}", params=params).json()["results"]
        for i in response:
            records.append({
                "connection_id": i["connection_id"],
                "type": i["presentation_request"]["name"].split(":")[0],
                "created_at": i["created_at"].split(".")[0],
                "state": i["state"],
                "pres_ex_id": i["presentation_exchange_id"]
            })
        return records

    def get_pres_exchange_id(self) -> str:
        """
        Get the first presentation exchange id from the response
        TODO: Refactor this function since it is hardcoded to always return the first response
        :return: The presentation exchange id as a string
        """
        response = requests.get(f"{self.__api_url}{endpoints['base_proof']}")
        return response.json()['results'][0]['presentation_exchange_id']

    def send_presentation(self, pres_ex_id: str, requested_attributes: dict, requested_predicates: dict,
                          self_attested_attributes: dict) -> dict:
        """
        Send a presentation as a response from a proof request
        :param pres_ex_id: The presentation exchange id of the originating proof request
        :param requested_attributes: The requested attributes of the proof request
        :param requested_predicates: The requested predicates of the proof request
        :param self_attested_attributes: Optional NOTE: not sure what it does, supply empty dict {}
        :return: The send presentation json response
        """
        presentation = {
            "requested_attributes": requested_attributes,
            "requested_predicates": requested_predicates,
            "self_attested_attributes": self_attested_attributes,
            "trace": "false",
        }
        response = requests.post(
            f"{self.__api_url}{endpoints['base_proof']}/{pres_ex_id}{endpoints['send_presentation']}",
            json=presentation)
        return response.json()

    def verify_presentation(self, pres_ex_id: str) -> dict:
        """
        Verify a received presentation
        :param pres_ex_id: The corresponding presentation exchange id you wish to verify
        :return: The verify presentation json response
        """
        return requests.post(
            f"{self.__api_url}{endpoints['base_proof']}/{pres_ex_id}{endpoints['verify_presentation']}").json()
