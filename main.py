from api_handler import ApiHandler, states
import time

if __name__ == "__main__":
    
    def sleep():
        time.sleep(3)

    schema_version = "69.0"
    schema_name = "schema_name" + schema_version
    schema_tag = "schema_tag" + schema_version

    # Create handler instances for both mobile and desktop
    mobile = ApiHandler("localhost", 7003)
    desktop = ApiHandler("localhost", 7001)

    # Create a auto-accept invitation on the mobile ACA-PY
    desktop_conn_id, invitation = desktop.create_invitation(
        alias="Mobile_conn",
        multi_use=False,
        auto_accept=False
    )

    # receive and auto accept the invitation on the desktop
    mobile_conn_id = mobile.receive_invitation(
        invitation_url=invitation,
        alias="Desktop_conn", auto_accept=False
    )

    print(f"mobile  -> connection id: {mobile_conn_id}")
    print(f"desktop -> connection id: {desktop_conn_id}")
    mobile.accept_invitation(mobile_conn_id)
    sleep()
    desktop.accept_request(desktop_conn_id)
    sleep()

    # Check the connection state
    while desktop.get_connection_state(desktop_conn_id) != states["active"]:
        print("Connection state is not active...")
        sleep()
    print("Connection state is active!")

    # Create schema
    schema = desktop.create_schema(
        schema_name=schema_name,
        schema_version=schema_version,
        attributes=["score", "high_score"]
    )
    print(f"desktop -> schema id: {schema['id']}")
    print("Creating credential definition, please have patients...")
    # Create cred definition with test schema id
    cred_def_id = desktop.create_credential_definition(
        schema_id=schema["id"],
        schema_tag=schema_tag,
        support_revocation=False
    )
    print(f"desktop -> credential def id: {cred_def_id}")

    # Create a revocation registry for the given credential definition id
    # desktop.create_revocation_registry(cred_def_id=cred_def_id)

    # Create an ?issuable? credential
    credential = desktop.issue_credential(
        conn_id=desktop_conn_id,
        cred_def_id=cred_def_id,
        attributes=[
            {"name": "score", "value": "12"},
            {"name": "high_score", "value": "300"}],
        schema=schema
    )
    print(f"desktop -> credential exchange id: {credential['credential_exchange_id']}")

    # Wait a couple of seconds to let the mobile agent actually receive and process the credential
    sleep()
    # Get credentials om mobile agent
    credentials = mobile.get_credentials()

    print(f"mobile  -> there are {len(credentials['results'])} credential(s)")
    print(f"mobile  -> {credentials['results'][0]['attrs']}")

    # Sends a proof request to mobile agent
    print("Sending proof request to mobile...")
    desktop_pres_ex_id = desktop.send_proof_request(
        conn_id=desktop_conn_id,
        requested_attributes={"score_attrs":{"name":"score", "restrictions": [{"schema_name":schema_name, "schema_version": schema_version}]}},
        requested_predicates={"high_score_pred":{"name":"high_score", "p_type": ">=", "p_value":250, "restrictions": [{"schema_name":schema_name, "schema_version": schema_version}]}}
    )
    print(f"desktop -> presentation exchange id: {desktop_pres_ex_id}")
    # TODO: Retreive proof /present-proof/{pres_ex_id}

    # Wait a couple of seconds to let the mobile agent actually receive and process the proposal
    sleep()
    print("Sending presentation from mobile to desktop")
    pres_response = mobile.send_presentation(
        pres_ex_id=mobile.get_pres_exchange_id(),
        requested_attributes={"score_attrs":{"cred_id":credentials['results'][0]['referent'], "revealed":True}},
        requested_predicates={"high_score_pred":{"cred_id":credentials['results'][0]['referent']}},
        self_attested_attributes={}
    )
    print("mobile  -> Proof has been sent" if len(pres_response['presentation']['proof']['proofs']) else "Proof has not been sent :-(")
    sleep()
    print("verifying the presentation...")
    res = desktop.verify_presentation(pres_ex_id=desktop_pres_ex_id)
    print("desktop -> proof has been verified" if bool(res) else "Proof has not been verified :(")




