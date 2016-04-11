__author__ = 'filip'


def tuplify(objs):
    if not objs:
        return tuple()
    if not hasattr(objs, '__iter__'):
        return (objs, )
    return tuple(objs)