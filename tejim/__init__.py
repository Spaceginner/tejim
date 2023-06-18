import os

from .data_convert import convert


def parse(content: str) -> dict:
    """
    will parse contents of the tejim file and return its dictionary representation

    :param content: the contents representing tejim file
    :return: dictionary representation of the contents
    """
    tokens = []

    # adapted from Spaceginner/opyn
    # splitter
    buffer, skip = "", 0
    for i in range(len(content)):
        if skip: skip -= 1; continue  # NOQA E702

        match_found = False
        for unique_symbol in ('!=', '=', ':', '\\', os.linesep):
            if content[i:i + len(unique_symbol)] == unique_symbol:
                if buffer:
                    tokens.append(buffer)
                    buffer = ""

                tokens.append(unique_symbol)
                skip = len(unique_symbol) - 1
                match_found = True
                break
        if not match_found:
            buffer += content[i]

    stored = {}

    # now convert that list of tokens into a dictionary
    skip = 0
    for i in range(len(tokens) - 1):
        if skip > 0: skip -= 1; continue  # NOQA E702

        # if it is a multi-line token
        if tokens[i+1] in ('!=', ':'):
            # find where the closing token is
            matched = False
            for j in range(i+1, len(tokens)):
                # if it is a closing token
                if tokens[j].strip() == '\\' \
                        and tokens[j+1].strip() == tokens[i].strip():
                    matched = True
                    # if it is a dictionary-like
                    if tokens[i+1] == ':':
                        stored[tokens[i].strip()] = parse(''.join(tokens[i+3:j]))
                    # if it is a multi-line value
                    elif tokens[i+1] == '!=':
                        stored[tokens[i].strip()] = ''.join(tokens[i + 3:j]).strip()
                    skip = j - i
                    break
            # if closing token was not found
            if not matched:
                raise ValueError(f'closing token was not found for `{tokens[i]}` token')
        # if it is a one-line token
        elif tokens[i+1] == '=':
            stored[tokens[i].strip()] = convert(tokens[i+2].strip())
            skip = 2

    return stored


def generate(store: dict, _level: int = 0) -> str:
    """
    generates a tejim file based on the store dictionary

    :param store: dictionary which has to be converted into a tejim file's representation
    :return: contents of the tejim file representing the store dictionary
    """
    contents = ""

    for key in store:
        if isinstance(store[key], str) and '\n' in store[key]:
            contents += "    " * _level + key + '!=\n\n' \
                        + store[key].strip() + '\n\n' \
                        + "    " * _level + f'\\{key}\n'
        elif isinstance(store[key], dict):
            contents += ('\n' if _level == 0 else '') \
                        + "    " * _level + key + ':\n' \
                        + generate(store[key], _level+1) \
                        + "    " * _level + f'\\{key}\n\n'
        else:
            contents += "    " * _level + key + '= ' \
                        + (store[key].strip() if isinstance(store[key], str) else str(store[key])) \
                        + '\n'

    return contents
