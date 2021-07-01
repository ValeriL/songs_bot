"""init tables

Revision ID: 2dbf653aa7b7
Revises:
Create Date: 2021-06-26 00:26:27.028714

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2dbf653aa7b7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "songs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("chords", sa.String(), nullable=True),
        sa.Column("strumming", sa.String(), nullable=True),
        sa.Column("lyrics", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )


def downgrade():
    op.drop_table("songs")
    op.drop_table("users")
