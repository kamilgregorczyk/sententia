import string
import random
from itertools import zip_longest


def gen_code(length=3):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def get_code(cls, filter_params={}):
    code = gen_code()
    i = 0
    while cls.objects.filter(**filter_params).filter(code=code).exists():
        i += 1
        code = gen_code() if i < 1000 else gen_code(3 + (i / 1000))
    return code


def zip_discard_compr(*iterables, sentinel=object()):
    return [[entry for entry in iterable if entry is not sentinel]
            for iterable in zip_longest(*iterables, fillvalue=sentinel)]
