"""Initial migration

Revision ID: 2c0134be860b
Revises: 
Create Date: 2024-10-04 14:18:40.786527

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Float, Text, DateTime, Boolean
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '2c0134be860b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу users
    op.create_table(
        'users',
        sa.Column('user_id', sa.String, primary_key=True, autoincrement=False),
        sa.Column('username', sa.String, nullable=True),
        sa.Column('login', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=True),
        sa.Column('user_type', sa.String, default='user')
    )

    # Создаем таблицу audio_files
    op.create_table(
        'audio_files',
        sa.Column('audio_id', sa.String, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),  # Изменено
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_extension', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Float, nullable=False),
        sa.Column('upload_date', sa.DateTime, default=datetime.utcnow),
        sa.Column('bucket_name', sa.String(255), nullable=False),
        sa.Column('s3_key', sa.String(255), nullable=False),
        sa.Column('url', sa.Text),  # Добавлено
        sa.Column('transcribed', sa.Boolean),  # Добавлено
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])  # Внешний ключ
    )

    # Создаем таблицу prompts
    op.create_table(
        'prompts',
        sa.Column('prompt_id', sa.String, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),  # Изменено
        sa.Column('prompt_name', sa.String(255), nullable=False),
        sa.Column('text', sa.Text),
        sa.Column('use_automatic', sa.Boolean, nullable=True, default=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])  # Внешний ключ
    )

    # Создаем таблицу transcriptions
    op.create_table(
        'transcriptions',
        sa.Column('transcription_id', sa.String, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),  # Изменено
        sa.Column('text', sa.Text),
        sa.Column('audio_id', sa.String(255), nullable=False),
        sa.Column('tokens', sa.Integer),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),  # Внешний ключ
        sa.ForeignKeyConstraint(['audio_id'], ['audio_files.audio_id'])  # Внешний ключ
    )

    # Создаем таблицу logs
    op.create_table(
        'logs',
        sa.Column('log_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(255), nullable=False),  # Изменено
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('message', sa.String(255), nullable=False),
        sa.Column('timestamp', sa.DateTime, default=datetime.utcnow),
    )

    # Создаем таблицу analysis
    op.create_table(
        'analysis',
        sa.Column('analysis_id', sa.String, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),  # Изменено
        sa.Column('text', sa.Text),
        sa.Column('prompt_id', sa.String(255), nullable=False),
        sa.Column('transcription_id', sa.String(255), nullable=False),
        sa.Column('tokens', sa.Integer),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),  # Внешний ключ
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.prompt_id']),  # Внешний ключ
        sa.ForeignKeyConstraint(['transcription_id'], ['transcriptions.transcription_id'])  # Внешний ключ
    )

    # Создаем таблицу api_keys
    op.create_table(
        'api_keys',
        sa.Column('api_key', sa.String, primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=False),  # Изменено
        sa.Column('comment', sa.Text),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])  # Внешний ключ
    )


def downgrade() -> None:
    """    # Удаляем таблицу logs
    op.drop_table('logs')

    # Удаляем таблицу transcriptions
    op.drop_table('transcriptions')

    # Удаляем таблицу prompts
    op.drop_table('prompts')

    # Удаляем таблицу audio_files
    op.drop_table('audio_files')

    # Удаляем таблицу users
    op.drop_table('users')

    # Удаляем таблицу api_keys
    op.drop_table('api_keys')

    # Удаляем таблицу analysis
    op.drop_table('analysis')"""
