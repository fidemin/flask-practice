"""empty message

Revision ID: 29f818b2ed2b
Revises: 3a9aa3cd7cd2
Create Date: 2024-04-14 16:51:54.092259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29f818b2ed2b'
down_revision = '3a9aa3cd7cd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_head_of', sa.String(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_employee_is_head_of_department'), 'department', ['is_head_of'], ['department_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('employee', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_employee_is_head_of_department'), type_='foreignkey')
        batch_op.drop_column('is_head_of')

    # ### end Alembic commands ###