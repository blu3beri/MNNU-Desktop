from library.api_handler import ApiHandler, states
from credentials.schema_attributes import naw
import time

if __name__ == "__main__":
    # Create handler instances for both mobile and desktop
    mobile = ApiHandler("localhost", 7003)
    # --- Test to issue credential to itself, variable names are not correct! ---
    desktop = ApiHandler("localhost", 7003)

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
    schema = mobile.create_schema(schema=naw)
    # Create credential definition on mobile
    cred_def_id = mobile.create_credential_definition(
        schema_id=schema["id"],
        schema_tag=naw["schema_name"],
        support_revocation=False
    )

    time.sleep(4)

    # Issue a NAW credential to desktop
    response = mobile.issue_credential(
        conn_id=mobile_conn_id,
        cred_def_id=cred_def_id,
        attributes=[
            {"name": "naam", "value": "Pietje"},
            {"name": "voorletters", "value": "a"},
            {"name": "achternaam", "value": "Puk"},
            {"name": "geslacht", "value": "a"},
            {"name": "geboortedatum", "value": "Vandaag"},
            {"name": "geboorteland", "value": "a"},
            {"name": "bsn", "value": "a"},
            {"name": "geldigheid_id", "value": "a"},
            {"name": "burgelijke_staat", "value": "a"},
            {"name": "telefoonnummer", "value": "a"},
            {"name": "email-adres","value": "a"},
            {"name": "straat", "value": "a"},
            {"name": "huisnummer", "value": "a"},
            {"name": "toevoeging", "value": "a"},
            {"name": "postcode", "value": "a"},
            {"name": "woonplaats", "value": "a"},
            {"name": "provincie", "value": "a"},
            {"name": "land", "value": "a"},
            {"name": "polisnummer", "value": "a"},
            {"name": "verzekeraar", "value": "a"},
            {"name": "voornaam_mantelzorger", "value": "a"},
            {"name": "tussenvoegsel_mantelzorger", "value": "a"},
            {"name": "achternaam_mantelzorger", "value": "a"},
            {"name": "telefoonnummer_mantelzorger", "value": "a"},
            {"name": "mobielnummer_mantelzorger", "value": "a"},
            {"name": "email-adres_mantelzorger", "value": "a"},
            {"name": "voornaam_contactpersoon", "value": "a"},
            {"name": "tussenvoegsel_contactpersoon", "value": "a"},
            {"name": "achternaam_contactpersoon", "value": "a"},
            {"name": "telefoonnummer_contactpersoon", "value": "a"},
            {"name": "mobielnummer_contactpersoon", "value": "a"},
            {"name": "email-adres_contactpersoon", "value": "a"},
            {"name": "naam_huisarts", "value": "a"},
            {"name": "straat_huisarts", "value": "a"},
            {"name": "huisnnummer_huisarts", "value": "a"},
            {"name": "toevoeging_huisarts", "value": "a"},
            {"name": "telefoonnummer_huisarts", "value": ""},
            {"name": "agb-code_huisarts", "value": ""},
            {"name": "uzi-nummer_huisarts", "value": ""},
            {"name": "email-adres_huisarts", "value": ""}],
        schema=schema)
    print(f"Issue cred response: {response}")
    time.sleep(3)
    # Show credential on desktop
    while not desktop.get_credentials()["results"]:
        print("Credentials not received")
        time.sleep(4)
    print(f"Credentials received: {desktop.get_credentials()}")
