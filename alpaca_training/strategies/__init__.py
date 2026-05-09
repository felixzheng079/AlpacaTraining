# alpaca_training/strategies/__init__.py
import importlib
import inspect
import os
import pkgutil


def discover_strategies():
    from lumibot.strategies.strategy import Strategy

    strategies = []
    package_dir = os.path.dirname(__file__)

    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        module = importlib.import_module(f"alpaca_training.strategies.{module_name}")

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
