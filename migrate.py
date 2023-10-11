# scripts/migrate.py
from alembic.config import Config
from alembic import command


def run_alembic_upgrade():
    # Path to your alembic.ini file
    alembic_ini_path = "alembic.ini"

    # Create Alembic config
    alembic_config = Config(alembic_ini_path)

    # Run Alembic upgrade
    command.upgrade(alembic_config, "head")


if __name__ == "__main__":
    run_alembic_upgrade()
