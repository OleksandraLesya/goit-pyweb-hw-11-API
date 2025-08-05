# alembic/env.py

import os
import sys
from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python's standard logging.
# This uses the same logger names as the engine and context.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.database.db import Base
# We need to import our model to make it visible to Alembic for autogenerate.
# This is a critical step, as Alembic needs to know about our `Contact` model.
from app.models.contacts import Contact

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Load environment variables from .env file
load_dotenv()

# Get the DATABASE_URL from our .env file.
# Note: For Alembic, we use a synchronous URL to avoid asyncio issues.
db_url = os.getenv("DATABASE_URL")

# Set the url to Alembic
config.set_main_option('sqlalchemy.url', db_url)

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.
    This version is designed to work with a synchronous connection for Alembic.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,  # This is important for SQLAlchemy 2.0 compatibility
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            dialect_opts={"paramstyle": "named"},
            compare_type=True, # Allows Alembic to detect changes in column types
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
