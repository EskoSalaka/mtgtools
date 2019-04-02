from functools import wraps
from warnings import warn


def scryfall_only(f):
    @wraps(f)
    def wrapper(self, *args, **kwds):
        if self.api_type != 'scryfall':
            print('The method {} works only for objects from the Scryfall api.'.format(str(f)))
            return

        return f(self, *args, **kwds)

    return wrapper

def deprecated(instead):
    def inner_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            warn(f'The method {func.__name__ } is currently deprecated. The method {instead} is automatically called instead"')
            return getattr(self, instead)(self, *args, **kwargs)

        return wrapper

    return inner_decorator