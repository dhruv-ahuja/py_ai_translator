import functools


def singleton(cls):
    @functools.wraps(cls)
    def init_singleton(*args, **kwargs):
        instance = init_singleton.__instance

        if instance is None:
            init_singleton.__instance = cls(*args, **kwargs)
        return init_singleton.__instance

    # set this attribute beforehand to avoid attributeError when function is called
    init_singleton.__instance = None
    return init_singleton
