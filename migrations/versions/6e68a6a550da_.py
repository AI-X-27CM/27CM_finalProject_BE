"""empty message

Revision ID: 6e68a6a550da
Revises: 
Create Date: 2024-03-19 15:58:34.101858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e68a6a550da'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('all',
    sa.Column('ALL_pk', sa.Integer(), nullable=False),
    sa.Column('ALL_Cnt', sa.Integer(), nullable=False),
    sa.Column('Detect_Cnt', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('ALL_pk')
    )
    op.create_index(op.f('ix_all_ALL_pk'), 'all', ['ALL_pk'], unique=False)
    op.create_table('error',
    sa.Column('error_pk', sa.Integer(), nullable=False),
    sa.Column('error', sa.String(), nullable=False),
    sa.Column('Date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('error_pk')
    )
    op.create_index(op.f('ix_error_error_pk'), 'error', ['error_pk'], unique=False)
    op.create_table('users',
    sa.Column('User_pk', sa.Integer(), nullable=False),
    sa.Column('ID', sa.String(), nullable=True),
    sa.Column('PWD', sa.String(), nullable=False),
    sa.Column('Phone', sa.String(), nullable=False),
    sa.Column('Date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('User_pk')
    )
    op.create_index(op.f('ix_users_ID'), 'users', ['ID'], unique=True)
    op.create_index(op.f('ix_users_User_pk'), 'users', ['User_pk'], unique=False)
    op.create_table('detect',
    sa.Column('Detect_pk', sa.Integer(), nullable=False),
    sa.Column('User_pk', sa.Integer(), nullable=True),
    sa.Column('Label', sa.String(), nullable=True),
    sa.Column('Record', sa.Text(), nullable=True),
    sa.Column('Date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['User_pk'], ['users.User_pk'], ),
    sa.PrimaryKeyConstraint('Detect_pk')
    )
    op.create_index(op.f('ix_detect_Detect_pk'), 'detect', ['Detect_pk'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_detect_Detect_pk'), table_name='detect')
    op.drop_table('detect')
    op.drop_index(op.f('ix_users_User_pk'), table_name='users')
    op.drop_index(op.f('ix_users_ID'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_error_error_pk'), table_name='error')
    op.drop_table('error')
    op.drop_index(op.f('ix_all_ALL_pk'), table_name='all')
    op.drop_table('all')
    # ### end Alembic commands ###
