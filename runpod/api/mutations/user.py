"""
RunPod | API | Mutations | User
"""


def generate_user_mutation(pubkey):
    """
    Generates a GraphQL mutation to edit a user's settings.

    Args:
        pubkey (str): A string representing the public key of the user.

    Returns:
        str: A GraphQL mutation string that can be used to edit a user's settings.
    """
    input_fields = []

    escaped_pubkey = pubkey.replace("\n", "\\n")
    input_fields.append(f'pubKey: "{escaped_pubkey}"')

    # Format input fields
    input_string = ", ".join(input_fields)

    return f"""
    mutation {{
        updateUserSettings(
            input: {{
                {input_string}
            }}
        ) {{
            id
            pubKey
        }}
    }}
    """
