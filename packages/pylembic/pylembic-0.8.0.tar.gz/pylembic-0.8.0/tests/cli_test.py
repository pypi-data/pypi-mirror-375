from pytest import fixture
from typer.testing import CliRunner
from pylembic.cli import app

runner = CliRunner()


@fixture
def valid_migrations_path(tmp_path):
    """Creates a temporary directory for valid migrations."""
    migrations_path = tmp_path / "migrations"
    migrations_path.mkdir()
    # Simulate valid migrations setup
    (migrations_path / "env.py").write_text("env content")
    (migrations_path / "script.py.mako").write_text("script content")
    (migrations_path / "version1.py").write_text("version 1 content")
    return str(migrations_path)


@fixture
def invalid_migrations_path(tmp_path):
    """Creates a temporary directory for invalid migrations."""
    migrations_path = tmp_path / "migrations"
    migrations_path.mkdir()
    # Simulate missing or invalid migrations setup
    (migrations_path / "env.py").write_text("env content")
    return str(migrations_path)


def test_validate_valid_migrations(valid_migrations_path, mocker):
    """Test validate command with valid migrations."""
    mock_validate = mocker.patch(
        "pylembic.validator.Validator.validate", return_value=True
    )

    result = runner.invoke(app, ["validate", valid_migrations_path])

    assert result.exit_code == 0
    assert "Validating migrations..." in result.output
    assert "Migrations validation passed!" in result.output
    mock_validate.assert_called_once()


def test_validate_verbose(valid_migrations_path, mocker):
    """Test validate command with verbose logging."""
    mock_validate = mocker.patch(
        "pylembic.validator.Validator.validate", return_value=True
    )

    result = runner.invoke(app, ["validate", valid_migrations_path, "--verbose"])

    assert result.exit_code == 0
    assert "Validating migrations..." in result.output
    assert "Verbose mode enabled." in result.output
    assert "Migrations validation passed!" in result.output
    mock_validate.assert_called_once()


def test_validate_check_branching(valid_migrations_path, mocker):
    """Test validate command with branching migrations."""
    mock_validate = mocker.patch(
        "pylembic.validator.Validator.validate", return_value=False
    )

    result = runner.invoke(
        app, ["validate", valid_migrations_path, "--detect-branches"]
    )

    assert result.exit_code == 0
    assert "Validating migrations..." in result.output
    assert "Detecting for branching migrations enabled." in result.output
    assert "Migrations validation failed!" in result.output
    mock_validate.assert_called_once()


def test_validate_invalid_migrations(invalid_migrations_path, mocker):
    """Test validate command with invalid migrations."""
    mock_validate = mocker.patch(
        "pylembic.validator.Validator.validate", return_value=False
    )

    result = runner.invoke(app, ["validate", invalid_migrations_path])

    assert result.exit_code == 0
    assert "Validating migrations..." in result.output
    assert "Migrations validation failed!" in result.output
    mock_validate.assert_called_once()


def test_show_graph(valid_migrations_path, mocker):
    """Test show-graph command to visualize the graph."""
    mock_visualize = mocker.patch("pylembic.validator.Validator.show_graph")

    result = runner.invoke(app, ["show-graph", valid_migrations_path])

    assert result.exit_code == 0
    assert "Visualizing migration graph..." in result.output
    mock_visualize.assert_called_once()


def test_no_action():
    """Test when no action is specified."""
    result = runner.invoke(app)

    assert result.exit_code != 0
    assert "Missing command" in result.output


def test_no_action_with_migrations(valid_migrations_path):
    """Test when no action is specified with migrations path."""
    result = runner.invoke(app, [valid_migrations_path])

    assert result.exit_code != 0
    assert "No such command" in result.output


def test_invalid_path():
    """Test when an invalid migrations path is provided."""
    result = runner.invoke(app, ["validate", "/invalid/path"])

    assert result.exit_code != 0
    assert "Processing migrations in: /invalid/path" in result.output
