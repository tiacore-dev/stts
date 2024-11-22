"""Create tables

Revision ID: f84d5fd4a370
Revises: 2c0134be860b
Create Date: 2024-11-22 22:55:23.739358

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Float, Text, DateTime, Boolean
from datetime import datetime



# revision identifiers, used by Alembic.
revision: str = 'f84d5fd4a370'
down_revision: Union[str, None] = '2c0134be860b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass



def downgrade() -> None:
   
