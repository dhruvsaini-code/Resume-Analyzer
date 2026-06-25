import os
import io
import matplotlib
matplotlib.use('Agg') # Headless plotting to prevent GUI rendering issues
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.platypus.flowables import Image as RLImage
from reportlab.pdfgen import canvas
from typing import Dict, Any, List

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render total page count
    and draw consistent headers/footers on all pages after the cover page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # We suppress headers/footers on the cover page (Page 1)
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(40, 755, "ATS SUITABILITY & RESUME ANALYTICS REPORT")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#6B7280"))
            self.drawRightString(572, 755, "SaaS ATS Screening Engine")
            
            # Divider line
            self.setStrokeColor(colors.HexColor("#E5E7EB"))
            self.setLineWidth(0.5)
            self.line(40, 748, 572, 748)
            
            # Footer line
            self.line(40, 48, 572, 48)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#4B5563"))
            self.drawString(40, 32, "Confidential Candidate Screening Profile")
            self.drawRightString(572, 32, f"Page {self._pageNumber} of {page_count}")
            
        self.restoreState()


class PDFReportGenerator:
    """
    Generates a professional multi-page PDF analysis report containing score cards,
    embedded matplotlib charts, skills tables, and structured career roadmaps.
    """
    
    @staticmethod
    def generate_report(
        candidate_name: str,
        contact_info: Dict[str, str],
        ats_results: Dict[str, Any],
        match_results: Dict[str, Any],
        feedback_results: Dict[str, Any],
        predicted_role: str,
        output_path: str
    ) -> str:
        # Ensure output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Setup document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=55, # Increased to leave room for running header
            bottomMargin=55
        )
        
        styles = getSampleStyleSheet()
        
        # Colors
        c_primary = colors.HexColor("#1E3A8A")   # Navy
        c_secondary = colors.HexColor("#0D9488") # Teal
        c_accent = colors.HexColor("#6366F1")    # Indigo
        c_text = colors.HexColor("#1F2937")      # Slate
        c_light = colors.HexColor("#F3F4F6")     # Cool Grey
        
        # Typography
        cover_title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=26,
            leading=32,
            textColor=colors.white,
            spaceAfter=8,
            alignment=1
        )
        
        cover_sub_style = ParagraphStyle(
            'CoverSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#93C5FD"),
            spaceAfter=25,
            alignment=1
        )
        
        h1_style = ParagraphStyle(
            'SectionH1',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=c_primary,
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True
        )
        
        h2_style = ParagraphStyle(
            'SubSectionH2',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=c_secondary,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=c_text
        )
        
        bullet_style = ParagraphStyle(
            'BulletCustom',
            parent=body_style,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=4
        )
        
        score_val_style = ParagraphStyle(
            'ScoreVal',
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=c_secondary,
            alignment=1
        )
        
        score_lbl_style = ParagraphStyle(
            'ScoreLbl',
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=c_text,
            alignment=1
        )

        story = []
        
        # ==========================================
        # PAGE 1: COVER PAGE
        # ==========================================
        
        # Spacer to push cover title down
        story.append(Spacer(1, 30))
        
        # Navy blue cover block
        cover_data = [
            [Paragraph("AI ATS RESUME ANALYTICS REPORT", cover_title_style)],
            [Paragraph("Enterprise SaaS Candidate Suitability & Skill Gaps Assessment", cover_sub_style)]
        ]
        cover_table = Table(cover_data, colWidths=[532])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_primary),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 35),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 1, c_primary),
        ]))
        story.append(cover_table)
        story.append(Spacer(1, 40))
        
        # Profile Details Box
        contact_list = []
        if contact_info.get('email'): contact_list.append(f"<b>Email:</b> {contact_info['email']}")
        if contact_info.get('phone'): contact_list.append(f"<b>Phone:</b> {contact_info['phone']}")
        if contact_info.get('location'): contact_list.append(f"<b>Location:</b> {contact_info['location']}")
        if contact_info.get('linkedin'): contact_list.append("<b>LinkedIn:</b> Connected")
        if contact_info.get('github'): contact_list.append("<b>GitHub:</b> Connected")
        
        details_data = [
            [Paragraph("<b>CANDIDATE INFORMATION</b>", ParagraphStyle('HDetail', fontName='Helvetica-Bold', fontSize=10, textColor=c_primary)), ""],
            [Paragraph(f"<b>Name:</b> {candidate_name}", body_style), Paragraph(f"<b>Target Career Path:</b> {predicted_role}", body_style)],
            [Paragraph("<br/>".join(contact_list) if contact_list else "<b>Contact Status:</b> Incomplete Details", body_style), ""]
        ]
        
        details_table = Table(details_data, colWidths=[266, 266])
        details_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (0, 2), (1, 2)),
            ('BACKGROUND', (0, 0), (-1, -1), c_light),
            ('LINEBELOW', (0, 0), (1, 0), 1, c_primary),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 40))
        
        # Large Score Badges
        ats_score = ats_results.get('overall_score', 0.0)
        match_score = match_results.get('match_score', 0.0)
        
        # Fetch Overall Rating Letter if present in advanced analytics
        overall_rating = "B+"
        if 'rating' in ats_results: # if directly passed
            overall_rating = ats_results['rating']
        elif 'scores' in ats_results:
            # We will recalculate rating if not directly bound
            overall_rating = "A" if ats_score >= 80 else ("B" if ats_score >= 60 else "C")
            
        score_badge_data = [
            [
                Paragraph(f"{ats_score}/100", score_val_style),
                Paragraph(f"{match_score}%", score_val_style),
                Paragraph(overall_rating, ParagraphStyle('RatingVal', fontName='Helvetica-Bold', fontSize=26, leading=30, textColor=c_accent, alignment=1))
            ],
            [
                Paragraph("ATS COMPATIBILITY", score_lbl_style),
                Paragraph("JOB DESCRIPTION MATCH", score_lbl_style),
                Paragraph("OVERALL QUALITY GRADE", score_lbl_style)
            ]
        ]
        score_badge_table = Table(score_badge_data, colWidths=[177, 177, 178])
        score_badge_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#10B981")),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
            ('LINEAFTER', (0, 0), (0, 1), 0.5, colors.HexColor("#A7F3D0")),
            ('LINEAFTER', (1, 0), (1, 1), 0.5, colors.HexColor("#A7F3D0")),
        ]))
        story.append(score_badge_table)
        
        # Force Page Break after Cover Page
        story.append(PageBreak())
        
        # ==========================================
        # PAGE 2: DETAILED SCORES & MATPLOTLIB CHARTS
        # ==========================================
        
        story.append(Paragraph("Executive Analytics Overview", h1_style))
        story.append(Paragraph("A breakdown of your resume metrics calculated across key ATS evaluation areas.", body_style))
        story.append(Spacer(1, 10))
        
        # Generate Matplotlib chart on the fly
        chart_buffer = io.BytesIO()
        plt.figure(figsize=(7, 3.5))
        
        labels = [
            'ATS Compatibility', 'Readability', 'Grammar', 'Experience',
            'Technical Skills', 'Projects', 'Formatting', 'Leadership'
        ]
        
        # Fallback values if scores not mapped
        score_values = [
            ats_score,
            ats_results.get('readability', 75.0),
            ats_results.get('grammar', 82.0),
            ats_results.get('experience_score', 70.0),
            ats_results.get('skills_score', 80.0) / 30.0 * 100.0,
            ats_results.get('projects_score', 75.0),
            ats_results.get('formatting_score', 85.0) / 20.0 * 100.0,
            ats_results.get('leadership_score', 65.0)
        ]
        # Clean scales
        score_values = [max(0.0, min(100.0, v)) for v in score_values]
        
        colors_list = ['#1E3A8A', '#0D9488', '#6366F1', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
        
        plt.barh(labels, score_values, color=colors_list, height=0.6)
        plt.xlim(0, 100)
        plt.xlabel('Score out of 100', fontsize=9, fontweight='bold', color='#1F2937')
        plt.title('Resume Domain Suitability Analysis', fontsize=10, fontweight='bold', color='#1E3A8A')
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
        chart_buffer.seek(0)
        plt.close()
        
        # Embed matplotlib graph as ReportLab Flowable Image
        story.append(RLImage(chart_buffer, width=440, height=210))
        story.append(Spacer(1, 15))
        
        # Section Completions Table
        sec_status = ats_results.get('section_status', {})
        sec_rows = []
        for i, (sec, ok) in enumerate(sec_status.items()):
            badge_color = colors.HexColor("#065F46") if ok else colors.HexColor("#991B1B")
            badge_bg = colors.HexColor("#D1FAE5") if ok else colors.HexColor("#FEE2E2")
            status_text = "Found (Passed)" if ok else "Missing (Failed)"
            
            p_sec = Paragraph(f"<b>{sec.replace('_', ' ').title()}</b>", body_style)
            p_status = Paragraph(f"<font color='{badge_color}'><b>{status_text}</b></font>", body_style)
            
            sec_rows.append([p_sec, p_status])
            
        sec_table = Table(sec_rows, colWidths=[266, 266])
        sec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_light),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(Paragraph("Logical Section Quality Check", h2_style))
        story.append(sec_table)
        
        story.append(PageBreak())
        
        # ==========================================
        # PAGE 3: JOB MATCHING GAPS & AI ROADMAP
        # ==========================================
        
        story.append(Paragraph("Job Description Alignment Audit", h1_style))
        story.append(Paragraph("Detailed mapping of skills overlap, keyword density, and capability gaps.", body_style))
        story.append(Spacer(1, 10))
        
        # Skills list table
        matching_skills = match_results.get('matching_skills', [])
        missing_skills = match_results.get('missing_skills', [])
        
        matching_p = Paragraph(", ".join(matching_skills[:15]) if matching_skills else "None identified in common", body_style)
        missing_p = Paragraph(", ".join(missing_skills[:15]) if missing_skills else "No critical skills missing!", body_style)
        
        skills_data = [
            [Paragraph("<b>Matching Keywords</b>", ParagraphStyle('G1', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#065F46"))), 
             Paragraph("<b>Missing Gaps (Keywords)</b>", ParagraphStyle('R1', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#991B1B")))],
            [matching_p, missing_p]
        ]
        skills_table = Table(skills_data, colWidths=[266, 266])
        skills_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#D1FAE5")),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#FEE2E2")),
            ('BOX', (0, 0), (0, 1), 1, colors.HexColor("#10B981")),
            ('BOX', (1, 0), (1, 1), 1, colors.HexColor("#EF4444")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(skills_table)
        story.append(Spacer(1, 15))
        
        # Capability verification results (seniority, experience, education checks)
        story.append(Paragraph("SaaS Fitment Audit Summaries", h2_style))
        
        fit_items = []
        if 'seniority_match' in match_results:
            sen_m = match_results['seniority_match']
            fit_items.append(Paragraph(f"• <b>Seniority Level Check:</b> {sen_m.get('explanation')}", bullet_style))
        if 'experience_similarity' in match_results:
            exp_m = match_results['experience_similarity']
            fit_items.append(Paragraph(f"• <b>Years of Experience Check:</b> {exp_m.get('explanation')}", bullet_style))
        if 'education_similarity' in match_results:
            edu_m = match_results['education_similarity']
            fit_items.append(Paragraph(f"• <b>Academic Qualification Check:</b> {edu_m.get('explanation')}", bullet_style))
        if 'tech_stack_similarity' in match_results:
            tech_m = match_results['tech_stack_similarity']
            fit_items.append(Paragraph(f"• <b>Tech Stack Compatibility Check:</b> {tech_m.get('explanation')}", bullet_style))
            
        if fit_items:
            story.append(KeepTogether(fit_items))
        else:
            # Fallback simple bullet list
            story.append(Paragraph("• Cosine similarity calculated on TF-IDF features shows structured match suitability.", bullet_style))
            
        story.append(Spacer(1, 15))
        
        # AI Roadmap & Recommendations
        story.append(Paragraph("Actionable Career Roadmap & Upskilling", h1_style))
        
        recs_list = []
        
        # Projects Suggestion
        recs_list.append(Paragraph("<b>Recommended Hands-on Projects:</b>", h2_style))
        for proj in feedback_results.get('project_suggestions', []):
            recs_list.append(Paragraph(f"• {proj}", bullet_style))
            
        recs_list.append(Spacer(1, 5))
        
        # Certifications Suggestion
        recs_list.append(Paragraph("<b>Recommended Industry Certifications:</b>", h2_style))
        for cert in feedback_results.get('certification_suggestions', []):
            recs_list.append(Paragraph(f"• {cert}", bullet_style))
            
        # Roadmap Steps
        recs_list.append(Spacer(1, 5))
        recs_list.append(Paragraph("<b>Step-by-Step Learning Timeline:</b>", h2_style))
        for idx, step in enumerate(feedback_results.get('learning_roadmap', []), 1):
            recs_list.append(Paragraph(f"<b>Step {idx}:</b> {step}", bullet_style))
            
        story.append(KeepTogether(recs_list))
        
        # Build PDF using NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        return output_path
