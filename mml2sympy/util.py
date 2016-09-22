import itertools


def isplit(iterable, splitters):
    '''
    Splits an iterable into 2d list based on a value in splitters

    http://stackoverflow.com/questions/4322705/split-a-list-into-nested-lists-on-a-value
    '''
    return [list(g) for k, g
            in itertools.groupby(iterable, lambda x:x in splitters) if not k]
