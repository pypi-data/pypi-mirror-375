try:
    import tomllib as toml
except ImportError:
    import toml
from pathlib import Path


def get_package_name():
    """
    Infer the package name.
    This is the name of the package code directory under `src/`, also the "import" name.
    This does not need to be the "project" name defined in `pyproject.toml`, which is for `pypi` and `pip`,
    related to install/uninstall.

    Here, we only consider one scenrio, that is, the package name contains dash,
    and the dash is replaced by underscore in the import name of the package. Specifically,
    the import name of the package is the name of the sole child directory of `src/`.
    """
    subs = [p for p in Path("src/").iterdir() if p.is_dir()]
    assert len(subs) == 1
    return subs[0].name


def parse_pyproject():
    return toml.load(open("pyproject.toml", "rb"))
