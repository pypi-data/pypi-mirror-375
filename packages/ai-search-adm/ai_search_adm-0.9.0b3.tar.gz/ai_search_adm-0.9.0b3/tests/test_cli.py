from unittest.mock import Mock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError
from click.exceptions import Exit
from typer.testing import CliRunner

from ai_search_adm.cli import (
    _confirm_destructive_operation,
    _index_exists,
    _mk_client,
    _sanitize_for_create,
    _validate_clear_params,
    app,
)

runner = CliRunner()


class TestMkClient:
    def test_mk_client_with_api_key(self) -> None:
        with patch("ai_search_adm.cli.SearchIndexClient") as mock_client:
            _mk_client("https://test.search.windows.net", "api-key")
            mock_client.assert_called_once()
            args, kwargs = mock_client.call_args
            assert "endpoint" in kwargs
            assert "credential" in kwargs

    def test_mk_client_with_default_credential(self) -> None:
        with (
            patch("ai_search_adm.cli.SearchIndexClient") as mock_client,
            patch("ai_search_adm.cli.DefaultAzureCredential") as mock_cred,
        ):
            _mk_client("https://test.search.windows.net", None)
            mock_cred.assert_called_once()
            mock_client.assert_called_once()


class TestIndexExists:
    def test_index_exists_true(self) -> None:
        mock_client = Mock()
        mock_client.get_index.return_value = Mock()
        assert _index_exists(mock_client, "test-index") is True

    def test_index_exists_false(self) -> None:
        mock_client = Mock()
        mock_client.get_index.side_effect = ResourceNotFoundError("Not found")
        assert _index_exists(mock_client, "test-index") is False


class TestSanitizeForCreate:
    def test_sanitize_for_create(self) -> None:
        mock_index = Mock()
        mock_index.name = "old-name"
        result = _sanitize_for_create(mock_index, "new-name")
        assert result.name == "new-name"


class TestDuplicateCommand:
    @patch("ai_search_adm.cli._mk_client")
    def test_duplicate_source_not_found(self, mock_mk_client: Mock) -> None:
        mock_client = Mock()
        mock_client.get_index.side_effect = ResourceNotFoundError("Not found")
        mock_mk_client.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "duplicate",
                "--endpoint",
                "https://test.search.windows.net",
                "--source",
                "non-existent",
                "--target",
                "target",
            ],
        )
        assert result.exit_code == 2

    @patch("ai_search_adm.cli._mk_client")
    @patch("ai_search_adm.cli._index_exists")
    @patch("ai_search_adm.cli.console")
    def test_duplicate_target_exists_no_overwrite(
        self, _mock_console: Mock, mock_index_exists: Mock, mock_mk_client: Mock
    ) -> None:
        mock_src_client = Mock()
        mock_dst_client = Mock()
        mock_mk_client.side_effect = [mock_src_client, mock_dst_client]

        # Mock successful source index retrieval
        mock_src_index = Mock()
        mock_src_client.get_index.return_value = mock_src_index

        # Mock target index exists
        mock_index_exists.return_value = True

        result = runner.invoke(
            app,
            ["duplicate", "--endpoint", "https://test.search.windows.net", "--source", "source", "--target", "target"],
        )
        # Target exists, no overwrite should exit with code 3
        assert result.exit_code == 3


