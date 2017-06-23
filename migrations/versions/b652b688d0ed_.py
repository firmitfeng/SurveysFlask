"""empty message

Revision ID: b652b688d0ed
Revises: c6170594b21e
Create Date: 2017-06-22 12:43:46.146126

"""

# revision identifiers, used by Alembic.
revision = 'b652b688d0ed'
down_revision = 'c6170594b21e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('archives',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('keywords', sa.String(length=200), nullable=True),
    sa.Column('type', sa.String(length=64), nullable=True),
    sa.Column('ctime', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['object_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'messages', sa.Column('ctime', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'messages', 'ctime')
    op.drop_table('archives')
    ### end Alembic commands ###