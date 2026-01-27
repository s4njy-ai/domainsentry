"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-27 21:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create domains table
    op.create_table('domains',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain_name', sa.String(length=255), nullable=False),
        sa.Column('registered_date', sa.DateTime(), nullable=True),
        sa.Column('expires_date', sa.DateTime(), nullable=True),
        sa.Column('updated_date', sa.DateTime(), nullable=True),
        sa.Column('registrar', sa.String(length=255), nullable=True),
        sa.Column('registrant_name', sa.String(length=255), nullable=True),
        sa.Column('registrant_organization', sa.String(length=255), nullable=True),
        sa.Column('registrant_country', sa.String(length=2), nullable=True),
        sa.Column('registrant_email', sa.String(length=255), nullable=True),
        sa.Column('name_servers', sa.JSON(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('risk_level', sa.String(length=50), nullable=True, default='low'),
        sa.Column('risk_factors', sa.JSON(), nullable=True),
        sa.Column('virustotal_reputation', sa.Integer(), nullable=True),
        sa.Column('abuseipdb_reputation', sa.Integer(), nullable=True),
        sa.Column('threat_indicators', sa.JSON(), nullable=True),
        sa.Column('certificate_issuer', sa.String(length=255), nullable=True),
        sa.Column('certificate_subject', sa.String(length=255), nullable=True),
        sa.Column('certificate_valid_from', sa.DateTime(), nullable=True),
        sa.Column('certificate_valid_to', sa.DateTime(), nullable=True),
        sa.Column('certificate_serial', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True, default='crt.sh'),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_domains_domain_name'), 'domains', ['domain_name'], unique=True)
    op.create_index(op.f('ix_domains_risk_score'), 'domains', ['risk_score'])
    op.create_index(op.f('ix_domains_created_at'), 'domains', ['created_at'])
    
    # Create domain_enrichments table
    op.create_table('domain_enrichments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('source_data', sa.JSON(), nullable=False),
        sa.Column('enrichment_type', sa.String(length=50), nullable=False),
        sa.Column('is_successful', sa.Boolean(), nullable=True, default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('http_status_code', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_domain_enrichments_domain_id'), 'domain_enrichments', ['domain_id'])
    op.create_index(op.f('ix_domain_enrichments_source'), 'domain_enrichments', ['source'])
    op.create_index(op.f('ix_domain_enrichments_created_at'), 'domain_enrichments', ['created_at'])
    
    # Create domain_scans table
    op.create_table('domain_scans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_type', sa.String(length=50), nullable=False),
        sa.Column('scan_data', sa.JSON(), nullable=False),
        sa.Column('previous_scan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('risk_factors', sa.JSON(), nullable=True),
        sa.Column('scanner_version', sa.String(length=50), nullable=True),
        sa.Column('scan_duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ),
        sa.ForeignKeyConstraint(['previous_scan_id'], ['domain_scans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_domain_scans_domain_id'), 'domain_scans', ['domain_id'])
    op.create_index(op.f('ix_domain_scans_scan_type'), 'domain_scans', ['scan_type'])
    op.create_index(op.f('ix_domain_scans_created_at'), 'domain_scans', ['created_at'])
    
    # Create news_feed_items table
    op.create_table('news_feed_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('link', sa.String(length=1000), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('categories', sa.String(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('link')
    )
    
    # Create indexes
    op.create_index(op.f('ix_news_feed_items_source'), 'news_feed_items', ['source'])
    op.create_index(op.f('ix_news_feed_items_published_at'), 'news_feed_items', ['published_at'])
    op.create_index(op.f('ix_news_feed_items_created_at'), 'news_feed_items', ['created_at'])


def downgrade() -> None:
    # Drop news_feed_items table
    op.drop_index(op.f('ix_news_feed_items_created_at'), table_name='news_feed_items')
    op.drop_index(op.f('ix_news_feed_items_published_at'), table_name='news_feed_items')
    op.drop_index(op.f('ix_news_feed_items_source'), table_name='news_feed_items')
    op.drop_table('news_feed_items')
    
    # Drop domain_scans table
    op.drop_index(op.f('ix_domain_scans_created_at'), table_name='domain_scans')
    op.drop_index(op.f('ix_domain_scans_scan_type'), table_name='domain_scans')
    op.drop_index(op.f('ix_domain_scans_domain_id'), table_name='domain_scans')
    op.drop_table('domain_scans')
    
    # Drop domain_enrichments table
    op.drop_index(op.f('ix_domain_enrichments_created_at'), table_name='domain_enrichments')
    op.drop_index(op.f('ix_domain_enrichments_source'), table_name='domain_enrichments')
    op.drop_index(op.f('ix_domain_enrichments_domain_id'), table_name='domain_enrichments')
    op.drop_table('domain_enrichments')
    
    # Drop domains table
    op.drop_index(op.f('ix_domains_updated_at'), table_name='domains')
    op.drop_index(op.f('ix_domains_created_at'), table_name='domains')
    op.drop_index(op.f('ix_domains_risk_score'), table_name='domains')
    op.drop_index(op.f('ix_domains_domain_name'), table_name='domains')
    op.drop_table('domains')