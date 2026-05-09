# tests/test_strategies.py
import os
import importlib
import pytest
from alpaca_training import strategies


class TestStrategyDiscovery:
    def setup_method(self):
        self.strategy_dir = os.path.join(os.path.dirname(strategies.__file__))
        self.example_file = os.path.join(self.strategy_dir, "example_strategy.py")
        self.non_strategy_file = None

    def teardown_method(self):
        for fname in ["example_strategy.py", "not_a_strategy.py"]:
            fpath = os.path.join(self.strategy_dir, fname)
            if os.path.exists(fpath):
                os.remove(fpath)
            pyc = fpath + "c"
            if os.path.exists(pyc):
                os.remove(pyc)
            cache_dir = os.path.join(self.strategy_dir, "__pycache__")
            if os.path.exists(cache_dir):
                import shutil
                shutil.rmtree(cache_dir, ignore_errors=True)

        preserved = {
            "__name__", "__doc__", "__file__", "__path__",
            "__package__", "__loader__", "__spec__",
            "__builtins__", "__cached__",
            "discover_strategies", "os", "importlib",
            "inspect", "pkgutil", "Strategy",
        }
        for mod in list(strategies.__dict__.keys()):
            if mod not in preserved:
                del strategies.__dict__[mod]

    def test_discover_strategies_finds_subclasses(self):
        with open(self.example_file, "w") as f:
            f.write("""
from lumibot.strategies.strategy import Strategy

class ExampleStrategy(Strategy):
    def on_trading_iteration(self):
        pass
""")

        from alpaca_training.strategies import discover_strategies

        found = discover_strategies()
        names = [s["name"] for s in found]
        assert "ExampleStrategy" in names

    def test_discover_strategies_includes_file_path(self):
        with open(self.example_file, "w") as f:
            f.write("""
from lumibot.strategies.strategy import Strategy

class ExampleStrategy(Strategy):
    def on_trading_iteration(self):
        pass
""")

        from alpaca_training.strategies import discover_strategies

        found = discover_strategies()
        example = next(s for s in found if s["name"] == "ExampleStrategy")
        assert "module" in example
        assert "cls" in example

    def test_discover_strategies_ignores_non_strategy_classes(self):
        with open(self.example_file, "w") as f:
            f.write("""
from lumibot.strategies.strategy import Strategy

class ExampleStrategy(Strategy):
    def on_trading_iteration(self):
        pass

class PlainClass:
    pass
""")

        from alpaca_training.strategies import discover_strategies

        found = discover_strategies()
        names = [s["name"] for s in found]
        assert "PlainClass" not in names
