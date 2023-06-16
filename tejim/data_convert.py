import os


def _convert_bool(sbool: str) -> bool:
    if sbool in ['yes', 'y', 'true']:
        return True
    return False


# tries to guess what type of data was meant
# inside of the config value
def convert(s: str) -> bool | str | int | float:
    # if it has a line separater it is def a str value
    # so we wont even try to test it against other values
    if os.linesep in s:
        return s

    if s.lower() in ['yes', 'no', 'y', 'n', 'true', 'false']:
        return _convert_bool(s)

    # Easier to Ask Forgiveness Than Permission
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s
