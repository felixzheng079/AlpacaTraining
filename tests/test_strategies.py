# tests/test_strategies.py
import os
import sys
import tempfile
from alpaca_training.strategies import discover_strategies


PACKAGE_NAME = "test_pkg"


def _write_package(tmpdir, modules):
    pkg_dir = os.path.join(tmpdir, PACKAGE_NAME)
    os.makedirs(pkg_dir, exist_ok=True)
    with open(os.path.join(pkg_dir, "__init__.py"), "w") as f:
        f.write("")
    for module_name, content in modules.items():
        with open(os.path.join(pkg_dir, f"{module_name}.py"), "w") as f:
            f.write(content)
    return pkg_dir


def _cleanup_modules(module_names):
    for name in module_names:
        sys.modules.pop(f"{PACKAGE_NAME}.{name}", None)
    sys.modules.pop(PACKAGE_NAME, None)


class TestStrategyDiscovery:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        sys.path.insert(0, self.tmpdir)
        self._module_names = []

    def teardown_method(self):
        _cleanup_modules(self._module_names)
        try:
            sys.path.remove(self.tmpdir)
        except ValueError:
            pass
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_package(self, modules):
        self._module_names = list(modules.keys())
        return _write_package(self.tmpdir, modules)

    def test_finds_subclasses(self):
        pkg_dir = self._make_package({
            "example_strategy": """
from lumibot.strategies.strategy import Strategy

class ExampleStrategy(Strategy):
    def on_trading_iteration(self):
        pass
"""
        })
        found = discover_strategies(package_dir=pkg_dir, package_name=PACKAGE_NAME)
        names = [s["name"] for s in found]
        assert "ExampleStrategy" in names

    def test_includes_module_info(self):
        pkg_dir = self._make_package({
            "my_module": """
from lumibot.strategies.strategy import Strategy

class MyStrategy(Strategy):
    def on_trading_iteration(self):
        pass
"""
        })
        found = discover_strategies(package_dir=pkg_dir, package_name=PACKAGE_NAME)
        entry = next(s for s in found if s["name"] == "MyStrategy")
        assert entry["module"] == "my_module"
        assert entry["cls"].__name__ == "MyStrategy"

    def test_ignores_non_strategy_classes(self):
        pkg_dir = self._make_package({
            "mixed": """
from lumibot.strategies.strategy import Strategy

class MyStrategy(Strategy):
    def on_trading_iteration(self):
        pass

class PlainClass:
    pass
"""
        })
        found = discover_strategies(package_dir=pkg_dir, package_name=PACKAGE_NAME)
        names = [s["name"] for s in found]
        assert "PlainClass" not in names

    def test_empty_directory_returns_empty_list(self):
        pkg_dir = self._make_package({})
        found = discover_strategies(package_dir=pkg_dir, package_name=PACKAGE_NAME)
        assert found == []

    def test_excludes_abstract_strategies(self):
        pkg_dir = self._make_package({
            "abstracts": """
import abc
from lumibot.strategies.strategy import Strategy

class AbstractStrategy(Strategy, abc.ABC):
    @abc.abstractmethod
    def on_trading_iteration(self):
        pass

class ConcreteStrategy(AbstractStrategy):
    def on_trading_iteration(self):
        pass
"""
        })
        found = discover_strategies(package_dir=pkg_dir, package_name=PACKAGE_NAME)
        names = [s["name"] for s in found]
        assert "ConcreteStrategy" in names
        assert "AbstractStrategy" not in names

    def test_strategy_base_class_not_in_results(self):
        pkg_dir = self._make_package({
            "base_test": """
from lumibot.strategies.strategy import Strategy

class TestStrategy(Strategy):
    def on_trading_iteration(self):
        pass
"""
        })
        found = discover_strategies(package_dir=pkg_dir, package_name=PACKAGE_NAME)
        names = [s["name"] for s in found]
        assert "Strategy" not in names

    def test_import_error_does_not_crash_discovery(self):
        pkg_dir = self._make_package({
            "good_strategy": """
from lumibot.strategies.strategy import Strategy

class GoodStrategy(Strategy):
    def on_trading_iteration(self):
        pass
""",
            "bad_module": """
import nonexistent_module_xyz

class BadStrategy:
    pass
"""
        })
        found = discover_strategies(package_dir=pkg_dir, package_name=PACKAGE_NAME)
        names = [s["name"] for s in found]
        assert "GoodStrategy" in names
