"""
Import service for handling data import operations.

Serwis importu obsługujący operacje importu danych.
"""

import os
import pandas as pd
import uuid
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.import_job import ImportJob, ImportedRegenerator, ImportStatus, ImportType, ValidationRule, UnitConversion
from app.schemas.import_schemas import (
    ImportJobCreate, ImportPreview, ColumnMapping, ValidationError,
    RegeneratorDataCreate, UnitConversionCreate, ValidationRuleCreate
)
from app.core.config import settings
from app.services.validation_service import RegeneratorPhysicsValidator
from app.services.unit_conversion import UnitConversionService


logger = structlog.get_logger(__name__)


class ImportService:
    """Service for handling data import operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def preview_file(
        self,
        file_path: str,
        original_filename: str,
        preview_rows: int = 100
    ) -> ImportPreview:
        """
        Preview uploaded file and suggest column mapping.

        Args:
            file_path: Path to uploaded file
            original_filename: Original name of the file
            preview_rows: Number of rows to preview (default 100)

        Returns:
            ImportPreview with suggested mapping and validation
        """
        try:
            # Read the Excel file with multiple sheets support
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            # Use first sheet or sheet named 'Data', 'Regenerators', etc.
            sheet_name = self._select_best_sheet(sheet_names)
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=preview_rows)

            # Clean column names
            df.columns = [self._clean_column_name(col) for col in df.columns]

            # Get file info
            headers = df.columns.tolist()
            sample_rows = df.head(10).fillna('').values.tolist()  # Replace NaN with empty string
            total_rows = len(pd.read_excel(file_path, sheet_name=sheet_name))  # Get actual total

            # Detect import type based on columns
            detected_type = self._detect_import_type(headers)

            # Generate suggested column mapping
            suggested_mapping = await self._suggest_column_mapping(headers, detected_type)

            # Enhanced validation with physics check
            validation_errors = await self._validate_preview_data(df, detected_type)

            logger.info(
                "File preview generated",
                filename=original_filename,
                sheet=sheet_name,
                total_rows=total_rows,
                detected_type=detected_type,
                headers_count=len(headers)
            )

            return ImportPreview(
                headers=headers,
                sample_rows=sample_rows,
                total_rows=total_rows,
                detected_type=detected_type,
                suggested_mapping=suggested_mapping,
                validation_errors=validation_errors
            )

        except Exception as e:
            logger.error("Failed to preview file", error=str(e), filename=original_filename)
            raise ValueError(f"Failed to read file: {str(e)}")

    async def create_import_job(
        self,
        user_id: str,
        file_path: str,
        job_data: ImportJobCreate
    ) -> ImportJob:
        """
        Create a new import job.

        Args:
            user_id: ID of the user creating the job
            file_path: Path to the uploaded file
            job_data: Import job creation data

        Returns:
            Created ImportJob instance
        """
        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            filename = f"{uuid.uuid4()}.xlsx"

            # Create import job
            import_job = ImportJob(
                user_id=user_id,
                filename=filename,
                original_filename=job_data.original_filename,
                file_size=file_size,
                import_type=job_data.import_type,
                column_mapping=[mapping.model_dump() for mapping in job_data.column_mapping],
                processing_options=job_data.processing_options
            )

            self.db.add(import_job)
            await self.db.commit()
            await self.db.refresh(import_job)

            # Move file to permanent location
            final_path = Path(settings.UPLOAD_DIR) / "imports" / filename
            final_path.parent.mkdir(parents=True, exist_ok=True)
            os.rename(file_path, final_path)

            logger.info(
                "Import job created",
                job_id=import_job.id,
                user_id=user_id,
                import_type=job_data.import_type
            )

            return import_job

        except Exception as e:
            logger.error("Failed to create import job", error=str(e), user_id=user_id)
            raise

    async def process_import_job(self, job_id: str) -> ImportJob:
        """
        Process an import job asynchronously.

        Args:
            job_id: ID of the import job to process

        Returns:
            Updated ImportJob instance
        """
        try:
            # Get import job
            result = await self.db.execute(select(ImportJob).where(ImportJob.id == job_id))
            job = result.scalar_one_or_none()

            if not job:
                raise ValueError(f"Import job {job_id} not found")

            # Update status to processing
            job.status = ImportStatus.PROCESSING
            job.started_at = datetime.now(UTC)
            await self.db.commit()

            # Read and process file
            file_path = Path(settings.UPLOAD_DIR) / "imports" / job.filename
            df = pd.read_excel(file_path)

            job.total_rows = len(df)
            await self.db.commit()

            # Process based on import type
            if job.import_type == ImportType.REGENERATOR_CONFIG:
                await self._process_regenerator_config(job, df)
            elif job.import_type == ImportType.MATERIAL_PROPERTIES:
                await self._process_material_properties(job, df)
            else:
                raise ValueError(f"Unsupported import type: {job.import_type}")

            # Update job status
            job.status = ImportStatus.COMPLETED
            job.completed_at = datetime.now(UTC)
            await self.db.commit()

            logger.info("Import job completed", job_id=job_id)
            return job

        except Exception as e:
            logger.error("Import job failed", job_id=job_id, error=str(e))

            # Update job with error
            if 'job' in locals():
                job.status = ImportStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now(UTC)
                await self.db.commit()

            raise

    async def get_import_job(self, job_id: str) -> Optional[ImportJob]:
        """Get import job by ID."""
        result = await self.db.execute(select(ImportJob).where(ImportJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_user_import_jobs(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ImportJob]:
        """Get import jobs for a user."""
        result = await self.db.execute(
            select(ImportJob)
            .where(ImportJob.user_id == user_id)
            .order_by(ImportJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    def _detect_import_type(self, headers: List[str]) -> Optional[ImportType]:
        """
        Detect import type based on column headers.

        Args:
            headers: List of column headers

        Returns:
            Detected ImportType or None
        """
        headers_lower = [h.lower() for h in headers]

        # Regenerator configuration keywords
        regenerator_keywords = [
            'length', 'width', 'height', 'temperature', 'pressure',
            'flow', 'efficiency', 'material', 'regenerator'
        ]

        # Material properties keywords
        material_keywords = [
            'thermal_conductivity', 'specific_heat', 'density',
            'porosity', 'material_name', 'properties'
        ]

        # Count keyword matches
        regenerator_score = sum(1 for keyword in regenerator_keywords
                              if any(keyword in header for header in headers_lower))
        material_score = sum(1 for keyword in material_keywords
                           if any(keyword in header for header in headers_lower))

        # Return type with highest score
        if regenerator_score >= material_score and regenerator_score > 0:
            return ImportType.REGENERATOR_CONFIG
        elif material_score > 0:
            return ImportType.MATERIAL_PROPERTIES

        return None

    def _select_best_sheet(self, sheet_names: List[str]) -> str:
        """
        Select the best sheet from Excel file for import.

        Args:
            sheet_names: List of sheet names in Excel file

        Returns:
            Selected sheet name
        """
        # Priority order for sheet selection
        priority_names = [
            'regenerators', 'data', 'main', 'import',
            'config', 'configuration', 'sheet1'
        ]

        # Check for exact matches (case insensitive)
        for priority in priority_names:
            for sheet in sheet_names:
                if sheet.lower() == priority:
                    return sheet

        # Check for partial matches
        for priority in priority_names:
            for sheet in sheet_names:
                if priority in sheet.lower():
                    return sheet

        # Default to first sheet
        return sheet_names[0] if sheet_names else 'Sheet1'

    def _clean_column_name(self, column_name: str) -> str:
        """
        Clean and normalize column names.

        Args:
            column_name: Original column name

        Returns:
            Cleaned column name
        """
        if pd.isna(column_name):
            return f"unnamed_column_{uuid.uuid4().hex[:8]}"

        # Convert to string and strip whitespace
        clean_name = str(column_name).strip()

        # Remove common prefixes/suffixes
        clean_name = clean_name.replace('Unnamed: ', '')

        # If empty after cleaning, generate name
        if not clean_name:
            return f"empty_column_{uuid.uuid4().hex[:8]}"

        return clean_name

    async def _suggest_column_mapping(
        self,
        headers: List[str],
        import_type: Optional[ImportType]
    ) -> List[ColumnMapping]:
        """
        Suggest column mapping based on headers and import type.

        Args:
            headers: List of column headers
            import_type: Detected import type

        Returns:
            List of suggested column mappings
        """
        mappings = []

        if import_type == ImportType.REGENERATOR_CONFIG:
            # Define mapping rules for regenerator config
            mapping_rules = {
                'name': ['name', 'regenerator_name', 'title'],
                'length': ['length', 'l', 'len'],
                'width': ['width', 'w', 'wide'],
                'height': ['height', 'h', 'high'],
                'design_temperature': ['design_temp', 'temp', 'temperature'],
                'max_temperature': ['max_temp', 'maximum_temperature'],
                'thermal_efficiency': ['efficiency', 'eff', 'thermal_efficiency'],
                'checker_material': ['checker', 'material', 'checker_material']
            }

            for header in headers:
                header_lower = header.lower()
                for target_field, keywords in mapping_rules.items():
                    if any(keyword in header_lower for keyword in keywords):
                        mappings.append(ColumnMapping(
                            source_column=header,
                            target_field=target_field,
                            data_type='float' if target_field in ['length', 'width', 'height', 'design_temperature', 'max_temperature', 'thermal_efficiency'] else 'string',
                            is_required=target_field in ['name', 'length', 'width', 'height']
                        ))
                        break

        # Add unmapped columns as info
        mapped_columns = {mapping.source_column for mapping in mappings}
        unmapped_columns = set(headers) - mapped_columns

        for unmapped_col in unmapped_columns:
            mappings.append(ColumnMapping(
                source_column=unmapped_col,
                target_field="unmapped",
                data_type="string",
                is_required=False
            ))

        return mappings

    async def _validate_preview_data(
        self,
        df: pd.DataFrame,
        import_type: Optional[ImportType] = None
    ) -> List[ValidationError]:
        """
        Validate preview data and return errors.

        Args:
            df: DataFrame to validate
            import_type: Detected import type for specific validation

        Returns:
            List of validation errors
        """
        errors = []

        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1)
        if empty_rows.any():
            empty_count = empty_rows.sum()
            errors.append(ValidationError(
                row=0,
                column="all",
                message=f"Found {empty_count} completely empty rows - these will be skipped",
                severity="warning"
            ))

        # Check for duplicate headers
        duplicate_headers = [col for col in df.columns if df.columns.tolist().count(col) > 1]
        if duplicate_headers:
            errors.append(ValidationError(
                row=0,
                column="headers",
                message=f"Duplicate column names found: {', '.join(set(duplicate_headers))}",
                severity="error"
            ))

        # Check for numeric columns with non-numeric data
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            non_numeric = pd.to_numeric(df[col], errors='coerce').isnull() & df[col].notnull()
            if non_numeric.any():
                first_error_idx = non_numeric.idxmax()
                error_value = df.loc[first_error_idx, col]
                errors.append(ValidationError(
                    row=int(first_error_idx),
                    column=col,
                    message=f"Non-numeric value in numeric column: '{error_value}'",
                    severity="error",
                    value=str(error_value)
                ))

        # Check for potential required fields missing
        if import_type == ImportType.REGENERATOR_CONFIG:
            required_indicators = ['name', 'length', 'width', 'height']
            for indicator in required_indicators:
                if not any(indicator.lower() in col.lower() for col in df.columns):
                    errors.append(ValidationError(
                        row=0,
                        column="headers",
                        message=f"No column found for required field '{indicator}' - manual mapping may be needed",
                        severity="warning"
                    ))

        # Check data consistency within preview
        if len(df) > 0:
            # Check for unusual data patterns
            for col in df.select_dtypes(include=['object']).columns:
                unique_count = df[col].nunique()
                total_count = len(df[col].dropna())
                if total_count > 10 and unique_count == 1:
                    errors.append(ValidationError(
                        row=0,
                        column=col,
                        message=f"Column '{col}' has same value in all rows - check if this is expected",
                        severity="info"
                    ))

        return errors

    async def _process_regenerator_config(self, job: ImportJob, df: pd.DataFrame):
        """Process regenerator configuration import."""
        processed_count = 0
        valid_count = 0
        invalid_count = 0
        errors = []
        warnings = []

        # Get column mapping
        column_mapping = {mapping['source_column']: mapping['target_field']
                         for mapping in job.column_mapping}

        # Initialize validation services
        unit_converter = UnitConversionService(self.db)
        physics_validator = RegeneratorPhysicsValidator(unit_converter)

        for idx, row in df.iterrows():
            row_errors = []
            row_warnings = []

            try:
                # Map columns to target fields
                mapped_data = {}
                for source_col, target_field in column_mapping.items():
                    if source_col in row and pd.notna(row[source_col]):
                        mapped_data[target_field] = row[source_col]

                # Apply unit conversions if specified in column mapping
                await self._apply_unit_conversions(mapped_data, job.column_mapping, unit_converter)

                # Validate physics constraints
                validation_errors = await physics_validator.validate_regenerator_data(mapped_data, idx)

                # Separate errors and warnings
                for error in validation_errors:
                    if error.severity == "error":
                        row_errors.append(error)
                    else:
                        row_warnings.append(error)

                # Only create regenerator record if no critical errors
                if not row_errors:
                    try:
                        # Create regenerator data (this also validates schema)
                        regenerator_data = RegeneratorDataCreate(**mapped_data)

                        # Calculate validation score based on warnings
                        validation_score = max(100.0 - (len(row_warnings) * 5), 60.0)

                        # Create imported regenerator record
                        imported_regenerator = ImportedRegenerator(
                            import_job_id=job.id,
                            **regenerator_data.model_dump(),
                            raw_data=row.to_dict(),
                            is_validated=len(row_errors) == 0,
                            validation_score=validation_score,
                            validation_notes=f"Validated with {len(row_warnings)} warnings"
                        )

                        self.db.add(imported_regenerator)
                        valid_count += 1

                        # Add warnings to global list
                        warnings.extend(row_warnings)

                    except Exception as schema_error:
                        # Schema validation failed
                        row_errors.append(ValidationError(
                            row=idx,
                            column="schema",
                            message=f"Schema validation failed: {str(schema_error)}",
                            severity="error",
                            value=mapped_data
                        ))

                if row_errors:
                    invalid_count += 1
                    errors.extend(row_errors)

            except Exception as e:
                invalid_count += 1
                errors.append(ValidationError(
                    row=idx,
                    column="processing",
                    message=f"Processing error: {str(e)}",
                    severity="error",
                    value=row.to_dict()
                ))

            processed_count += 1

            # Update progress every 10 rows
            if processed_count % 10 == 0:
                job.processed_rows = processed_count
                job.valid_rows = valid_count
                job.invalid_rows = invalid_count
                await self.db.commit()

        # Final update
        job.processed_rows = processed_count
        job.valid_rows = valid_count
        job.invalid_rows = invalid_count
        job.validation_errors = [error.model_dump() for error in errors]
        job.validation_warnings = [warning.model_dump() for warning in warnings]

        await self.db.commit()

    async def _apply_unit_conversions(
        self,
        data: Dict[str, Any],
        column_mappings: List[Dict[str, Any]],
        unit_converter: UnitConversionService
    ):
        """Apply unit conversions to mapped data."""

        for mapping in column_mappings:
            target_field = mapping.get('target_field')
            source_unit = mapping.get('unit')
            conversion_factor = mapping.get('conversion_factor')

            if target_field in data and source_unit:
                value = data[target_field]

                if isinstance(value, (int, float)) and conversion_factor:
                    # Apply simple conversion factor
                    data[target_field] = value * conversion_factor
                elif isinstance(value, (int, float)) and source_unit:
                    # Apply unit conversion service
                    try:
                        # Map field to unit type
                        unit_type_mapping = {
                            'length': 'length',
                            'width': 'length',
                            'height': 'length',
                            'design_temperature': 'temperature',
                            'max_temperature': 'temperature',
                            'working_pressure': 'pressure',
                            'pressure_drop': 'pressure',
                            'air_flow_rate': 'flow_rate',
                            'gas_flow_rate': 'flow_rate',
                            'fuel_consumption': 'power'
                        }

                        if target_field in unit_type_mapping:
                            from app.services.unit_conversion import UnitType
                            unit_type = UnitType(unit_type_mapping[target_field])

                            # Assume target unit is metric (meters, Celsius, Pascal, etc.)
                            target_units = {
                                'length': 'm',
                                'temperature': 'celsius',
                                'pressure': 'pa',
                                'flow_rate': 'm3h',
                                'power': 'w'
                            }

                            target_unit = target_units.get(unit_type_mapping[target_field], source_unit)

                            if source_unit.lower() != target_unit.lower():
                                converted_value = await unit_converter.convert_value(
                                    value, source_unit, target_unit, unit_type
                                )
                                data[target_field] = converted_value

                    except Exception as e:
                        logger.warning(
                            "Unit conversion failed",
                            field=target_field,
                            source_unit=source_unit,
                            error=str(e)
                        )

    async def _process_material_properties(self, job: ImportJob, df: pd.DataFrame):
        """Process material properties import."""
        # Placeholder for material properties processing
        # This would be implemented similar to regenerator config
        pass

    async def dry_run_import(
        self,
        user_id: str,
        file_path: str,
        column_mapping: List[ColumnMapping],
        import_type: ImportType,
        processing_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform dry run import to validate data without saving to database.

        Args:
            user_id: ID of the user
            file_path: Path to the uploaded file
            column_mapping: Column mapping configuration
            import_type: Type of import
            processing_options: Additional processing options

        Returns:
            Dry run results with validation summary
        """
        try:
            # Read the full file
            df = pd.read_excel(file_path)
            total_rows = len(df)

            # Initialize counters and collections
            valid_count = 0
            invalid_count = 0
            warning_count = 0
            errors = []
            warnings = []
            sample_valid_data = []
            sample_invalid_data = []

            # Get column mapping dict
            column_mapping_dict = {mapping.source_column: mapping for mapping in column_mapping}

            # Initialize services
            unit_converter = UnitConversionService(self.db)
            physics_validator = RegeneratorPhysicsValidator(unit_converter)

            logger.info(
                "Starting dry run import",
                user_id=user_id,
                total_rows=total_rows,
                import_type=import_type
            )

            # Process each row
            for idx, row in df.iterrows():
                if idx >= 1000:  # Limit dry run to first 1000 rows for performance
                    break

                row_errors = []
                row_warnings = []

                try:
                    # Map columns to target fields
                    mapped_data = {}
                    for source_col, mapping in column_mapping_dict.items():
                        if source_col in row and pd.notna(row[source_col]) and mapping.target_field != "unmapped":
                            value = row[source_col]

                            # Apply data type conversion
                            try:
                                if mapping.data_type == 'float':
                                    value = float(value)
                                elif mapping.data_type == 'integer':
                                    value = int(value)
                                elif mapping.data_type == 'boolean':
                                    value = bool(value)
                                elif mapping.data_type == 'string':
                                    value = str(value).strip()

                                mapped_data[mapping.target_field] = value

                            except (ValueError, TypeError) as e:
                                row_errors.append(ValidationError(
                                    row=int(idx),
                                    column=source_col,
                                    message=f"Data type conversion failed: {str(e)}",
                                    severity="error",
                                    value=str(value)
                                ))

                    # Apply unit conversions if specified
                    await self._apply_unit_conversions(mapped_data, column_mapping, unit_converter)

                    # Validate physics constraints if regenerator config
                    if import_type == ImportType.REGENERATOR_CONFIG and mapped_data:
                        validation_errors = await physics_validator.validate_regenerator_data(mapped_data, idx)

                        for error in validation_errors:
                            if error.severity == "error":
                                row_errors.append(error)
                            else:
                                row_warnings.append(error)

                    # Check if row is valid
                    if not row_errors:
                        valid_count += 1
                        if len(sample_valid_data) < 5:  # Keep sample of valid data
                            sample_valid_data.append({
                                'row': int(idx),
                                'data': mapped_data,
                                'warnings': [w.message for w in row_warnings]
                            })
                    else:
                        invalid_count += 1
                        if len(sample_invalid_data) < 5:  # Keep sample of invalid data
                            sample_invalid_data.append({
                                'row': int(idx),
                                'data': mapped_data,
                                'errors': [e.message for e in row_errors]
                            })

                    # Collect errors and warnings
                    errors.extend(row_errors)
                    warnings.extend(row_warnings)
                    if row_warnings:
                        warning_count += 1

                except Exception as e:
                    invalid_count += 1
                    error = ValidationError(
                        row=int(idx),
                        column="processing",
                        message=f"Row processing error: {str(e)}",
                        severity="error"
                    )
                    errors.append(error)

            # Calculate statistics
            processed_rows = min(len(df), 1000)
            success_rate = (valid_count / processed_rows * 100) if processed_rows > 0 else 0

            logger.info(
                "Dry run import completed",
                total_rows=total_rows,
                processed_rows=processed_rows,
                valid_count=valid_count,
                invalid_count=invalid_count,
                success_rate=success_rate
            )

            return {
                'success': True,
                'summary': {
                    'total_rows': total_rows,
                    'processed_rows': processed_rows,
                    'valid_rows': valid_count,
                    'invalid_rows': invalid_count,
                    'warning_rows': warning_count,
                    'success_rate': round(success_rate, 2)
                },
                'validation': {
                    'errors': [error.model_dump() for error in errors[:50]],  # Limit to first 50 errors
                    'warnings': [warning.model_dump() for warning in warnings[:50]],
                    'error_count': len(errors),
                    'warning_count': len(warnings)
                },
                'samples': {
                    'valid_data': sample_valid_data,
                    'invalid_data': sample_invalid_data
                },
                'recommendations': self._generate_import_recommendations(
                    success_rate, errors, warnings, total_rows
                )
            }

        except Exception as e:
            logger.error("Dry run import failed", error=str(e), user_id=user_id)
            return {
                'success': False,
                'error': str(e),
                'summary': {
                    'total_rows': 0,
                    'processed_rows': 0,
                    'valid_rows': 0,
                    'invalid_rows': 0,
                    'warning_rows': 0,
                    'success_rate': 0
                }
            }

    def _generate_import_recommendations(
        self,
        success_rate: float,
        errors: List[ValidationError],
        warnings: List[ValidationError],
        total_rows: int
    ) -> List[str]:
        """
        Generate recommendations based on dry run results.

        Args:
            success_rate: Percentage of valid rows
            errors: List of validation errors
            warnings: List of validation warnings
            total_rows: Total number of rows

        Returns:
            List of recommendations
        """
        recommendations = []

        if success_rate < 50:
            recommendations.append(
                "⚠️ Low success rate detected. Review column mappings and data quality before import."
            )
        elif success_rate < 80:
            recommendations.append(
                "⚡ Moderate success rate. Consider fixing common errors to improve import quality."
            )
        else:
            recommendations.append(
                "✅ Good success rate. Data appears ready for import."
            )

        # Analyze common error types
        error_types = {}
        for error in errors:
            error_type = error.column
            error_types[error_type] = error_types.get(error_type, 0) + 1

        if error_types:
            most_common_error = max(error_types, key=error_types.get)
            recommendations.append(
                f"🔧 Most common errors in column '{most_common_error}' ({error_types[most_common_error]} occurrences)"
            )

        if len(warnings) > total_rows * 0.1:  # More than 10% of rows have warnings
            recommendations.append(
                "⚠️ Many warnings detected. Review data for potential quality issues."
            )

        if total_rows > 10000:
            recommendations.append(
                "📊 Large dataset detected. Consider processing in smaller batches for better performance."
            )

        return recommendations