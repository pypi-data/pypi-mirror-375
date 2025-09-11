def clean_docstring(docstring: str) -> str:
    """Cleans the docstring by removing the Args section.

    Args:
        docstring: Complete docstring to clean

    Returns:
        Clean docstring without Args section
    """
    if not docstring:
        return ""

    # Remove the Args section and any text after it
    cleaned = re.sub(r"\s*Args:.*", "", docstring, flags=re.DOTALL).strip()

    return cleaned


def parse_docstring_args(docstring: str) -> Dict[str, str]:
    """Extracts parameter descriptions from the Args section of the docstring.

    Args:
        docstring: Complete docstring of the function/class

    Returns:
        Dictionary with parameter descriptions
    """
    if not docstring:
        return {}

    # Find the Args section
    args_match = re.search(
        r"Args:\s*(.*?)(?:\n\n|\n[A-Za-z]+:|\Z)", docstring, re.DOTALL
    )
    if not args_match:
        return {}

    # Extract parameter descriptions
    args_text = args_match.group(1).strip()
    param_descriptions = {}

    # Process line by line to avoid capturing descriptions of other parameters
    lines = args_text.split("\n")
    current_param = None
    current_desc = []

    for raw_line in lines:
        line = raw_line.strip()
        # Find a new parameter
        param_match = re.match(r"(\w+)\s*\((.*?)\):\s*(.+)", line)

        if param_match:
            # Save description of previous parameter if exists
            if current_param:
                param_descriptions[current_param] = " ".join(current_desc).strip()

            # Start new parameter
            current_param = param_match.group(1)
            current_desc = [param_match.group(3)]
        elif current_param and line:
            # Continue description of current parameter
            current_desc.append(line)

    # Save last description
    if current_param:
        param_descriptions[current_param] = " ".join(current_desc).strip()

    return param_descriptions


def generate_json_schema(cls: type) -> Dict[str, Any]:
    """Generates a JSON schema for a class based on its characteristics.

    Args:
        cls:
            The class to generate the schema for

    Returns:
        JSON schema for the class
    """
    name = cls.get_module_name()
    description = cls.get_module_description()
    clean_description = clean_docstring(description)
    param_descriptions = parse_docstring_args(description)
    annotations = cls.get_module_annotations()

    properties = {}
    required = []

    for param, type_hint in annotations.items():
        if param == "return":
            continue

        prop_schema = {"type": "string"}  # Default as string

        # Check if enum is defined
        if hasattr(type_hint, "__args__") and type_hint.__origin__ is Literal:
            prop_schema["enum"] = list(type_hint.__args__)

        # Add parameter description if available
        if param in param_descriptions:
            prop_schema["description"] = param_descriptions[param]

        # Mark as required
        if get_origin(type_hint) is not Union:
            required.append(param)

        properties[param] = prop_schema

    json_schema = {
        "name": name,
        "description": clean_description or f"Function for {name}",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
        "strict": True,
    }

    return json_schema

