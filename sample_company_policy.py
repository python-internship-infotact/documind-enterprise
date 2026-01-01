#!/usr/bin/env python3
"""
Create a sample company policy PDF for presentation demo
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import io

def create_sample_policy_pdf():
    """Create a comprehensive sample company policy PDF"""
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("ACME CORPORATION - EMPLOYEE HANDBOOK", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Table of Contents
    toc_title = Paragraph("TABLE OF CONTENTS", styles['Heading1'])
    story.append(toc_title)
    story.append(Spacer(1, 12))
    
    toc_items = [
        "1. Refund Policy ............................ Page 2",
        "2. Customer Support ......................... Page 2", 
        "3. Vacation Policy .......................... Page 3",
        "4. Working Hours ............................ Page 3",
        "5. Expense Reimbursement .................... Page 4",
        "6. IT Security Policy ....................... Page 4"
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Page 1 - Refund Policy
    story.append(Paragraph("1. REFUND POLICY", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    refund_text = """
    ACME Corporation offers a comprehensive 30-day money-back guarantee on all products and services. 
    Our refund policy is designed to ensure customer satisfaction while maintaining fair business practices.
    
    <b>Eligibility Requirements:</b>
    • Refund requests must be submitted within 30 days of purchase
    • Products must be returned in original condition with all packaging
    • Digital services are eligible for refund within 14 days of activation
    • Custom or personalized items are non-refundable unless defective
    
    <b>Refund Process:</b>
    1. Contact our customer support team at support@acme.com or call 1-800-ACME-HELP
    2. Provide your order number and reason for the refund request
    3. Follow the return instructions provided by our support team
    4. Once we receive and inspect the returned item, we will process your refund
    5. Refunds are typically processed within 5-7 business days
    
    <b>Refund Methods:</b>
    • Original payment method (credit card, PayPal, etc.)
    • Store credit (if preferred by customer)
    • Bank transfer for large amounts (over $500)
    
    For questions about our refund policy, please contact our customer support team.
    """
    
    story.append(Paragraph(refund_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Page 2 - Customer Support
    story.append(Paragraph("2. CUSTOMER SUPPORT", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    support_text = """
    ACME Corporation is committed to providing exceptional customer support to all our clients.
    Our dedicated support team is available to assist you with any questions or concerns.
    
    <b>Contact Information:</b>
    • Email: support@acme.com (Response within 24 hours)
    • Phone: 1-800-ACME-HELP (1-800-226-3435)
    • Live Chat: Available on our website 24/7
    • Support Portal: https://support.acme.com
    
    <b>Support Hours:</b>
    • Phone Support: Monday-Friday, 8:00 AM - 8:00 PM EST
    • Email Support: 24/7 (responses within 24 hours)
    • Live Chat: 24/7 automated, live agents 9:00 AM - 6:00 PM EST
    • Emergency Support: Available 24/7 for critical issues
    
    <b>Support Categories:</b>
    • Technical Issues: Product functionality, troubleshooting
    • Billing Questions: Invoices, payments, refunds
    • Account Management: Profile updates, password resets
    • General Inquiries: Product information, company policies
    
    <b>Priority Support:</b>
    Premium customers receive priority support with guaranteed response times:
    • Critical Issues: 2-hour response time
    • High Priority: 4-hour response time
    • Standard Issues: 24-hour response time
    """
    
    story.append(Paragraph(support_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Page 3 - Vacation Policy
    story.append(Paragraph("3. VACATION POLICY", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    vacation_text = """
    ACME Corporation values work-life balance and provides generous vacation benefits to all employees.
    
    <b>Vacation Accrual:</b>
    • New employees: 2 vacation days per month (24 days annually)
    • Employees with 3+ years: 2.5 vacation days per month (30 days annually)
    • Employees with 7+ years: 3 vacation days per month (36 days annually)
    • Senior management: 4 vacation days per month (48 days annually)
    
    <b>Vacation Request Process:</b>
    1. Submit vacation requests at least 2 weeks in advance
    2. Use the employee portal to request time off
    3. Manager approval required for all vacation requests
    4. Blackout periods apply during busy seasons (November-December)
    
    <b>Vacation Policies:</b>
    • Maximum carryover: 5 days to the following year
    • Vacation payout: Available upon termination for unused days
    • Sick leave: Separate from vacation time (10 days annually)
    • Personal days: 3 personal days per year (separate from vacation)
    """
    
    story.append(Paragraph(vacation_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Page 4 - Working Hours
    story.append(Paragraph("4. WORKING HOURS", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    hours_text = """
    ACME Corporation maintains flexible working hours to accommodate diverse employee needs.
    
    <b>Standard Working Hours:</b>
    • Core hours: 10:00 AM - 3:00 PM (all employees must be available)
    • Flexible start time: 7:00 AM - 10:00 AM
    • Flexible end time: 3:00 PM - 7:00 PM
    • Total hours per week: 40 hours
    • Lunch break: 1 hour (flexible timing)
    
    <b>Remote Work Policy:</b>
    • Hybrid model: 3 days in office, 2 days remote
    • Full remote available for certain roles
    • Remote work equipment provided by company
    • Monthly in-person team meetings required
    
    <b>Overtime Policy:</b>
    • Overtime pre-approval required from manager
    • Time-and-a-half pay for hours over 40 per week
    • Compensatory time off available instead of overtime pay
    • Maximum 10 hours overtime per week without special approval
    """
    
    story.append(Paragraph(hours_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def save_sample_pdf():
    """Save the sample PDF to file"""
    pdf_content = create_sample_policy_pdf()
    
    with open("sample_company_policy.pdf", "wb") as f:
        f.write(pdf_content)
    
    print("✅ Sample company policy PDF created: sample_company_policy.pdf")
    print("📄 Contains policies for: refund, support, vacation, working hours")
    print("🎯 Ready for presentation demo!")

if __name__ == "__main__":
    try:
        save_sample_pdf()
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        save_sample_pdf()