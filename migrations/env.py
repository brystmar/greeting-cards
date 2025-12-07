from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from backend import create_app, db

# Define the Alembic config object
alembic_config = context.config

# Interpret the config file for Python logging.
fileConfig(alembic_config.config_file_name)

# Create Flask app and push context
flask_app = create_app()
flask_app.app_context().push()

# Tell Alembic what models to autogenerate against
target_metadata = db.metadata

def run_migrations_offline():
    url = flask_app.config["SQLALCHEMY_DATABASE_URI"]
    context.configure(
        url=url,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = flask_app.config["SQLALCHEMY_DATABASE_URI"]
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
