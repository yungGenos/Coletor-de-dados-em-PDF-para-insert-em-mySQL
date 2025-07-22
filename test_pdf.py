#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar extração de PDF
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bibliotecas de PDF
try:
    import PyPDF2
    logger.info("✅ PyPDF2 disponível")
except ImportError:
    logger.error("❌ PyPDF2 não encontrado")

try:
    import pdfplumber
    logger.info("✅ pdfplumber disponível")
except ImportError:
    logger.error("❌ pdfplumber não encontrado")

try:
    import fitz  # PyMuPDF
    logger.info("✅ PyMuPDF disponível")
except ImportError:
    logger.error("❌ PyMuPDF não encontrado")

def test_pdf_extraction(pdf_path):
    """Testa extração de PDF com diferentes métodos"""
    
    if not os.path.exists(pdf_path):
        logger.error(f"Arquivo não encontrado: {pdf_path}")
        return
    
    logger.info(f"Testando PDF: {pdf_path}")
    logger.info(f"Tamanho do arquivo: {os.path.getsize(pdf_path)} bytes")
    
    # Teste 1: PyMuPDF
    try:
        import fitz
        logger.info("\n=== TESTE PYMUPDF ===")
        doc = fitz.open(pdf_path)
        logger.info(f"Número de páginas: {len(doc)}")
        
        for page_num in range(min(3, len(doc))):  # Testa apenas as 3 primeiras páginas
            page = doc.load_page(page_num)
            text = page.get_text()
            logger.info(f"Página {page_num + 1}: {len(text)} caracteres")
            if text.strip():
                logger.info(f"Amostra: {text[:200]}...")
            else:
                logger.warning(f"Página {page_num + 1} sem texto")
        
        doc.close()
        
    except Exception as e:
        logger.error(f"PyMuPDF falhou: {e}")
    
    # Teste 2: pdfplumber
    try:
        import pdfplumber
        logger.info("\n=== TESTE PDFPLUMBER ===")
        
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Número de páginas: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages[:3], 1):  # Testa apenas as 3 primeiras páginas
                text = page.extract_text()
                logger.info(f"Página {page_num}: {len(text) if text else 0} caracteres")
                
                if text and text.strip():
                    logger.info(f"Amostra: {text[:200]}...")
                else:
                    logger.warning(f"Página {page_num} sem texto")
                
                # Verifica tabelas
                tables = page.extract_tables()
                if tables:
                    logger.info(f"Página {page_num}: {len(tables)} tabela(s) encontrada(s)")
                    
    except Exception as e:
        logger.error(f"pdfplumber falhou: {e}")
    
    # Teste 3: PyPDF2
    try:
        logger.info("\n=== TESTE PYPDF2 ===")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            logger.info(f"Número de páginas: {len(pdf_reader.pages)}")
            
            for page_num, page in enumerate(pdf_reader.pages[:3], 1):  # Testa apenas as 3 primeiras páginas
                text = page.extract_text()
                logger.info(f"Página {page_num}: {len(text)} caracteres")
                
                if text.strip():
                    logger.info(f"Amostra: {text[:200]}...")
                else:
                    logger.warning(f"Página {page_num} sem texto")
                    
    except Exception as e:
        logger.error(f"PyPDF2 falhou: {e}")

if __name__ == "__main__":
    # Testa o PDF específico do usuário
    pdf_path = r"c:\Users\thiago.oliveira\Downloads\SP - SAO PAULO - SETE PRAIAS - 20582 - 10803604 - 01_04_2025.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    test_pdf_extraction(pdf_path)
