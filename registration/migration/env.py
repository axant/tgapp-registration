from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

def run_migrations_online():
    engine = engine_from_config(config.get_section(config.config_ini_section),
                                prefix='sqlalchemy.',
                                poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(connection=connection, target_metadata=None,
                      version_table='registration_migrate')

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

run_migrations_online()