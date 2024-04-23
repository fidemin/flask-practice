"""empty message

Revision ID: cb2ad64daec0
Revises: a0fb9d41e293
Create Date: 2024-04-23 20:06:49.056223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb2ad64daec0'
down_revision = 'a0fb9d41e293'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('project')
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('email', sa.VARCHAR(), nullable=False),
    sa.Column('password', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('email', name='pk_user'),
    sa.UniqueConstraint('email', name='uq_user_email')
    )
    op.create_table('project',
    sa.Column('project_id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('project_id', name='pk_project')
    )
    # ### end Alembic commands ###
