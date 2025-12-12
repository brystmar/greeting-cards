"""
Misc small helper functions
"""
from logging import getLogger
from re import sub

logger = getLogger()


def convert_to_bool(input_data) -> bool:
    """Converts a given input to boolean"""
    # logger.debug(f"Starting convert_to_bool({input}), type: {type(input)}")

    output = input_data

    if type(input_data) == bool:
        logger.debug(f"Input was already boolean.")
        return input_data
    elif type(input_data) == str:
        if input_data.lower() in ['true', '1', 't', 'y', 'yes']:
            output = True
        else:
            output = False
    elif type(input_data) == int:
        if input_data == 1:
            output = True
        else:
            output = False
    else:
        logger.warning(f"Unsupported type provided: {type(input_data)}")
        logger.warning(f"Setting value to False")
        output = False

    # logger.debug(f"Ending convert_to_bool, returning {output}")
    return output


def remove_milliseconds_from_datetime_string(text) -> str:
    if isinstance(text, str):
        position = text.find(".")
        if position == -1:
            return text
        else:
            return text[:position]
    else:
        raise TypeError(f"Input to remove_milliseconds_from_datetime_string must be a string, not {type(text)}.")


def scrub_password_from_database_uri(uri: str) -> str:
    # Matches: postgresql://username:password@host/...
    return sub(r'(postgresql\+psycopg://[^:]+:)([^@]+)(@)', r'\1DB_PW\3', uri)
