"""Add partitions to user_signin

Revision ID: 3805d350e094
Revises: 4b544cbf53df
Create Date: 2024-08-15 15:32:52.443755

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3805d350e094"
down_revision: Union[str, None] = "4b544cbf53df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users.user_sign_in_smart PARTITION OF users.user_sign_in 
        FOR VALUES IN ('smart')
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users.user_sign_in_mobile PARTITION OF users.user_sign_in 
        FOR VALUES IN ('mobile')
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users.user_sign_in_web PARTITION OF users.user_sign_in 
        FOR VALUES IN ('web')
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS users.user_sign_in_smart;")
    op.execute("DROP TABLE IF EXISTS users.user_sign_in_mobile;")
    op.execute("DROP TABLE IF EXISTS users.user_sign_in_web;")
