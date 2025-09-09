try:
    import importlib.metadata as importlib_metadata
except ImportError:
    # Python < 3.8
    import importlib_metadata

try:
    __version__ = importlib_metadata.version("active-boxes")
except importlib_metadata.PackageNotFoundError:
    # Package is not installed
    __version__ = "unknown"
