"""
PDF report generation service.

Serwis generowania raportów PDF.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.shapes import Drawing
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFGenerator:
    """PDF report generator using ReportLab."""

    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")

        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""

        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f2937')
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#374151')
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=20,
            textColor=colors.HexColor('#4b5563'),
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=5
        ))

        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold'
        ))

        # Warning style
        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold'
        ))

    def generate_report_pdf(self, report_data: Dict[str, Any], sections: List[Dict[str, Any]], output_path: Path) -> Path:
        """Generate a complete PDF report."""

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        story = []

        # Title page
        story.extend(self._create_title_page(report_data))

        # Executive summary
        story.extend(self._create_executive_summary(report_data, sections))

        # Table of contents
        story.extend(self._create_table_of_contents(sections))

        # Report sections
        for section in sections:
            story.extend(self._create_section(section))

        # Footer
        story.extend(self._create_footer())

        doc.build(story)
        return output_path

    def _create_title_page(self, report_data: Dict[str, Any]) -> List:
        """Create report title page."""
        story = []

        # Logo placeholder
        story.append(Spacer(1, 2*inch))

        # Report title
        title = Paragraph(report_data.get('title', 'System Report'), self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Report type
        report_type = report_data.get('report_type', '').replace('_', ' ').title()
        subtitle = Paragraph(f"{report_type} Report", self.styles['Subtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 0.5*inch))

        # Description
        if report_data.get('description'):
            desc = Paragraph(report_data['description'], self.styles['Normal'])
            story.append(desc)
            story.append(Spacer(1, 0.3*inch))

        # Generation info
        generated_at = datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')
        info_data = [
            ['Generated:', generated_at],
            ['Report ID:', report_data.get('id', 'N/A')],
            ['Format:', report_data.get('format', 'PDF').upper()],
            ['Status:', report_data.get('status', 'completed').title()]
        ]

        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111827')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('RIGHTPADDING', (0, 0), (0, -1), 20),
            ('LEFTPADDING', (1, 0), (1, -1), 10),
        ]))

        story.append(Spacer(1, 1*inch))
        story.append(info_table)

        # Page break
        story.append(PageBreak())

        return story

    def _create_executive_summary(self, report_data: Dict[str, Any], sections: List[Dict[str, Any]]) -> List:
        """Create executive summary section."""
        story = []

        story.append(Paragraph("Executive Summary", self.styles['Subtitle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))

        # Key findings
        summary_text = f"""
        This {report_data.get('report_type', '').replace('_', ' ')} report provides comprehensive insights
        into system performance and optimization results. The report covers data from
        {report_data.get('date_range', {}).get('start_date', 'N/A')} to
        {report_data.get('date_range', {}).get('end_date', 'N/A')}.
        """

        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 20))

        # Key metrics summary
        if sections:
            story.append(Paragraph("Key Highlights:", self.styles['SectionHeader']))

            highlights = []
            for section in sections[:3]:  # Top 3 sections
                data = section.get('data', {})
                if data:
                    for key, value in list(data.items())[:2]:  # Top 2 metrics per section
                        if isinstance(value, (int, float)):
                            highlights.append(f"• {key.replace('_', ' ').title()}: {value:,.2f}")
                        elif isinstance(value, str) and value.replace('.', '').isdigit():
                            highlights.append(f"• {key.replace('_', ' ').title()}: {value}")

            for highlight in highlights[:6]:  # Top 6 highlights
                story.append(Paragraph(highlight, self.styles['Normal']))
                story.append(Spacer(1, 8))

        story.append(PageBreak())
        return story

    def _create_table_of_contents(self, sections: List[Dict[str, Any]]) -> List:
        """Create table of contents."""
        story = []

        story.append(Paragraph("Table of Contents", self.styles['Subtitle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))

        toc_data = [['Section', 'Page']]
        page_num = 4  # Starting page after title, summary, TOC

        for i, section in enumerate(sections, 1):
            section_name = section.get('name', f'Section {i}').replace('_', ' ').title()
            toc_data.append([f"{i}. {section_name}", str(page_num)])
            page_num += 1

        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(toc_table)
        story.append(PageBreak())

        return story

    def _create_section(self, section: Dict[str, Any]) -> List:
        """Create a report section."""
        story = []

        # Section title
        section_name = section.get('name', 'Unnamed Section').replace('_', ' ').title()
        story.append(Paragraph(section_name, self.styles['Subtitle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))

        # Section data
        data = section.get('data', {})
        if data:
            story.extend(self._create_data_table(data))

        # Charts
        charts = section.get('charts', [])
        for chart in charts:
            story.extend(self._create_chart(chart))

        story.append(PageBreak())
        return story

    def _create_data_table(self, data: Dict[str, Any]) -> List:
        """Create a data table from section data."""
        story = []

        # Convert data to table format
        table_data = [['Metric', 'Value']]

        for key, value in data.items():
            metric_name = key.replace('_', ' ').title()

            if isinstance(value, float):
                if 'percentage' in key.lower() or 'rate' in key.lower():
                    formatted_value = f"{value:.1f}%"
                else:
                    formatted_value = f"{value:,.2f}"
            elif isinstance(value, int):
                formatted_value = f"{value:,}"
            elif isinstance(value, dict):
                formatted_value = json.dumps(value, indent=2)[:100] + "..." if len(str(value)) > 100 else json.dumps(value)
            else:
                formatted_value = str(value)

            table_data.append([metric_name, formatted_value])

        if len(table_data) > 1:  # Only create table if there's data
            table = Table(table_data, colWidths=[3*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ]))

            story.append(table)
            story.append(Spacer(1, 20))

        return story

    def _create_chart(self, chart_config: Dict[str, Any]) -> List:
        """Create a chart from chart configuration."""
        story = []

        chart_type = chart_config.get('type', 'bar')
        chart_title = chart_config.get('title', 'Chart')

        # Chart title
        story.append(Paragraph(chart_title, self.styles['SectionHeader']))

        # For now, create a placeholder for charts
        # In a full implementation, you would generate actual charts
        story.append(Paragraph(f"[{chart_type.upper()} CHART PLACEHOLDER]", self.styles['Normal']))
        story.append(Paragraph(f"Data: {chart_config.get('data', [])}", self.styles['Normal']))
        story.append(Spacer(1, 20))

        return story

    def _create_footer(self) -> List:
        """Create report footer."""
        story = []

        story.append(Spacer(1, 1*inch))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#d1d5db')))
        story.append(Spacer(1, 10))

        footer_text = f"""
        This report was generated automatically by the Forglass Regenerator Optimizer (FRO) system.
        Generated on {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}.

        For questions or support, please contact your system administrator.
        """

        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER
        )

        story.append(Paragraph(footer_text, footer_style))

        return story


# Fallback simple PDF generator for when ReportLab is not available
class SimplePDFGenerator:
    """Simple text-based PDF generator fallback."""

    def generate_report_pdf(self, report_data: Dict[str, Any], sections: List[Dict[str, Any]], output_path: Path) -> Path:
        """Generate a simple text-based PDF report."""

        # Create a simple text file as fallback
        with open(output_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
            f.write(f"REPORT: {report_data.get('title', 'System Report')}\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Report Type: {report_data.get('report_type', 'N/A')}\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            f.write(f"Format: {report_data.get('format', 'PDF')}\n\n")

            for i, section in enumerate(sections, 1):
                f.write(f"{i}. {section.get('name', 'Section').replace('_', ' ').title()}\n")
                f.write("-" * 30 + "\n")

                data = section.get('data', {})
                for key, value in data.items():
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")

                f.write("\n")

        return output_path.with_suffix('.txt')