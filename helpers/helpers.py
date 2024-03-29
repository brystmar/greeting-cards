"""
Miscellaneous small helper functions
"""
from logging import getLogger

logger = getLogger()


def convert_to_bool(input) -> bool:
    """Converts a given input to boolean"""
    # logger.debug(f"Starting convert_to_bool({input}), type: {type(input)}")

    output = input

    if type(input) == bool:
        logger.debug(f"Input was already boolean.")
        return input
    elif type(input) == str:
        if input.lower() in ['true', '1', 't', 'y', 'yes']:
            output = True
        else:
            output = False
    elif type(input) == int:
        if input == 1:
            output = True
        else:
            output = False
    else:
        logger.warning(f"Unsupported type provided: {type(input)}")
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
