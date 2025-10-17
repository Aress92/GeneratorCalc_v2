"""
Import job models for data validation and processing.

Modele zadań importu danych z walidacją i przetwarzaniem.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Integer, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.core.database import Base


class ImportStatus(str, Enum):
    """Status of import job."""
    PENDING = "pending"
    PROCESSING = "processing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ImportType(str, Enum):
    """Type of import data."""
    REGENERATOR_CONFIG = "regenerator_config"
    MATERIAL_PROPERTIES = "material_properties"
    OPERATING_CONDITIONS = "operating_conditions"
    CHECKER_PATTERN = "checker_pattern"
    WALL_CONFIGURATION = "wall_configuration"


class ImportJob(Base):
    """Import job tracking table."""

    __tablename__ = "import_jobs"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    import_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default=ImportStatus.PENDING)

    # Progress tracking
    total_rows = Column(Integer, default=0)
    processed_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    invalid_rows = Column(Integer, default=0)

    # Validation results
    validation_errors = Column(JSON, default=list)
    validation_warnings = Column(JSON, default=list)
    column_mapping = Column(JSON, default=dict)

    # Metadata
    metadata_info = Column(JSON, default=dict)
    processing_options = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="import_jobs")
    imported_regenerators = relationship("ImportedRegenerator", back_populates="import_job")


class ImportedRegenerator(Base):
    """Imported regenerator configuration data."""

    __tablename__ = "imported_regenerators"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_job_id = Column(CHAR(36), ForeignKey("import_jobs.id"), nullable=False)

    # Basic identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    regenerator_type = Column(String(50), nullable=False)  # crown, end-port, cross-fired

    # Geometric properties
    length = Column(Float, nullable=False)  # meters
    width = Column(Float, nullable=False)   # meters
    height = Column(Float, nullable=False)  # meters
    volume = Column(Float, nullable=True)   # m3

    # Thermal properties
    design_temperature = Column(Float, nullable=False)  # Celsius
    max_temperature = Column(Float, nullable=False)     # Celsius
    working_pressure = Column(Float, nullable=True)     # Pascal

    # Flow properties
    air_flow_rate = Column(Float, nullable=True)        # m3/h
    gas_flow_rate = Column(Float, nullable=True)        # m3/h
    pressure_drop = Column(Float, nullable=True)        # Pascal

    # Material properties
    checker_material = Column(String(255), nullable=True)
    insulation_material = Column(String(255), nullable=True)
    refractory_material = Column(String(255), nullable=True)

    # Performance data
    thermal_efficiency = Column(Float, nullable=True)    # percentage
    heat_recovery_rate = Column(Float, nullable=True)    # percentage
    fuel_consumption = Column(Float, nullable=True)      # kW or BTU/h

    # Validation status
    is_validated = Column(Boolean, default=False)
    validation_score = Column(Float, nullable=True)      # 0-100
    validation_notes = Column(Text, nullable=True)

    # Raw imported data
    raw_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    import_job = relationship("ImportJob", back_populates="imported_regenerators")


class ValidationRule(Base):
    """Validation rules for imported data."""

    __tablename__ = "validation_rules"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    import_type = Column(String(50), nullable=False)
    field_name = Column(String(100), nullable=False)

    # Rule definition
    rule_type = Column(String(50), nullable=False)  # range, regex, required, custom
    rule_config = Column(JSON, nullable=False)      # rule parameters
    severity = Column(String(20), nullable=False)   # error, warning, info

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UnitConversion(Base):
    """Unit conversion definitions."""

    __tablename__ = "unit_conversions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_unit = Column(String(50), nullable=False)
    to_unit = Column(String(50), nullable=False)
    conversion_factor = Column(Float, nullable=False)
    conversion_offset = Column(Float, default=0.0)

    # Metadata
    unit_type = Column(String(50), nullable=False)  # temperature, length, pressure, etc.
    description = Column(Text, nullable=True)

    # Formula: to_value = (from_value * factor) + offset

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)