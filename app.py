from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
import logging
from datetime import datetime
import PyPDF2
from werkzeug.utils import secure_filename
import uuid
import re

# Bibliotecas adicionais para melhor extração de PDF
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui_mude_para_producao')

# Configuração de logging melhorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sistema_logs.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
DATA_FILE = 'dados_coletados.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um arquivo PDF usando múltiplas bibliotecas para melhor compatibilidade"""
    extracted_text = ""
    extraction_methods = []
    
    # Método 1: PyMuPDF (melhor para PDFs complexos e escaneados)
    if PYMUPDF_AVAILABLE:
        try:
            logger.info("Tentando extração com PyMuPDF")
            doc = fitz.open(pdf_path)
            text_pymupdf = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    text_pymupdf += f"\n--- Página {page_num + 1} (PyMuPDF) ---\n{page_text}\n"
            
            doc.close()
            
            if text_pymupdf.strip():
                extracted_text = text_pymupdf
                extraction_methods.append("PyMuPDF")
                logger.info(f"PyMuPDF extraiu {len(text_pymupdf)} caracteres")
            
        except Exception as e:
            logger.warning(f"PyMuPDF falhou: {str(e)}")
    
    # Método 2: pdfplumber (excelente para tabelas e layout complexo)
    if PDFPLUMBER_AVAILABLE and not extracted_text:
        try:
            logger.info("Tentando extração com pdfplumber")
            with pdfplumber.open(pdf_path) as pdf:
                text_plumber = ""
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_plumber += f"\n--- Página {page_num} (pdfplumber) ---\n{page_text}\n"
                    
                    # Também tenta extrair tabelas se houver
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables, 1):
                            text_plumber += f"\n--- Tabela {table_num} da Página {page_num} ---\n"
                            for row in table:
                                if row:
                                    text_plumber += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
                
                if text_plumber.strip():
                    extracted_text = text_plumber
                    extraction_methods.append("pdfplumber")
                    logger.info(f"pdfplumber extraiu {len(text_plumber)} caracteres")
                    
        except Exception as e:
            logger.warning(f"pdfplumber falhou: {str(e)}")
    
    # Método 3: PyPDF2 (fallback padrão)
    if not extracted_text:
        try:
            logger.info("Tentando extração com PyPDF2")
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_pypdf2 = ""
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Processando PDF com {total_pages} páginas usando PyPDF2")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_pypdf2 += f"\n--- Página {page_num} (PyPDF2) ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"Erro ao extrair texto da página {page_num} com PyPDF2: {str(e)}")
                        text_pypdf2 += f"\n--- Página {page_num} ---\n[Erro ao extrair texto desta página]\n"
                
                if text_pypdf2.strip():
                    extracted_text = text_pypdf2
                    extraction_methods.append("PyPDF2")
                    logger.info(f"PyPDF2 extraiu {len(text_pypdf2)} caracteres")
                    
        except Exception as e:
            logger.error(f"PyPDF2 também falhou: {str(e)}")
    
    # Método 4: Tentativa de OCR básico com PyMuPDF se texto não foi extraído
    if PYMUPDF_AVAILABLE and not extracted_text:
        try:
            logger.info("Tentando extração de imagem/OCR com PyMuPDF")
            doc = fitz.open(pdf_path)
            ocr_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Tenta extrair texto de imagens na página
                image_list = page.get_images()
                if image_list:
                    ocr_text += f"\n--- Página {page_num + 1} (Imagens detectadas) ---\n"
                    ocr_text += f"[PDF contém {len(image_list)} imagem(s) - texto pode estar em formato de imagem]\n"
                
                # Extrai qualquer texto visível mesmo que seja pouco
                all_text = page.get_text("text")
                if all_text.strip():
                    ocr_text += all_text + "\n"
            
            doc.close()
            
            if ocr_text.strip():
                extracted_text = ocr_text
                extraction_methods.append("PyMuPDF-OCR")
                logger.info(f"PyMuPDF-OCR extraiu {len(ocr_text)} caracteres")
                
        except Exception as e:
            logger.warning(f"Extração de imagem falhou: {str(e)}")
    
    # Resultado final
    if extracted_text:
        # Adiciona informações sobre o método usado
        method_info = f"[Métodos de extração utilizados: {', '.join(extraction_methods)}]\n\n"
        final_text = method_info + extracted_text.strip()
        
        logger.info(f"Extração concluída com sucesso usando: {', '.join(extraction_methods)}")
        logger.info(f"Total de caracteres extraídos: {len(final_text)}")
        
        return final_text
    else:
        logger.error("Todas as tentativas de extração de texto falharam")
        return "[PDF processado mas não foi possível extrair texto legível com nenhum método disponível]"

def save_data_to_log(data):
    """Salva os dados em log estruturado com backup automático"""
    try:
        timestamp = datetime.now()
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "id": str(uuid.uuid4()),
            "data": data,
            "created_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0"
        }
        
        # Salva em arquivo JSON estruturado
        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")
        
        # Cria backup diário se não existir
        backup_filename = f"backup_{timestamp.strftime('%Y%m%d')}.json"
        if not os.path.exists(backup_filename):
            try:
                with open(backup_filename, 'w', encoding='utf-8') as backup_f:
                    backup_f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")
                logger.info(f"Backup diário criado: {backup_filename}")
            except Exception as e:
                logger.warning(f"Erro ao criar backup: {str(e)}")
        
        # Log para acompanhamento
        logger.info(f"Dados salvos com ID: {log_entry['id']}")
        return log_entry['id']
        
    except Exception as e:
        logger.error(f"Erro ao salvar dados: {str(e)}")
        return None

