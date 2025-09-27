"""
Regenerator configuration models.

Modele konfiguracji regeneratorów.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Integer, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR

from app.core.database import Base


class RegeneratorType(str, Enum):
    """Types of regenerators."""
    CROWN = "crown"
    END_PORT = "end-port"
    CROSS_FIRED = "cross-fired"


class ConfigurationStatus(str, Enum):
    """Configuration status."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    ARCHIVED = "archived"


class RegeneratorConfiguration(Base):
    """Main regenerator configuration table."""

    __tablename__ = "regenerator_configurations"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)

    # Basic identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    regenerator_type = Column(String(50), nullable=False)

    # Configuration metadata
    configuration_version = Column(String(20), default="1.0")
    status = Column(String(20), nullable=False, default=ConfigurationStatus.DRAFT)

    # Wizard progress tracking
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, default=7)
    completed_steps = Column(JSON, default=list)  # List of completed step numbers

    # Main configuration data
    geometry_config = Column(JSON, nullable=True)
    materials_config = Column(JSON, nullable=True)
    thermal_config = Column(JSON, nullable=True)
    flow_config = Column(JSON, nullable=True)
    constraints_config = Column(JSON, nullable=True)
    visualization_config = Column(JSON, nullable=True)

    # 3D model data
    model_geometry = Column(JSON, nullable=True)  # 3D geometry data
    model_materials = Column(JSON, nullable=True)  # Material assignments

    # Validation results
    is_validated = Column(Boolean, default=False)
    validation_score = Column(Float, nullable=True)
    validation_errors = Column(JSON, default=list)
    validation_warnings = Column(JSON, default=list)

    # Template information
    based_on_template_id = Column(CHAR(36), ForeignKey("configuration_templates.id"), nullable=True)
    is_template = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    template = relationship("ConfigurationTemplate", back_populates="configurations")


class ConfigurationTemplate(Base):
    """Pre-defined configuration templates."""

    __tablename__ = "configuration_templates"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Template metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    regenerator_type = Column(String(50), nullable=False)
    category = Column(String(100), nullable=True)  # crown, end-port, cross-fired

    # Template configuration
    template_config = Column(JSON, nullable=False)
    default_values = Column(JSON, nullable=True)
    required_fields = Column(JSON, nullable=True)

    # Usage metadata
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)

    # Creator information
    created_by_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("User")
    configurations = relationship("RegeneratorConfiguration", back_populates="template")


class Material(Base):
    """Materials library for regenerator components."""

    __tablename__ = "materials"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic information
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    material_code = Column(String(100), nullable=True)

    # Material classification
    material_type = Column(String(50), nullable=False)  # refractory, insulation, checker, etc.
    category = Column(String(100), nullable=True)
    application = Column(String(100), nullable=True)  # high_temp, medium_temp, insulation

    # Physical properties
    properties = Column(JSON, nullable=False)  # All material properties as JSON

    # Standard properties (for easy querying)
    density = Column(Float, nullable=True)  # kg/m³
    thermal_conductivity = Column(Float, nullable=True)  # W/(m·K)
    specific_heat = Column(Float, nullable=True)  # kJ/(kg·K)
    max_temperature = Column(Float, nullable=True)  # °C

    # Porosity and surface area
    porosity = Column(Float, nullable=True)  # % (0-100)
    surface_area = Column(Float, nullable=True)  # m²/m³

    # Composition
    chemical_composition = Column(JSON, nullable=True)

    # Cost and availability
    cost_per_unit = Column(Float, nullable=True)
    cost_unit = Column(String(20), nullable=True)  # per kg, per m³, etc.
    availability = Column(String(50), nullable=True)

    # Version control
    version = Column(String(20), default="1.0")
    superseded_by_id = Column(CHAR(36), ForeignKey("materials.id"), nullable=True)

    # Approval workflow
    approval_status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_by_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_standard = Column(Boolean, default=False)  # Standard industry materials

    # Creator information
    created_by_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])
    superseded_by = relationship("Material", remote_side=[id])


class GeometryComponent(Base):
    """3D geometry components for regenerator visualization."""

    __tablename__ = "geometry_components"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    configuration_id = Column(CHAR(36), ForeignKey("regenerator_configurations.id"), nullable=False)

    # Component identification
    component_name = Column(String(255), nullable=False)
    component_type = Column(String(50), nullable=False)  # checker, wall, insulation, etc.
    parent_component_id = Column(CHAR(36), ForeignKey("geometry_components.id"), nullable=True)

    # Geometry data
    geometry_data = Column(JSON, nullable=False)  # 3D vertices, faces, etc.
    transformation_matrix = Column(JSON, nullable=True)  # Position, rotation, scale

    # Material assignment
    material_id = Column(CHAR(36), ForeignKey("materials.id"), nullable=True)

    # Physical properties
    volume = Column(Float, nullable=True)  # m³
    surface_area = Column(Float, nullable=True)  # m²
    mass = Column(Float, nullable=True)  # kg

    # Visualization properties
    color = Column(String(7), nullable=True)  # Hex color
    opacity = Column(Float, default=1.0)
    is_visible = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    configuration = relationship("RegeneratorConfiguration")
    material = relationship("Material")
    parent_component = relationship("GeometryComponent", remote_side=[id])


class ConfigurationConstraint(Base):
    """Configuration constraints and validation rules."""

    __tablename__ = "configuration_constraints"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Constraint metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    constraint_type = Column(String(50), nullable=False)  # geometric, thermal, flow, material
    regenerator_type = Column(String(50), nullable=True)  # Apply to specific types only

    # Constraint definition
    constraint_config = Column(JSON, nullable=False)  # Constraint parameters
    severity = Column(String(20), nullable=False)  # error, warning, info

    # Rule logic
    rule_expression = Column(Text, nullable=True)  # Mathematical expression
    validation_function = Column(String(255), nullable=True)  # Python function name

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConfigurationHistory(Base):
    """Track configuration changes for audit and version control."""

    __tablename__ = "configuration_history"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    configuration_id = Column(CHAR(36), ForeignKey("regenerator_configurations.id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)

    # Change information
    action = Column(String(50), nullable=False)  # create, update, validate, export
    step_name = Column(String(100), nullable=True)  # Which wizard step was modified

    # Change details
    changes = Column(JSON, nullable=True)  # What was changed
    old_values = Column(JSON, nullable=True)  # Previous values
    new_values = Column(JSON, nullable=True)  # New values

    # Metadata
    session_id = Column(String(255), nullable=True)  # Browser session
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    configuration = relationship("RegeneratorConfiguration")
    user = relationship("User")