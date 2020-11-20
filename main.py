from api_handler import ApiHandler, states
import time

if __name__ == "__main__":
    schema_version = "1.0"
    schema_name = "schema_name" + schema_version
    schema_tag = "schema_tag" + schema_version

    # Create handler instances for both mobile and desktop
    mobile = ApiHandler("localhost", 7003)
    desktop = ApiHandler("localhost", 7001)

    # Create a auto-accept invitation on the mobile ACA-PY
    mobile_conn_id, invitation = mobile.create_invitation(
        alias="Desktop_conn",
        multi_use=False,
        auto_accept=True
    )

    # receive and auto accept the invitation on the desktop
    desktop_conn_id = desktop.receive_invitation(
        invitation_url=invitation,
        alias="Mobile_conn", auto_accept=True
    )

    # Check the connection state
    while desktop.get_connection_state(desktop_conn_id) != states["active"]:
        print("Connection state is not active...")
        time.sleep(1)
    print("Connection state is active")

    # Create schema
    schema = desktop.create_schema(
        schema_name=schema_name,
        schema_version=schema_version,
        attributes=["score", "high_score"]
    )
    print(f"Schema id: {schema['id']}")
    print("Creating credential definition, please have patients...")
    # Create cred definition with test schema id
    cred_def_id = desktop.create_credential_definition(
        schema_id=schema["id"],
        schema_tag=schema_tag,
        support_revocation=False
    )
    print(f"Credential def id: {cred_def_id}")

    # Create a revocation registry for the given credential definition id
    # desktop.create_revocation_registry(cred_def_id=cred_def_id)

    # Create an ?issuable? credential
    credential = desktop.send_issue_credential(
        conn_id=desktop_conn_id,
        cred_def_id=cred_def_id,
        attributes=[
            {"mime-type": "text/plain", "name": "score", "value": "12"},
            {"mime-type": "text/plain", "name": "high_score", "value": "300"}],
        schema=schema
    )
    print(f"Credential exchange id: {credential['credential_exchange_id']}")

    # Wait a couple of seconds to let the mobile agent actually receive and process the credential
    time.sleep(2)
    # Get credentials om mobile agent
    credentials = mobile.get_credentials()
    print(f"There are {len(credentials['results'])} credential(s)\nfirst entry: {credentials['results'][0]['attrs']}")

    print("Sending proof request to mobile")
    pres_ex_id = desktop.send_proof_request(
        conn_id=desktop_conn_id,
        requested_attributes={"score_attrs":{"name":"score", "restrictions": [{"schema_name":schema_name, "schema_version": schema_version}]}},
        #requested_predicates={"additionalProp1": {"name": "high_score", "p_type": ">=", "p_value": 250}}
        requested_predicates={"high_score_attrs":{"name":"high_score", "p_type": ">=", "p_value":250, "restrictions": [{"schema_name":schema_name, "schema_version": schema_version}]}}
    )
    print(f"Presentation exchange id: {pres_ex_id}")

    # Wait a couple of seconds to let the mobile agent actually receive and process the proposal
    time.sleep(2)
    print("Sending presentation from mobile to desktop")
    # pres_response = mobile.send_presentation(
    #    pres_ex_id=mobile.get_pres_exchange_id(),
    #    requested_attributes={},
    #    requested_predicates={"additionalProp1": {"cred_id": credentials['results'][0]['referent']}},
    # )
    # print(f"Presentation response: {pres_response}")
