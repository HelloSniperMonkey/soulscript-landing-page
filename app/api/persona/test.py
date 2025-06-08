import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime
import textwrap

def create_pdf_from_json_chat(json_data, output_filename="psychological_assessment_report.pdf"):
    """
    Generate a beautifully formatted PDF report from psychological assessment JSON data.
    
    Args:
        json_data: Either a JSON string or a dictionary containing the assessment data
        output_filename: Name of the output PDF file
    
    Returns:
        str: Success message with filename
    """
    
    # Parse JSON if it's a string
    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return f"Error parsing JSON: {e}"
    else:
        data = json_data
    
    # Create PDF document with professional margins
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=60,
        leftMargin=60,
        topMargin=80,
        bottomMargin=80
    )
    
    # Get base styles
    styles = getSampleStyleSheet()
    
    # Enhanced custom styles with modern design
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=40,
        spaceBefore=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a'),  # Deep blue
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=colors.HexColor('#3b82f6'),  # Lighter blue
        borderPadding=15,
        backColor=colors.HexColor('#f8fafc'),  # Light gray background
        borderRadius=5
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569'),  # Gray
        fontName='Helvetica-Oblique'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        spaceBefore=25,
        textColor=colors.HexColor('#1e40af'),  # Blue
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.HexColor('#3b82f6'),
        borderPadding=10,
        backColor=colors.HexColor('#eff6ff'),  # Very light blue
        leftIndent=0,
        borderRadius=3
    )
    
    subsection_style = ParagraphStyle(
        'SubsectionHeader',
        parent=styles['Heading3'],
        fontSize=13,
        spaceAfter=8,
        spaceBefore=15,
        textColor=colors.HexColor('#059669'),  # Green
        fontName='Helvetica-Bold',
        leftIndent=15,
        borderWidth=0,
        borderColor=colors.HexColor('#10b981'),
        borderPadding=5,
        backColor=colors.HexColor('#f0fdf4')  # Very light green
    )
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        spaceBefore=4,
        alignment=TA_JUSTIFY,
        leftIndent=25,
        rightIndent=10,
        textColor=colors.HexColor('#374151'),  # Dark gray
        fontName='Helvetica',
        leading=14  # Line spacing
    )
    
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=content_style,
        backColor=colors.HexColor('#fef3c7'),  # Light yellow
        borderWidth=1,
        borderColor=colors.HexColor('#f59e0b'),  # Orange
        borderPadding=8,
        leftIndent=20,
        rightIndent=20,
        borderRadius=3
    )
    
    info_box_style = ParagraphStyle(
        'InfoBox',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=15,
        spaceBefore=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f2937'),
        backColor=colors.HexColor('#f3f4f6'),
        borderWidth=1,
        borderColor=colors.HexColor('#d1d5db'),
        borderPadding=12,
        borderRadius=5
    )
    
    # Story list to hold all content
    story = []
    
    # Header with logo placeholder and title
    story.append(Spacer(1, 20))
    story.append(Paragraph("PSYCHOLOGICAL ASSESSMENT REPORT", title_style))
    story.append(Spacer(1, 10))
    
    # Subtitle with generation info
    date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated on {date_str}", subtitle_style))
    
    # Professional separator line
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3b82f6')))
    story.append(Spacer(1, 30))
    
    # Document info box
    story.append(Paragraph(
        "<b>CONFIDENTIAL DOCUMENT</b><br/>"
        "This report contains sensitive psychological assessment information.<br/>"
        "Handle in accordance with applicable privacy regulations.",
        info_box_style
    ))
    story.append(Spacer(1, 20))
    
    # Enhanced function to format section data
    def format_section(section_data, section_title, is_important=False):
        # Add section header with improved styling
        story.append(Paragraph(section_title.upper(), section_style))
        
        # Handle direct string values
        if isinstance(section_data, str):
            if section_data and section_data.lower() not in ["unclear", "not provided", "none", ""]:
                # Use highlight style for important sections
                style_to_use = highlight_style if is_important else content_style
                story.append(Paragraph(f"• {section_data}", style_to_use))
                story.append(Spacer(1, 8))
        
        # Handle dictionary sections
        elif isinstance(section_data, dict):
            for key, value in section_data.items():
                if value and str(value).lower() not in ["unclear", "not provided", "none", ""]:
                    # Format key name
                    key_formatted = key.replace("_", " ").replace("'", "").title()
                    key_formatted = key_formatted.replace("And", "and").replace("Of", "of")
                    
                    # Add subsection header
                    story.append(Paragraph(f"◆ {key_formatted}", subsection_style))
                    
                    # Format content with better text wrapping
                    content_text = str(value).strip()
                    if len(content_text) > 120:
                        # For longer text, add paragraph breaks for better readability
                        sentences = content_text.split('. ')
                        formatted_sentences = []
                        for i, sentence in enumerate(sentences):
                            if sentence and not sentence.endswith('.') and i < len(sentences) - 1:
                                sentence += '.'
                            formatted_sentences.append(sentence)
                        
                        # Group sentences into paragraphs
                        paragraphs = []
                        current_paragraph = []
                        char_count = 0
                        
                        for sentence in formatted_sentences:
                            if char_count + len(sentence) > 300 and current_paragraph:
                                paragraphs.append(' '.join(current_paragraph))
                                current_paragraph = [sentence]
                                char_count = len(sentence)
                            else:
                                current_paragraph.append(sentence)
                                char_count += len(sentence)
                        
                        if current_paragraph:
                            paragraphs.append(' '.join(current_paragraph))
                        
                        for paragraph in paragraphs:
                            story.append(Paragraph(paragraph, content_style))
                            story.append(Spacer(1, 6))
                    else:
                        story.append(Paragraph(content_text, content_style))
                        story.append(Spacer(1, 8))
        
        # Handle list sections
        elif isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if value and str(value).lower() not in ["unclear", "not provided", "none", ""]:
                            key_formatted = key.replace("_", " ").title()
                            story.append(Paragraph(f"◆ {key_formatted}", subsection_style))
                            story.append(Paragraph(str(value), content_style))
                            story.append(Spacer(1, 8))
        
        # Add section separator
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="80%", thickness=1, color=colors.HexColor('#e5e7eb')))
        story.append(Spacer(1, 20))
    
    # Process sections with improved organization and importance flags
    section_order = [
        ('Personal Information', 'Personal Information', True),
        ('Current Emotional State', 'Current Emotional State', True),
        ('Mental Health History', 'Mental Health History', True),
        ('Trauma History', 'Trauma History', True),
        ('Therapy Goals', 'Therapy Goals', True),
        ('Employment & Lifestyle', 'Employment & Lifestyle', False),
        ('Behavioral Patterns', 'Behavioral Patterns', False),
        ('Support System', 'Support System', False)
    ]
    
    # Process new JSON structure
    for key, title, is_important in section_order:
        if key in data:
            format_section(data[key], title, is_important)
    
    # Handle backward compatibility with old nested structure
    info_data = data.get('info', {})
    if info_data:
        legacy_sections = [
            ('demographics', 'Demographics', True),
            ('therapyReasons', 'Therapy Goals & Reasons', True),
            ('mentalHealthHistory', 'Mental Health History', True),
            ('traumaAndAdverseExperiences', 'Trauma & Adverse Experiences', True),
            ('riskAssessment', 'Risk Assessment', True),
            ('psychologicalFormulation', 'Psychological Formulation', True),
            ('therapyRecommendations', 'Therapy Recommendations', True),
            ('familyEmployment', 'Family & Employment Status', False),
            ('substanceUse', 'Substance Use', False),
            ('healthAndLifestyle', 'Health & Lifestyle', False),
            ('medicalAndMedicationHistory', 'Medical & Medication History', False),
            ('behavioralPatterns', 'Behavioral Patterns', False),
            ('strengthsAndResources', 'Strengths & Resources', False)
        ]
        
        for key, title, is_important in legacy_sections:
            if key in info_data:
                format_section(info_data[key], title, is_important)
    
    # Professional footer section
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3b82f6')))
    story.append(Spacer(1, 20))
    
    # Footer content
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=8
    )
    
    story.append(Paragraph("<b>END OF ASSESSMENT REPORT</b>", footer_style))
    story.append(Spacer(1, 15))
    
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#6b7280'),
        leftIndent=40,
        rightIndent=40,
        backColor=colors.HexColor('#f9fafb'),
        borderWidth=1,
        borderColor=colors.HexColor('#d1d5db'),
        borderPadding=15,
        borderRadius=5
    )
    
    story.append(Paragraph(
        "<b>IMPORTANT DISCLAIMER:</b> This report is generated from assessment data and is intended for "
        "use by qualified mental health professionals only. The information contained herein should be "
        "interpreted within the context of a comprehensive clinical evaluation. This document is "
        "confidential and should be handled in accordance with applicable privacy and ethical guidelines.",
        disclaimer_style
    ))
    
    try:
        # Build PDF with enhanced error handling
        doc.build(story)
        return f"✅ Enhanced PDF successfully generated: {output_filename}"
    except Exception as e:
        return f"❌ Error generating PDF: {e}"


