"""
创建GIS相关表的数据库迁移脚本
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON, GEOMETRY
import uuid


# revision identifiers, used by Alembic.
revision = '001_create_gis_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """创建GIS相关表"""
    
    # 创建图层表
    op.create_table(
        'layers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('geometry_type', sa.String(50), nullable=False),
        sa.Column('srid', sa.Integer, default=4326, nullable=False),
        sa.Column('extent_min_x', sa.Float, nullable=True),
        sa.Column('extent_min_y', sa.Float, nullable=True),
        sa.Column('extent_max_x', sa.Float, nullable=True),
        sa.Column('extent_max_y', sa.Float, nullable=True),
        sa.Column('feature_count', sa.Integer, default=0),
        sa.Column('is_visible', sa.Boolean, default=True),
        sa.Column('opacity', sa.Float, default=1.0),
        sa.Column('style', JSON, default={}),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # 创建空间要素表
    op.create_table(
        'spatial_features',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('layer_id', UUID(as_uuid=True), sa.ForeignKey('layers.id'), nullable=False, index=True),
        sa.Column('geometry', GEOMETRY(geometry_type='GEOMETRY', srid=4326), nullable=False),
        sa.Column('properties', JSON, default={}),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # 创建分析结果表
    op.create_table(
        'analysis_results',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('analysis_type', sa.String(50), nullable=False, index=True),
        sa.Column('input_parameters', JSON, nullable=False),
        sa.Column('result_data', JSON, nullable=False),
        sa.Column('geometry', GEOMETRY(geometry_type='GEOMETRY', srid=4326), nullable=True),
        sa.Column('statistics', JSON, default={}),
        sa.Column('execution_time', sa.Float, default=0.0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )
    
    # 创建空间索引
    op.execute('CREATE INDEX idx_spatial_features_geometry ON spatial_features USING GIST (geometry)')
    op.execute('CREATE INDEX idx_analysis_results_geometry ON analysis_results USING GIST (geometry)')
    
    # 创建图层名称唯一索引
    op.create_unique_constraint('uq_layers_name', 'layers', ['name'])


def downgrade():
    """删除GIS相关表"""
    
    # 删除索引
    op.execute('DROP INDEX IF EXISTS idx_spatial_features_geometry')
    op.execute('DROP INDEX IF EXISTS idx_analysis_results_geometry')
    
    # 删除约束
    op.drop_constraint('uq_layers_name', 'layers', type_='unique')
    
    # 删除表
    op.drop_table('analysis_results')
    op.drop_table('spatial_features')
    op.drop_table('layers')