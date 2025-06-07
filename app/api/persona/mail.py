from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import textwrap
import json
from datetime import datetime

from email.mime.application import MIMEApplication

from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import sys
from lxml.html.diff import htmldiff
from os import environ as env
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

load_dotenv()

def split_text(text, max_chars=100):
    return textwrap.wrap(text, width=max_chars)

def draw_wrapped_text(c, x, y, text, font="Helvetica", font_size=10, line_height=14):
    c.setFont(font, font_size)
    for line in split_text(text):
        c.drawString(x, y, line)
        y -= line_height
        if y < 60:
            c.showPage()
            y = letter[1] - 60
            c.setFont(font, font_size)
    return y

def draw_enhanced_wrapped_text(c, x, y, text, font="Helvetica", font_size=10, line_height=14, max_chars=90, color=colors.black):
    """Enhanced text wrapping with color support and better formatting"""
    c.setFont(font, font_size)
    c.setFillColor(color)
    
    # Split text into paragraphs first
    paragraphs = text.split('\n') if '\n' in text else [text]
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            y -= line_height // 2
            continue
            
        lines = textwrap.wrap(paragraph, width=max_chars)
        for line in lines:
            if y < 80:  # Page break with more margin
                c.showPage()
                # Add header on new page
                draw_page_header(c)
                y = letter[1] - 120
                c.setFont(font, font_size)
                c.setFillColor(color)
            
            c.drawString(x, y, line)
            y -= line_height
        
        # Add space between paragraphs
        y -= line_height // 2
    
    return y

def draw_page_header(c):
    """Draw header on each page"""
    width, height = letter
    margin = 50
    
    # Header background
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.rect(0, height - 60, width, 60, fill=1, stroke=0)
    
    # Header text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - 35, "🧠 SoulScript Therapy Assessment Report")
    
    # Date
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, height - 35, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Confidentiality notice
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(margin, height - 50, "CONFIDENTIAL - For Therapeutic Use Only")

def draw_section_header(c, x, y, text, width):
    """Draw an enhanced section header with styling"""
    header_height = 25
    
    # Background gradient effect (simulated with rectangles)
    c.setFillColor(colors.HexColor('#34495E'))
    c.rect(x - 15, y - 5, width - 2 * x + 30, header_height, fill=1, stroke=0)
    
    # Border
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(2)
    c.rect(x - 15, y - 5, width - 2 * x + 30, header_height, fill=0, stroke=1)
    
    # Text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y + 5, text)
    
    return y - 35

def draw_subsection_header(c, x, y, text):
    """Draw a subsection header"""
    c.setFillColor(colors.HexColor('#3498DB'))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"▶ {text}")
    return y - 20

def draw_metric_box(c, x, y, name, score, width=200):
    """Draw a styled metric box with score visualization"""
    box_height = 30
    
    # Determine color based on score
    if score >= 7:
        bg_color = colors.HexColor('#E74C3C')  # Red
        text_color = colors.white
        status = "HIGH"
    elif score >= 5:
        bg_color = colors.HexColor('#F39C12')  # Orange
        text_color = colors.white
        status = "MODERATE"
    else:
        bg_color = colors.HexColor('#27AE60')  # Green
        text_color = colors.white
        status = "LOW"
    
    # Draw background
    c.setFillColor(bg_color)
    c.roundRect(x, y - box_height + 5, width, box_height, 8, fill=1, stroke=0)
    
    # Draw border
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(1)
    c.roundRect(x, y - box_height + 5, width, box_height, 8, fill=0, stroke=1)
    
    # Draw text
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 10, y - 10, name)
    c.drawRightString(x + width - 10, y - 10, f"{score}/10 ({status})")
    
    return y - box_height - 5

