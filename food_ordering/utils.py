# common helper function


def get_option_value(option_tuple, key):
    '''
    This function will return the value of key when a tuple is optional in a model
    :param option_tuple: tuple of tuple
    :param key: value in zeroth index of tuple
    :return: value in first index of tuple
    '''
    for type in option_tuple:
        if type[0] == key:
            return type[1]
    return None
