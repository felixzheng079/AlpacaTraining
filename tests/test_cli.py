from click.testing import CliRunner
from alpaca_training.cli import cli


class TestCLI:
    def test_list_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "SMACrossover" in result.output

    def test_status_command(self, monkeypatch, tmp_path):
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr("alpaca_training.config.DB_PATH", db_path)
        from alpaca_training.db import init_db, save_daily_snapshot, update_position
        init_db(db_path)
        save_daily_snapshot(db_path, "2026-05-09", 150.0, 5, "active")

        runner = CliRunner()
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0

    def test_list_has_no_errors(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
