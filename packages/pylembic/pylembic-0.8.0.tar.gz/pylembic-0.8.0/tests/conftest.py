from os import path

from pytest import fixture


@fixture
def with_one_migration_path():
    return path.join(path.dirname(path.abspath(__file__)), "fixtures", "one_migration")


@fixture
def with_migrations_path():
    return path.join(path.dirname(path.abspath(__file__)), "fixtures", "migrations")


@fixture
def with_circular_migrations_path():
    return path.join(
        path.dirname(path.abspath(__file__)), "fixtures", "circular_migrations"
    )


def cleanup_migration_006(with_migrations_path):
    orphan_migration_file = path.join(with_migrations_path, "versions", "006_head.py")
    with open(orphan_migration_file, "w") as f:
        f.write(
            """\"\"\"head migration\"\"\"

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None
"""
        )


@fixture
def with_orphan_migration(with_migrations_path):
    orphan_migration_file = path.join(with_migrations_path, "versions", "006_head.py")
    with open(orphan_migration_file, "w") as f:
        f.write(
            """\"\"\"orphan migration\"\"\"

revision = "006"
down_revision = None  # Orphan migration
branch_labels = None
depends_on = None
"""
        )

    yield

    # Cleanup
    cleanup_migration_006(with_migrations_path)


@fixture
def with_multiple_bases_or_heads_migration(with_migrations_path):
    orphan_migration_file = path.join(with_migrations_path, "versions", "006_head.py")
    with open(orphan_migration_file, "w") as f:
        f.write(
            """\"\"\"orphan migration\"\"\"

revision = "006"
down_revision = "004"  # Multiple heads
branch_labels = None
depends_on = None
"""
        )

    yield

    # Cleanup
    cleanup_migration_006(with_migrations_path)