def validate_form_data(data):
    """Valida se um arquivo PDF foi enviado"""
    errors = []
    
    # Apenas verifica se o arquivo PDF está presente
    if not data.get('pdf_file_uploaded'):
        errors.append("Arquivo PDF é obrigatório")
    
    return errors

def sanitize_filename(filename):
    """Sanitiza o nome do arquivo para segurança"""
    # Remove caracteres especiais e mantém apenas letras, números, pontos e hífens
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return name[:100]  # Limita o tamanho

def validate_pdf_file(file):
    """Valida se o arquivo PDF é válido"""
    try:
        # Tenta ler o PDF para verificar se está válido
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        if num_pages == 0:
            return False, "PDF não contém páginas"
        
        if num_pages > 100:
            return False, "PDF muito grande (máximo 100 páginas)"
            
        return True, None
    except Exception as e:
        logger.error(f"Erro ao validar PDF: {str(e)}")
        return False, "Arquivo PDF inválido ou corrompido"

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Processa o upload de arquivo PDF e extrai dados automaticamente"""
    try:
        logger.info("Iniciando processamento de upload de PDF")
        logger.info(f"Arquivos recebidos: {list(request.files.keys())}")
        
        # Verifica se arquivo PDF foi enviado
        if 'pdf_file' not in request.files:
            return jsonify({'success': False, 'errors': ['Nenhum arquivo PDF foi enviado']}), 400
        
        file = request.files['pdf_file']
        
        if not file or file.filename == '':
            return jsonify({'success': False, 'errors': ['Arquivo PDF é obrigatório']}), 400
        
        logger.info(f"Arquivo PDF encontrado: {file.filename}, tamanho: {len(file.read())} bytes")
        file.seek(0)  # Reset após ler o tamanho
        
        # Validação do tipo de arquivo
        if not allowed_file(file.filename):
            error_msg = f'Tipo de arquivo não permitido: {file.filename}. Use apenas PDF.'
            logger.error(error_msg)
            return jsonify({'success': False, 'errors': [error_msg]}), 400
        
        # Validação do PDF
        file.seek(0)  # Reset file pointer
        is_valid, validation_error = validate_pdf_file(file)
        if not is_valid:
            error_msg = f'PDF inválido: {validation_error}'
            logger.error(error_msg)
            return jsonify({'success': False, 'errors': [error_msg]}), 400
        
        # Salvamento do arquivo
        file.seek(0)  # Reset file pointer again
        filename = sanitize_filename(secure_filename(file.filename))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(filepath)
        logger.info(f"Arquivo salvo: {filepath}")
        
        # Extração de texto do PDF
        pdf_text = extract_text_from_pdf(filepath)
        if pdf_text is None:
            error_msg = 'Erro ao processar PDF - não foi possível extrair texto'
            logger.error(error_msg)
            return jsonify({'success': False, 'errors': [error_msg]}), 400
        
        # Informações do arquivo
        arquivo_info = {
            'nome_original': file.filename,
            'nome_salvo': filename,
            'tamanho': os.path.getsize(filepath),
            'caminho': filepath
        }
        
        # Estrutura final dos dados (apenas dados extraídos do PDF)
        processed_data = {
            'pdf_content': pdf_text,
            'arquivo': arquivo_info,
            'status': 'processado',
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string
        }
        
        logger.info(f"Dados processados: {len(str(processed_data))} caracteres")
        
        # Salva os dados
        record_id = save_data_to_log(processed_data)
        
        if record_id:
            logger.info(f"Processamento concluído com sucesso. ID: {record_id}")
            return jsonify({
                'success': True, 
                'message': 'Dados extraídos e salvos com sucesso!',
                'record_id': record_id,
                'arquivo': arquivo_info['nome_original'],
                'caracteres_extraidos': len(pdf_text)
            })
        else:
            logger.error("Erro ao salvar dados processados")
            return jsonify({'success': False, 'errors': ['Erro ao salvar dados']}), 500
            
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'errors': [f'Erro interno do servidor: {str(e)}']}), 500

@app.route('/visualizar')
def visualizar():
    """Página para visualizar dados coletados com paginação e filtros"""
    try:
        dados = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            dados.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.warning(f"Linha JSON inválida ignorada: {e}")
        
        # Ordenar por timestamp (mais recente primeiro)
        dados.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        logger.info(f"Carregados {len(dados)} registros para visualização")
        return render_template('visualizar.html', dados=dados)
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        flash('Erro ao carregar dados', 'error')
        return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    """API para estatísticas do sistema"""
    try:
        total_registros = 0
        total_pdfs = 0
        
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            total_registros += 1
                            if data.get('data', {}).get('pdf_content'):
                                total_pdfs += 1
                        except json.JSONDecodeError:
                            continue
        
        return jsonify({
            'total_registros': total_registros,
            'total_pdfs': total_pdfs,
            'uptime': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

# Tratamento de erros globais
@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'errors': ['Arquivo muito grande. Máximo 16MB']}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Erro interno 500: {str(e)}")
    return jsonify({'success': False, 'errors': ['Erro interno do servidor']}), 500

if __name__ == '__main__':
    logger.info("Iniciando Sistema de Coleta de Dados")
    logger.info(f"Pasta de uploads: {UPLOAD_FOLDER}")
    logger.info(f"Arquivo de dados: {DATA_FILE}")
    logger.info("Sistema disponível em: http://localhost:5000")
    
    # Modo debug apenas em desenvolvimento
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
