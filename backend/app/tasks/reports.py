"""
Report generation tasks for Celery.

Zadania generowania raportów.
"""

from app.celery import celery_app


@celery_app.task
def generate_pdf_report_task(scenario_id: str, template: str) -> dict:
    """
    Generate PDF report in background.

    Args:
        scenario_id: Scenario ID
        template: Report template type

    Returns:
        Report generation results
    """
    # Placeholder for actual PDF generation logic
    return {
        "status": "SUCCESS",
        "scenario_id": scenario_id,
        "template": template,
        "file_path": f"/reports/{scenario_id}.pdf",
    }


@celery_app.task
def generate_xlsx_report_task(scenario_id: str, include_charts: bool = True) -> dict:
    """
    Generate XLSX report in background.

    Args:
        scenario_id: Scenario ID
        include_charts: Whether to include charts

    Returns:
        Report generation results
    """
    # Placeholder for actual XLSX generation logic
    return {
        "status": "SUCCESS",
        "scenario_id": scenario_id,
        "include_charts": include_charts,
        "file_path": f"/reports/{scenario_id}.xlsx",
    }