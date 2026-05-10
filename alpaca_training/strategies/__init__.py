# alpaca_training/strategies/__init__.py
import importlib
import inspect
import logging
import os
import pkgutil

logger = logging.getLogger(__name__)


def discover_strategies(package_dir=None, package_name=None):
    from lumibot.strategies.strategy import Strategy

    strategies = []
    if package_dir is None:
        package_dir = os.path.dirname(__file__)
    if package_name is None:
        package_name = "alpaca_training.strategies"

    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        full_name = f"{package_name}.{module_name}"
        try:
            module = importlib.import_module(full_name)
        except Exception as e:
            logger.warning("Failed to import module %s: %s", full_name, e)
            continue

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj is Strategy:
                continue
            if issubclass(obj, Strategy) and not inspect.isabstract(obj):
                strategies.append({
                    "name": name,
                    "cls": obj,
                    "module": module_name,
                })

    return strategies
