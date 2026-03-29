# 🌐 MissFlora AI Customer Assistant - Web API
# Flask REST API - missflora.com.tr entegrasyonu için

from flask import Flask, request, jsonify
from flask_cors import CORS
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import torch
import logging
from datetime import datetime
import os

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # CORS için (frontend erişimi)

# ============================
# MODEL YÜKLEME
# ============================

MODEL_PATH = "./missflora-qwen-final-YYYYMMDD_HHMMSS"  # EĞİTİM SONRASI KLASÖR YOLUNU BURAYA YAZIN

logger.info("🔄 Model yükleniyor...")

try:
    # Model yükle
    model = AutoPeftModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True
    )

    # Tokenizer yükle
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

    model.eval()  # Evaluation mode

    logger.info("✅ Model başarıyla yüklendi!")
    logger.info(f"   → Model: {MODEL_PATH}")
    logger.info(f"   → Device: {next(model.parameters()).device}")

except Exception as e:
    logger.error(f"❌ Model yüklenemedi: {str(e)}")
    exit(1)

# ============================
# CHAT FONKSIYONU
# ============================

def chat_with_missflora(user_message, max_tokens=256, temperature=0.7):
    """
    MissFlora AI ile sohbet et

    Args:
        user_message (str): Kullanıcı mesajı
        max_tokens (int): Maksimum token sayısı
        temperature (float): Yaratıcılık (0.0-1.0)

    Returns:
        str: AI yanıtı
    """
    try:
        # Chat template oluştur
        messages = [
            {
                "role": "system",
                "content": "Sen MissFlora müşteri hizmetleri asistanısın. MissFlora ev bakım ve koku ürünleri hakkında Türkçe yardım sağlıyorsun. Nazik, bilgili ve yardımseversin."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Tokenize
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        # Decode
        response = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        return response.strip()

    except Exception as e:
        logger.error(f"❌ Chat hatası: {str(e)}")
        return "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."

# ============================
# API ENDPOINTS
# ============================

@app.route('/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    return jsonify({
        "status": "healthy",
        "model": MODEL_PATH,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint

    Örnek istek:
    POST /chat
    {
        "message": "MissFlora Nem Alıcı ne kadar dayanır?",
        "max_tokens": 256,
        "temperature": 0.7
    }
    """
    try:
        # Request verisini al
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                "error": "Message alanı gerekli"
            }), 400

        user_message = data['message']
        max_tokens = data.get('max_tokens', 256)
        temperature = data.get('temperature', 0.7)

        logger.info(f"📩 Gelen mesaj: {user_message}")

        # AI yanıtı al
        response = chat_with_missflora(
            user_message=user_message,
            max_tokens=max_tokens,
            temperature=temperature
        )

        logger.info(f"💬 AI yanıtı: {response}")

        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Chat endpoint hatası: {str(e)}")
        return jsonify({
            "error": "Bir hata oluştu"
        }), 500

@app.route('/batch-chat', methods=['POST'])
def batch_chat():
    """
    Toplu chat endpoint (birden fazla soru)

    Örnek istek:
    POST /batch-chat
    {
        "messages": [
            "MissFlora Nem Alıcı nedir?",
            "WC Blok nasıl kullanılır?",
            "İletişim bilgileri"
        ]
    }
    """
    try:
        data = request.get_json()

        if not data or 'messages' not in data:
            return jsonify({
                "error": "Messages alanı gerekli"
            }), 400

        messages = data['messages']
        max_tokens = data.get('max_tokens', 256)
        temperature = data.get('temperature', 0.7)

        responses = []
        for msg in messages:
            response = chat_with_missflora(
                user_message=msg,
                max_tokens=max_tokens,
                temperature=temperature
            )
            responses.append({
                "question": msg,
                "answer": response
            })

        return jsonify({
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Batch chat hatası: {str(e)}")
        return jsonify({
            "error": "Bir hata oluştu"
        }), 500

# ============================
# ÇALIŞTIR
# ============================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("🚀 MissFlora AI Customer Assistant API Başlatılıyor...")
    logger.info("=" * 80)
    logger.info(f"📍 URL: http://localhost:5000")
    logger.info(f"📍 Health: http://localhost:5000/health")
    logger.info(f"📍 Chat: POST http://localhost:5000/chat")
    logger.info("=" * 80)

    # Flask uygulamasını başlat
    app.run(
        host='0.0.0.0',     # Tüm networklerden erişim
        port=5000,          # Port
        debug=False,        # Production'da False
        threaded=True       # Multi-threading
    )
