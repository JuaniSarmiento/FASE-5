"""
Migración: Agregar tabla simulator_events

Revision ID: add_simulator_events
Revises: 
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_simulator_events'
down_revision = None  # Actualizar con la última revisión
branch_labels = None
depends_on = None


def upgrade():
    """
    Crear tabla simulator_events para capturar eventos de simuladores
    """
    op.create_table(
        'simulator_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Event metadata
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('student_id', sa.String(length=100), nullable=False),
        sa.Column('simulator_type', sa.String(length=50), nullable=False),
        
        # Event details
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_data', JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        
        # Context
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    )
    
    # Indexes para optimizar queries
    op.create_index('idx_event_session', 'simulator_events', ['session_id', 'timestamp'])
    op.create_index('idx_event_type_student', 'simulator_events', ['event_type', 'student_id'])
    op.create_index('idx_event_simulator_session', 'simulator_events', ['simulator_type', 'session_id'])
    
    print("✅ Tabla 'simulator_events' creada exitosamente")
    print("✅ Índices creados para optimización de queries")


def downgrade():
    """
    Eliminar tabla simulator_events
    """
    op.drop_index('idx_event_simulator_session', table_name='simulator_events')
    op.drop_index('idx_event_type_student', table_name='simulator_events')
    op.drop_index('idx_event_session', table_name='simulator_events')
    op.drop_table('simulator_events')
    
    print("⚠️  Tabla 'simulator_events' eliminada")
