__version__ = '0.0.1.dev31'

try:
    from importlib.metadata import version
    __version__ = version("solidkit")
except:
    pass
