from binance.client import Client
import os
from dotenv import load_dotenv
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env dosyasından API anahtarlarını yükle
load_dotenv()

# Binance API Key ve Secret
api_key = os.getenv('BINANCE_API_KEY', '')
api_secret = os.getenv('BINANCE_API_SECRET', '')

if not api_key or not api_secret:
    logger.warning("API anahtarları bulunamadı. Test modu kullanılacak.")

# Client oluştur
client = Client(
    api_key, 
    api_secret,
    tld='com',
    testnet=False  # Mainnet kullan
)

# Bağlantı testi
def test_connection():
    try:
        client.ping()
        logger.info("Binance bağlantısı başarılı")
        return True
    except Exception as e:
        logger.error(f"Binance bağlantı hatası: {str(e)}")
        return False

# Başlangıçta bağlantıyı test et
test_connection()