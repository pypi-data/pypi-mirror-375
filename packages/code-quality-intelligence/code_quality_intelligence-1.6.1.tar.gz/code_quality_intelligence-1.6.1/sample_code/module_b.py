from module_a import add


def compute(values):
    result = []
    for v in values:
        if v == 0:
            result.append(add(v, v))
        else:
            result.append(add(v, v - 1))
    return result


def load_pickle(p):
    import pickle
    return pickle.loads(p)


