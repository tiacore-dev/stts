"""api_key_id

Revision ID: 80796f7ff1a8
Revises: 03a9209bb46a
Create Date: 2024-11-13 13:54:57.426871

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '80796f7ff1a8'
down_revision: Union[str, None] = '03a9209bb46a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавление столбца key_id как primary key
    op.add_column('api_keys', sa.Column('key_id', sa.String(), nullable=False))
    
    # Устанавливаем key_id как primary key
    op.create_primary_key('pk_api_keys', 'api_keys', ['key_id'])

    # Изменение столбца api_key на NOT NULL
    op.alter_column('api_keys', 'api_key', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    # Удаляем primary key
    op.drop_constraint('pk_api_keys', 'api_keys', type_='primary')

    # Удаляем столбец key_id
    op.drop_column('api_keys', 'key_id')

    # Возвращаем столбец api_key обратно в nullable
    op.alter_column('api_keys', 'api_key', existing_type=sa.String(), nullable=True)
