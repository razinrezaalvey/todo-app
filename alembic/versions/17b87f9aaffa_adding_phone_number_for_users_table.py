"""adding phone number for users table

Revision ID: 17b87f9aaffa
Revises: 
Create Date: 2026-09-29 22:21:32.155925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17b87f9aaffa'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('Users',sa.Column('phone_number',sa.String(12),nullable=True))

def downgrade() -> None:
    op.drop_column('Users','phone_number')
#run code : alembic downgrade -1