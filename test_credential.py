from library.api_handler import ApiHandler, states
from credentials.schema_attributes import naw
import time

if __name__ == "__main__":
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

    time.sleep(3)

    desktop.accept_request(desktop_conn_id)

    time.sleep(3)

    # Check the connection state
    while desktop.get_connection_state(desktop_conn_id) != states["active"]:
        print("Connection state is not active...")
        time.sleep(3)
    print("-" * 50)
    print("Connection state is active!")
    print("-" * 50)

    # Create schema on mobile
    schema = mobile.create_schema(naw)
    # Create credential definition on mobile
    cred_def_id = mobile.create_credential_definition(schema["id"], naw["schema_name"], support_revocation=False)

    # Issue a NAW credential to desktop
    response = mobile.issue_credential(
        conn_id=mobile_conn_id,
        cred_def_id=cred_def_id,
        attributes=[
            {
                "name": "naam",
                "value": "Pietje"
            },
            {
                "name": "voorletters",
                "value": ""
            },
            {
                "name": "achternaam",
                "value": "Puk"
            },
            {
                "name": "geslacht",
                "value": ""
            },
            {
                "name": "geboortedatum",
                "value": ""
            },
            {
                "name": "geboorteland",
                "value": ""
            },
            {
                "name": "bsn",
                "value": ""
            },
            {
                "name": "geldigheid_id",
                "value": ""
            },
            {
                "name": "burgelijke_staat",
                "value": ""
            },
            {
                "name": "telefoonnummer",
                "value": ""
            },
            {
                "name": "email-adres",
                "value": ""
            },
            {
                "name": "straat",
                "value": ""
            },
            {
                "name": "huisnummer",
                "value": ""
            },
            {
                "name": "toevoeging",
                "value": ""
            },
            {
                "name": "postcode",
                "value": ""
            },
            {
                "name": "woonplaats",
                "value": ""
            },
            {
                "name": "provincie",
                "value": ""
            },
            {
                "name": "land",
                "value": ""
            },
            {
                "name": "polisnummer",
                "value": ""
            },
            {
                "name": "verzekeraar",
                "value": ""
            },
            {
                "name": "voornaam_mantelzorger",
                "value": ""
            },
            {
                "name": "tussenvoegsel_mantelzorger",
                "value": ""
            },
            {
                "name": "achternaam_mantelzorger",
                "value": ""
            },
            {
                "name": "telefoonnummer_mantelzorger",
                "value": ""
            },
            {
                "name": "mobielnummer_mantelzorger",
                "value": ""
            },
            {
                "name": "email-adres_mantelzorger",
                "value": ""
            },
            {
                "name": "voornaam_contactpersoon",
                "value": ""
            },
            {
                "name": "tussenvoegsel_contactpersoon",
                "value": ""
            },
            {
                "name": "achternaam_contactpersoon",
                "value": ""
            },
            {
                "name": "telefoonnummer_contactpersoon",
                "value": ""
            },
            {
                "name": "mobielnummer_contactpersoon",
                "value": ""
            },
            {
                "name": "email-adres_contactpersoon",
                "value": ""
            },
            {
                "name": "naam_huisarts",
                "value": ""
            },
            {
                "name": "straat_huisarts",
                "value": ""
            },
            {
                "name": "huisnnummer_huisarts",
                "value": ""
            },
            {
                "name": "toevoeging_huisarts",
                "value": ""
            },
            {
                "name": "telefoonnummer_huisarts",
                "value": ""
            },
            {
                "name": "agb-code_huisarts",
                "value": ""
            },
            {
                "name": "uzi-nummer_huisarts",
                "value": ""
            },
            {
                "name": "email-adres_huisarts",
                "value": ""
            }],
        schema=schema)
    print(f"Issue cred response: {response}")
    time.sleep(3)
    # Show credential on desktop
    print(desktop.get_credentials())
