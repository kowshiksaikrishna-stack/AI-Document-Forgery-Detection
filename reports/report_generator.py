# reports/report_generator.py

from datetime import datetime

def generate_report(result):

    return f"""
AI DOCUMENT VERIFICATION REPORT
================================

Document Type : {result['document_type']}
OCR Status    : {result['ocr_status']}
Face Status   : {result['face_status']}
Forgery Score : {result['forgery_score']}
Risk Score    : {result['risk_score']}
Result        : {result['result']}

Document Hash:
{result['document_hash']}

Blockchain Transaction:
{result['blockchain_tx']}

Generated:
{datetime.now()}
"""