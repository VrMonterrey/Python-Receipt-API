"""empty message

Revision ID: 136d72d6d03d
Revises: a273c342775b
Create Date: 2024-09-21 11:16:20.145407

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "136d72d6d03d"
down_revision: Union[str, None] = "a273c342775b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_table(
        "receipts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("payment_type", sa.String(), nullable=False),
        sa.Column("payment_amount", sa.Float(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_receipts_id"), "receipts", ["id"], unique=False)
    op.create_table(
        "receipt_product",
        sa.Column("receipt_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["receipt_id"],
            ["receipts.id"],
        ),
        sa.PrimaryKeyConstraint("receipt_id", "product_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("receipt_product")
    op.drop_index(op.f("ix_receipts_id"), table_name="receipts")
    op.drop_table("receipts")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
    # ### end Alembic commands ###