def create_pdf_from_json(json_data, filename):
    """Enhanced PDF creation with improved styling and layout"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin
    
    # Enhanced Title Page
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.rect(0, height - 150, width, 150, fill=1, stroke=0)
    
    # Main title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    title_text = "🧠 THERAPY ASSESSMENT REPORT"
    text_width = c.stringWidth(title_text, "Helvetica-Bold", 24)
    c.drawString((width - text_width) / 2, height - 80, title_text)
    
    # Subtitle
    c.setFont("Helvetica", 14)
    subtitle = "Comprehensive Psychological Analysis"
    subtitle_width = c.stringWidth(subtitle, "Helvetica", 14)
    c.drawString((width - subtitle_width) / 2, height - 110, subtitle)
    
    # System info
    c.setFont("Helvetica-Oblique", 10)
    system_info = f"Generated by SoulScript System | {datetime.now().strftime('%B %d, %Y')}"
    system_width = c.stringWidth(system_info, "Helvetica-Oblique", 10)
    c.drawString((width - system_width) / 2, height - 135, system_info)
    
    y = height - 200
    
    # Important notice box
    notice_y = y - 50
    c.setFillColor(colors.HexColor('#E8F4FD'))
    c.roundRect(margin, notice_y - 40, width - 2 * margin, 70, 10, fill=1, stroke=1)
    
    c.setFillColor(colors.HexColor('#2980B9'))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin + 20, notice_y - 5, "⚠️ CONFIDENTIALITY NOTICE")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    notice_text = "This report contains sensitive psychological information intended solely for therapeutic purposes."
    y = draw_enhanced_wrapped_text(c, margin + 20, notice_y - 25, notice_text, max_chars=80)
    
    y = notice_y - 80
    
    # Priority sections mapping
    priority_sections = {
        'behavioralPatterns': ('🧭 BEHAVIORAL PATTERNS', 1),
        'riskAssessment': ('⚠️ RISK ASSESSMENT', 2),
        'psychologicalFormulation': ('🧩 PSYCHOLOGICAL FORMULATION', 3),
        'strengthsAndResources': ('💪 STRENGTHS & RESOURCES', 4),
        'therapyRecommendations': ('🎯 THERAPY RECOMMENDATIONS', 5)
    }
    
    # Get info sections
    info_data = json_data.get("info", {})
    
    # Sort sections by priority
    sorted_sections = []
    for section_key, items in info_data.items():
        if section_key in priority_sections:
            priority = priority_sections[section_key][1]
            title = priority_sections[section_key][0]
            sorted_sections.append((priority, section_key, title, items))
        else:
            # Add other sections at the end
            title = section_key.replace("_", " ").title()
            sorted_sections.append((99, section_key, title, items))
    
    sorted_sections.sort(key=lambda x: x[0])
    
    # Process each section
    for priority, section_key, section_title, items in sorted_sections:
        if not items:
            continue
            
        # Check if section has meaningful content
        has_content = any(item.get("value", "").strip() and 
                         item.get("value", "").lower() not in ["unclear", "not provided"] 
                         for item in items)
        
        if not has_content:
            continue
        
        # Start new page for major sections
        if y < 200:
            c.showPage()
            draw_page_header(c)
            y = height - 120
        
        # Draw section header
        y = draw_section_header(c, margin, y, section_title, width)
        
        # Group items by label for better organization
        grouped_items = {}
        for item in items:
            label = item.get("label", "General")
            value = item.get("value", "")
            if value and value.lower() not in ["unclear", "not provided"]:
                if label not in grouped_items:
                    grouped_items[label] = []
                grouped_items[label].append(value)
        
        # Render grouped content
        for label, values in grouped_items.items():
            if y < 120:
                c.showPage()
                draw_page_header(c)
                y = height - 120
            
            # Subsection header with special styling for important sections
            if section_key == 'riskAssessment':
                if 'risk' in label.lower():
                    y = draw_subsection_header(c, margin, y, f"🚨 {label}")
                elif 'protective' in label.lower():
                    y = draw_subsection_header(c, margin, y, f"🛡️ {label}")
                else:
                    y = draw_subsection_header(c, margin, y, label)
            else:
                y = draw_subsection_header(c, margin, y, label)
            
            # Content
            for value in values:
                if y < 100:
                    c.showPage()
                    draw_page_header(c)
                    y = height - 120
                
                # Choose color based on content type
                text_color = colors.black
                if section_key == 'riskAssessment' and 'risk' in label.lower():
                    text_color = colors.HexColor('#C0392B')
                elif 'strength' in label.lower() or 'protective' in label.lower():
                    text_color = colors.HexColor('#27AE60')
                
                y = draw_enhanced_wrapped_text(c, margin + 20, y, f"• {value}", 
                                             font_size=10, color=text_color)
                y -= 5
            
            y -= 10
        
        y -= 20
    
    # Enhanced Graph Section
    if "graph" in json_data:
        # Start new page for graphs
        c.showPage()
        draw_page_header(c)
        y = height - 120
        
        y = draw_section_header(c, margin, y, "📊 PSYCHOLOGICAL METRICS", width)
        
        # Create summary of all metrics
        all_metrics = []
        for graph_type, entries in json_data["graph"].items():
            for entry in entries:
                name = entry.get('name', '')
                score = entry.get('score', entry.get('severity', 0))
                all_metrics.append((name, score, graph_type))
        
        # Sort by severity (highest first)
        all_metrics.sort(key=lambda x: x[1], reverse=True)
        
        # Draw metrics with visual indicators
        y = draw_subsection_header(c, margin, y, "Assessment Scores (Ranked by Severity)")
        
        for name, score, category in all_metrics:
            if y < 140:
                c.showPage()
                draw_page_header(c)
                y = height - 120
            
            y = draw_metric_box(c, margin + 20, y, f"{name} ({category.title()})", score, width - 2*margin - 40)
            y -= 5
        
        # Add interpretation guide
        y -= 20
        if y < 200:
            c.showPage()
            draw_page_header(c)
            y = height - 120
        
        y = draw_subsection_header(c, margin, y, "📈 Score Interpretation Guide")
        
        interpretation = [
            "🟢 Low (1-3): Minimal concern, within normal range",
            "🟡 Moderate (4-6): Some attention needed, monitor progress", 
            "🔴 High (7-10): Significant concern, priority for intervention"
        ]
        
        for interp in interpretation:
            y = draw_enhanced_wrapped_text(c, margin + 20, y, interp, font_size=10)
            y -= 5
    
    # Footer on last page
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.drawString(margin, 30, "End of Report - All information confidential and for therapeutic use only")
    c.drawRightString(width - margin, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    c.save()
    print(f"✅ Enhanced PDF report generated: {filename}")


def sendEmail(Name, To, subject, message, attachment_path=None):
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()

    email = env["EMAIL"]
    password = env["PASSWORD"]
    s.login(email, password)

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = Name
    msg["To"] = To

    text = message.replace("<br>", "\n")
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(message, "html")

    msg.attach(part1)
    msg.attach(part2)

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

    s.sendmail(Name, To, msg.as_string())
    s.quit()