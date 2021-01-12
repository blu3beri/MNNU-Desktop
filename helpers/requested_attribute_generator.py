def generate_requested_attributes(schema: dict) -> dict:
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
