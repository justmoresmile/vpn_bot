import importlib
import pkgutil


def load_protocol_handlers():

    package = importlib.import_module(
        "app.protocols.handlers"
    )

    for module in pkgutil.iter_modules(
        package.__path__
    ):

        if module.name == "base":
            continue

        importlib.import_module(
            f"{package.__name__}.{module.name}"
        )