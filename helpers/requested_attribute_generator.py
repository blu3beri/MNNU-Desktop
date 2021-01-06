def generate_requested_attributes(schema: list) -> dict:
    attributes = {}
    for i, attribute in enumerate(schema[1]):
        attributes[f"attribute{i}"] = {
            "name": attribute,
            "restrictions": [
                {
                    "schema_name": schema[0][0],
                    "schema_version": schema[0][1]
                }
            ]
        }
    return attributes
