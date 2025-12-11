from flask import Flask, render_template, request, send_file, jsonify, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import base64

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up old files in uploads directory"""
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                file_age = datetime.now().timestamp() - os.path.getmtime(file_path)
                if file_age > 3600:  # Delete files older than 1 hour
                    os.remove(file_path)
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.route('/')
def index():
    cleanup_old_files()
    return render_template('index.html')

@app.route('/barcode-generator')
def barcode_generator():
    return render_template('barcode_generator.html')

@app.route('/document-generator')
def document_generator():
    return render_template('document_generator.html')

@app.route('/generate_barcode', methods=['POST'])
def generate_barcode():
    try:
        product_name = request.form.get('product_name', '')
        price = request.form.get('price', '')
        barcode_number = request.form.get('barcode_number', '')
        date = request.form.get('date', '')
        description = request.form.get('description', '')
        
        if not all([product_name, price, barcode_number, date]):
            return jsonify({'error': 'Lütfen tüm zorunlu alanları doldurun'}), 400
        
        # Generate barcode image
        barcode_class = barcode.get_barcode_class('code128')
        barcode_instance = barcode_class(barcode_number, writer=ImageWriter())
        
        # Create barcode image
        barcode_buffer = io.BytesIO()
        barcode_instance.write(barcode_buffer)
        barcode_buffer.seek(0)
        
        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Logo handling
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename != '' and allowed_file(logo_file.filename):
                logo_filename = secure_filename(logo_file.filename)
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], f"logo_{uuid.uuid4()}_{logo_filename}")
                logo_file.save(logo_path)
                
                # Add logo to PDF
                img = RLImage(logo_path, width=2*inch, height=1*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.5*inch))
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("ÜRÜN ETİKETİ", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Product Name
        product_style = ParagraphStyle(
            'ProductName',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            alignment=TA_CENTER,
            bold=True
        )
        elements.append(Paragraph(f"<b>{product_name}</b>", product_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Barcode Image
        barcode_img = RLImage(barcode_buffer, width=4*inch, height=1.5*inch)
        elements.append(barcode_img)
        elements.append(Spacer(1, 0.1*inch))
        
        # Barcode Number
        barcode_text_style = ParagraphStyle(
            'BarcodeText',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            fontName='Courier'
        )
        elements.append(Paragraph(barcode_number, barcode_text_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Price
        price_style = ParagraphStyle(
            'Price',
            parent=styles['Normal'],
            fontSize=20,
            textColor=colors.HexColor('#e74c3c'),
            alignment=TA_CENTER,
            bold=True
        )
        elements.append(Paragraph(f"<b>Fiyat: {price} TL</b>", price_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Date and Description
        info_data = [
            ["Tarih:", date],
        ]
        
        if description:
            info_data.append(["Açıklama:", description])
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(info_table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        # Create unique filename
        filename = f"etiket_{uuid.uuid4()}.pdf"
        
        return send_file(
            io.BytesIO(pdf_buffer.read()),
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Bir hata oluştu: {str(e)}'}), 500

@app.route('/generate_document', methods=['POST'])
def generate_document():
    try:
        company_name = request.form.get('company_name', '')
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        date = request.form.get('date', '')
        authorized_name = request.form.get('authorized_name', '')
        
        if not all([company_name, title, description, date, authorized_name]):
            return jsonify({'error': 'Lütfen tüm alanları doldurun'}), 400
        
        # Create PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Logo handling
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename != '' and allowed_file(logo_file.filename):
                logo_filename = secure_filename(logo_file.filename)
                logo_path = os.path.join(app.config['UPLOAD_FOLDER'], f"logo_{uuid.uuid4()}_{logo_filename}")
                logo_file.save(logo_path)
                
                # Add logo to PDF (top left)
                img = RLImage(logo_path, width=2*inch, height=1*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.2*inch))
        
        # Company Name
        company_style = ParagraphStyle(
            'CompanyName',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(company_name, company_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Title
        title_style = ParagraphStyle(
            'DocumentTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_RIGHT,
            spaceAfter=20
        )
        elements.append(Paragraph(f"Tarih: {date}", date_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Description
        description_style = ParagraphStyle(
            'Description',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            alignment=TA_LEFT,
            leading=14
        )
        
        # Split description by newlines and create paragraphs
        description_lines = description.split('\n')
        for line in description_lines:
            if line.strip():
                elements.append(Paragraph(line, description_style))
                elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Signature handling
        signature_elements = []
        if 'signature' in request.files:
            signature_file = request.files['signature']
            if signature_file and signature_file.filename != '' and allowed_file(signature_file.filename):
                signature_filename = secure_filename(signature_file.filename)
                signature_path = os.path.join(app.config['UPLOAD_FOLDER'], f"signature_{uuid.uuid4()}_{signature_filename}")
                signature_file.save(signature_path)
                
                # Add signature image
                img = RLImage(signature_path, width=2*inch, height=1*inch)
                signature_elements.append(img)
                signature_elements.append(Spacer(1, 0.1*inch))
        
        # Authorized Name and Title
        authorized_style = ParagraphStyle(
            'Authorized',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_RIGHT
        )
        signature_elements.append(Paragraph(f"Yetkili: {authorized_name}", authorized_style))
        signature_elements.append(Paragraph("İmza", authorized_style))
        
        # Create signature table (right aligned)
        signature_table = Table([[signature_elements]], colWidths=[6*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(signature_table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        # Create unique filename
        filename = f"belge_{uuid.uuid4()}.pdf"
        
        return send_file(
            io.BytesIO(pdf_buffer.read()),
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Bir hata oluştu: {str(e)}'}), 500

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    return jsonify({'error': 'Dosya boyutu 5MB limitini aşıyor'}), 413

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)