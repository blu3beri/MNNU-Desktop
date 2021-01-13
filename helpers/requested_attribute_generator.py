def generate_requested_attributes(schema: dict) -> dict:
    """
    Generate a dict with the requested attributes from a schema
    :param schema: The schema where the attributes need to be generated from
    :return: A dict with the requested attributes
    """
    attributes = {}
    for i, attribute in enumerate(schema["attributes"]):
        attributes[f"attribute{i}"] = {
            "name": attribute,
            "restrictions": [
                {
                    "schema_name": schema["schema_name"],
                    "schema_version": schema["schema_version"]
                }
            ]
        }
    return attributes
