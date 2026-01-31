"""Initial schema: events, users, subscriptions, entitlements, state_transitions.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("event_id", sa.String(255), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.UniqueConstraint("provider", "event_id", name="uq_events_provider_event_id"),
    )
    op.create_index("ix_events_provider", "events", ["provider"], unique=False)
    op.create_index("ix_events_event_type", "events", ["event_type"], unique=False)
    op.create_index("ix_events_received_at", "events", ["received_at"], unique=False)
    op.create_index("ix_events_provider_event_type", "events", ["provider", "event_type"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("external_customer_id", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_external_customer_id", "users", ["external_customer_id"], unique=False)
    op.create_index("ix_users_provider", "users", ["provider"], unique=False)

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=False)

    op.create_table(
        "entitlements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_key", sa.String(128), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "feature_key", name="uq_entitlements_user_feature"),
    )
    op.create_index("ix_entitlements_user_id", "entitlements", ["user_id"], unique=False)
    op.create_index("ix_entitlements_feature_key", "entitlements", ["feature_key"], unique=False)

    op.create_table(
        "state_transitions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("from_state", sa.String(64), nullable=True),
        sa.Column("to_state", sa.String(64), nullable=False),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transitioned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_state_transitions_entity_type", "state_transitions", ["entity_type"], unique=False)
    op.create_index("ix_state_transitions_entity_id", "state_transitions", ["entity_id"], unique=False)
    op.create_index("ix_state_transitions_event_id", "state_transitions", ["event_id"], unique=False)


def downgrade() -> None:
    op.drop_table("state_transitions")
    op.drop_table("entitlements")
    op.drop_table("subscriptions")
    op.drop_table("users")
    op.drop_table("events")