# Additional utility function for creating table-based layouts (optional enhancement)
def create_info_table(data_dict, col_widths=None):
    """
    Create a formatted table for structured data display
    """
    from reportlab.platypus import Table, TableStyle
    
    if not data_dict:
        return None
    
    # Prepare table data
    table_data = []
    for key, value in data_dict.items():
        if value and str(value).lower() not in ["unclear", "not provided", "none", ""]:
            key_formatted = key.replace("_", " ").title()
            table_data.append([key_formatted, str(value)])
    
    if not table_data:
        return None
    
    # Create table
    if col_widths is None:
        col_widths = [150, 350]  # Default column widths
    
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    return table


def example_usage():
    """Example of how to use the function with sample data"""
    
    # Sample JSON data (you can replace this with your actual data)
    sample_json = '''
    {
  "Personal Information": {
    "Name": "Vibhuti",
    "Age": "unclear",
    "Gender": "unclear",
    "Contact": "unclear"
  },
  "Employment & Lifestyle": {
    "Employment Status": "unclear",
    "Relationship Status": "unclear",
    "Daily Routine": "unclear"
  },
  "Mental Health History": {
    "Past Diagnoses": "unclear",
    "Previous Treatments": "unclear",
    "Family History of Mental Health Conditions": "unclear"
  },
  "Trauma History": {
    "Significant Life Events": "unclear",
    "Impact": "unclear",
    "Coping Mechanisms": "unclear"
  },
  "Behavioral Patterns": {
    "Substance Use": "unclear",
    "Addiction or Compulsive Behaviors": "unclear"
  },
  "Support System": {
    "Social Support": "unclear",
    "Family & Friends' Role": "unclear"
  },
  "Current Emotional State": "nervous",
  "Therapy Goals": "The user has not specified any explicit therapy goals but is looking for a listening ear and support. They are also interested in communicating in Hindi."
}

    '''
    
    result = create_pdf_from_json_chat(sample_json, "sample_assessment.pdf")
    print(result)

# For loading from file
def create_pdf_from_json_file(json_file_path, output_filename="psychological_assessment.pdf"):
    """
    Load JSON from file and generate PDF
    
    Args:
        json_file_path: Path to the JSON file
        output_filename: Name of the output PDF file
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        
        return create_pdf_from_json_chat(json_data, output_filename)
    except FileNotFoundError:
        return f"Error: File {json_file_path} not found"
    except Exception as e:
        return f"Error reading file: {e}"

if __name__ == "__main__":
    # Example usage
    example_usage()