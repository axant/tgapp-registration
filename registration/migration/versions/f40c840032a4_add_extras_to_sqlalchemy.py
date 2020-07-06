"""add extras to sqlalchemy"""

revision = 'f40c840032a4'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'registration_registration',
        sa.Column('extras', sa.UnicodeText()),
    )


def downgrade():
    op.drop_column('registration_registration', 'extras')
