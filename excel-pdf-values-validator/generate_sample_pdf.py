#!/usr/bin/env python3
"""
Generate a sample PDF with generic parameter data similar to the Excel structure
but without any proprietary information.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import pandas as pd
from datetime import datetime

def create_sample_data():
    """Create generic sample data similar to the Excel structure"""
    sample_data = [
        ['Parameter', 'Value', 'Unit'],
        ['Volume', '25.500', 'm³'],
        ['Mass', '10500.250', 'kg'],
        ['Density at 15°C', '412.000', 'kg/m³'],
        ['Temperature', '25.0', '°C'],
        ['Pressure', '101.325', 'kPa'],
        ['Flow Rate', '150.5', 'L/min'],
        ['Viscosity', '2.8', 'cP'],
        ['pH Level', '7.2', '-'],
        ['Conductivity', '1250.0', 'µS/cm'],
        ['Total Dissolved Solids', '625.0', 'mg/L'],
        ['Turbidity', '0.5', 'NTU'],
        ['Chemical Oxygen Demand', '45.2', 'mg/L'],
        ['Biochemical Oxygen Demand', '15.8', 'mg/L'],
        ['Suspended Solids', '12.3', 'mg/L'],
        ['Nitrogen (Total)', '8.9', 'mg/L'],
        ['Phosphorus (Total)', '1.2', 'mg/L'],
        ['Chloride', '125.0', 'mg/L'],
        ['Sulfate', '85.4', 'mg/L'],
        ['Alkalinity', '180.5', 'mg CaCO₃/L'],
        ['Hardness', '200.3', 'mg CaCO₃/L'],
    ]
    return sample_data

def generate_sample_pdf(filename='files/sample_generic_parameters.pdf'):
    """Generate a PDF with sample parameter data"""
    
    # Create the PDF document
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle',
                                parent=styles['Heading1'],
                                fontSize=16,
                                spaceAfter=30,
                                alignment=1)  # Center alignment
    
    # Add title
    title = Paragraph("Generic Parameters Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Add timestamp
    timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                         styles['Normal'])
    elements.append(timestamp)
    elements.append(Spacer(1, 20))
    
    # Create sample data
    data = create_sample_data()
    
    # Create table
    table = Table(data, colWidths=[3*inch, 1.5*inch, 1*inch])
    
    # Style the table
    table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Data rows styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Alternate row colors
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('BACKGROUND', (0, 2), (-1, -1), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), colors.beige),
        ('BACKGROUND', (0, 6), (-1, 6), colors.beige),
        ('BACKGROUND', (0, 8), (-1, 8), colors.beige),
        ('BACKGROUND', (0, 10), (-1, 10), colors.beige),
        ('BACKGROUND', (0, 12), (-1, 12), colors.beige),
        ('BACKGROUND', (0, 14), (-1, 14), colors.beige),
        ('BACKGROUND', (0, 16), (-1, 16), colors.beige),
        ('BACKGROUND', (0, 18), (-1, 18), colors.beige),
        ('BACKGROUND', (0, 20), (-1, 20), colors.beige),
        
        # Padding
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Add footer note
    footer_note = Paragraph(
        "<i>Note: This is a sample PDF with generic parameter data for testing purposes only. "
        "All values are fictional and do not represent any real measurements or proprietary information.</i>",
        styles['Italic']
    )
    elements.append(footer_note)
    
    # Build PDF
    doc.build(elements)
    print(f"Sample PDF generated: {filename}")

if __name__ == "__main__":
    import os
    
    # Make sure files directory exists
    os.makedirs('files', exist_ok=True)
    
    # Generate the sample PDF
    generate_sample_pdf()
