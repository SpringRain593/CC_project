import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool, create_engine # Added create_engine for run_migrations_online flexibility

from alembic import context

# ---- Add this section to make your app importable ----
# This assumes env.py is in project_root/alembic/
# and your app is in project_root/app/
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# ---- End section ----

from app.core.config import settings # 匯入您的應用程式設定
from app.db.base_class import Base  # 匯入您的 SQLAlchemy Base
# Import your models here so that Base.metadata is populated
# For example:
from app.models import user # Make sure your User model (and others) are imported

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Set the SQLAlchemy URL from your application's settings ---
# This overrides the sqlalchemy.url from alembic.ini
if settings.DATABASE_URL:
    config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
else:
    # Handle case where DATABASE_URL might not be set in your app's settings for some reason
    # Or raise an error, as it's critical for migrations.
    print("Warning: DATABASE_URL not found in application settings. Alembic might not connect.")
# --- End SQLAlchemy URL setup ---


# --- Set target_metadata to your Base.metadata ---
# This allows autogenerate to detect changes to your models
target_metadata = Base.metadata
# --- End target_metadata setup ---


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url is now correctly picked up from config.set_main_option above
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata, # Use the populated target_metadata
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # engine_from_config will use the sqlalchemy.url set by config.set_main_option
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), # Gets settings from alembic.ini section (e.g. [alembic])
        prefix="sqlalchemy.", # Looks for settings like sqlalchemy.url, sqlalchemy.poolclass etc.
        poolclass=pool.NullPool,
        # You could also create the engine directly if preferred:
        # connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata # Use the populated target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