class TestClearCommand:
    @patch("ai_search_adm.cli._mk_client")
    @patch("ai_search_adm.cli.input")
    @patch("ai_search_adm.cli.console")
    def test_clear_index_not_found(self, _mock_console: Mock, _mock_input: Mock, mock_mk_client: Mock) -> None:
        mock_client = Mock()
        mock_client.get_index.side_effect = ResourceNotFoundError("Not found")
        mock_mk_client.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "clear",
                "--endpoint",
                "https://test.search.windows.net",
                "--index",
                "non-existent",
            ],
        )
        assert result.exit_code == 2

    @patch("ai_search_adm.cli._mk_client")
    @patch("ai_search_adm.cli.input")
    @patch("ai_search_adm.cli.console")
    def test_clear_user_cancels(self, _mock_console: Mock, mock_input: Mock, mock_mk_client: Mock) -> None:
        mock_client = Mock()
        mock_client.get_index.return_value = Mock()
        mock_mk_client.return_value = mock_client

        # User types something other than DELETE
        mock_input.return_value = "cancel"

        result = runner.invoke(
            app,
            [
                "clear",
                "--endpoint",
                "https://test.search.windows.net",
                "--index",
                "test-index",
            ],
        )
        # Should exit with 0 when cancelled
        assert result.exit_code == 0
        # Should not call delete_index
        mock_client.delete_index.assert_not_called()

    @patch("ai_search_adm.cli._mk_client")
    @patch("ai_search_adm.cli.input")
    @patch("ai_search_adm.cli.console")
    def test_clear_success(self, _mock_console: Mock, mock_input: Mock, mock_mk_client: Mock) -> None:
        mock_client = Mock()
        mock_index = Mock()
        mock_index.name = "test-index"
        mock_client.get_index.return_value = mock_index
        mock_client.delete_index.return_value = None
        mock_client.create_index.return_value = mock_index
        mock_mk_client.return_value = mock_client

        # User confirms with DELETE
        mock_input.return_value = "DELETE"

        result = runner.invoke(
            app,
            [
                "clear",
                "--endpoint",
                "https://test.search.windows.net",
                "--index",
                "test-index",
            ],
        )
        assert result.exit_code == 0
        # Should call delete and then create
        mock_client.delete_index.assert_called_once_with("test-index")
        mock_client.create_index.assert_called_once()

    def test_validate_clear_params_missing_endpoint(self) -> None:
        with patch("ai_search_adm.cli.console") as mock_console:
            with pytest.raises(Exit) as exc_info:
                _validate_clear_params("", "test-index")
            assert exc_info.value.exit_code == 1
            mock_console.print.assert_called()

    def test_validate_clear_params_missing_index(self) -> None:
        with patch("ai_search_adm.cli.console") as mock_console:
            with pytest.raises(Exit) as exc_info:
                _validate_clear_params("https://test.search.windows.net", "")
            assert exc_info.value.exit_code == 1
            mock_console.print.assert_called()

    def test_confirm_destructive_operation_cancel(self) -> None:
        with patch("ai_search_adm.cli.input") as mock_input, patch("ai_search_adm.cli.console"):
            mock_input.return_value = "cancel"
            with pytest.raises(Exit) as exc_info:
                _confirm_destructive_operation("test-index")
            assert exc_info.value.exit_code == 0

    def test_confirm_destructive_operation_keyboard_interrupt(self) -> None:
        with patch("ai_search_adm.cli.input") as mock_input, patch("ai_search_adm.cli.console"):
            mock_input.side_effect = KeyboardInterrupt()
            with pytest.raises(Exit) as exc_info:
                _confirm_destructive_operation("test-index")
            assert exc_info.value.exit_code == 0


class TestStatsCommand:
    @patch("ai_search_adm.cli._mk_client")
    @patch("ai_search_adm.cli.console")
    def test_stats_index_not_found(self, _mock_console: Mock, mock_mk_client: Mock) -> None:
        mock_client = Mock()
        mock_client.get_index_statistics.side_effect = ResourceNotFoundError("Not found")
        mock_mk_client.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "stats",
                "--endpoint",
                "https://test.search.windows.net",
                "--index",
                "non-existent",
            ],
        )
        assert result.exit_code == 2

    @patch("ai_search_adm.cli._mk_client")
    @patch("ai_search_adm.cli.console")
    def test_stats_success(self, _mock_console: Mock, mock_mk_client: Mock) -> None:
        mock_client = Mock()
        mock_stats = {
            "document_count": 12345,
            "storage_size": 1048576,  # 1 MB
            "vector_index_size": 524288,  # 512 KB
        }
        mock_client.get_index_statistics.return_value = mock_stats
        mock_mk_client.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "stats",
                "--endpoint",
                "https://test.search.windows.net",
                "--index",
                "test-index",
            ],
        )
        assert result.exit_code == 0
        mock_client.get_index_statistics.assert_called_once_with("test-index")

    @patch("ai_search_adm.cli._mk_client")
    @patch("ai_search_adm.cli.console")
    def test_stats_without_vector_index(self, _mock_console: Mock, mock_mk_client: Mock) -> None:
        mock_client = Mock()
        mock_stats = {
            "document_count": 100,
            "storage_size": 2048,  # 2 KB
        }
        mock_client.get_index_statistics.return_value = mock_stats
        mock_mk_client.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "stats",
                "--endpoint",
                "https://test.search.windows.net",
                "--index",
                "simple-index",
            ],
        )
        assert result.exit_code == 0
        mock_client.get_index_statistics.assert_called_once_with("simple-index")

    def test_stats_missing_parameters(self) -> None:
        result = runner.invoke(
            app,
            ["stats"],
        )
        assert result.exit_code == 1
        assert "Missing required options" in result.output
