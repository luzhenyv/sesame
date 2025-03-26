"""initial migration

Revision ID: initial
Revises:
Create Date: 2024-03-19 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create family_members table
    op.create_table(
        "family_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("relationship", sa.String(length=50), nullable=False),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("health_score", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_family_members_id"), "family_members", ["id"], unique=False)

    # Create health_events table
    op.create_table(
        "health_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date_time", sa.DateTime(), nullable=False),
        sa.Column("family_member_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("file_paths", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("file_types", postgresql.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(
            ["family_member_id"],
            ["family_members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_health_events_id"), "health_events", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_healthevents_id"), table_name="healthevents")
    op.drop_table("healthevents")
    op.drop_index(op.f("ix_familymembers_id"), table_name="familymembers")
    op.drop_table("familymembers")
