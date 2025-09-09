from pytest import raises

from pylembic.exceptions import CircularDependencyError
from pylembic.validator import Validator


def test_validate_alembic_migrations(with_migrations_path):
    # given
    validator = Validator(alembic_config_path=with_migrations_path)

    # when
    result = validator.validate(verbose=True)

    # then
    assert result, "Validation should pass"
    assert len(validator.graph.nodes) == 6, "Graph should contain all 6 revisions"


def test_validate_alembic_migrations_checking_branches(with_migrations_path, caplog):
    # given
    validator = Validator(alembic_config_path=with_migrations_path)

    # when
    result = validator.validate(verbose=True, detect_branches=True)

    # then
    assert not result, "Validation should fail due to branching"
    branches_log = [
        record for record in caplog.records if "Branching" in record.message
    ]
    assert len(branches_log) == 2, "Branching migrations should be detected"


def test_orphan_migration_detection(
    with_migrations_path, with_orphan_migration, caplog
):
    # given
    validator = Validator(alembic_config_path=with_migrations_path)

    # when
    result = validator.validate(verbose=True)

    # then
    assert not result, "Validation should fail due to orphan migration"
    # Check the logs for orphan migration warnings
    orphan_logs = [
        record for record in caplog.records if "orphan" in record.message.lower()
    ]
    assert len(orphan_logs) == 1, "Orphan migration should be detected"


def test_multiple_bases_or_heads(
    with_migrations_path, with_multiple_bases_or_heads_migration, caplog
):
    # given
    validator = Validator(alembic_config_path=with_migrations_path)

    # when
    result = validator.validate(verbose=True)

    # then
    assert not result, "Validation should fail due to multiple heads or bases"
    # Check the logs for multiple heads or bases warnings
    multiple_heads_or_bases_logs = [
        record for record in caplog.records if "multiple" in record.message.lower()
    ]
    assert (
        len(multiple_heads_or_bases_logs) == 1
    ), "Multiple heads or bases should be detected"


def test_circular_dependencies(with_circular_migrations_path):
    # when
    with raises(CircularDependencyError) as exc_info:
        _ = Validator(alembic_config_path=with_circular_migrations_path)

    # then
    assert "Cycle is detected" in str(exc_info.value), "Cycle should be detected"


def test_one_migration__no_orphans_check(with_one_migration_path, caplog):
    # given
    validator = Validator(alembic_config_path=with_one_migration_path)

    # when
    result = validator.validate(verbose=True)

    # then
    assert result, "Validation should pass"
    assert len(validator.graph.nodes) == 1, "Graph should contain only one revision"
    assert "Only one migration detected. Skipping orphan check." in caplog.text
