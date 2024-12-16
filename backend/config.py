from binance.client import Client
import os
from dotenv import load_dotenv
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API anahtarları
api_key = "2HJKDiBf7MXZ2KpQWlniLxsOzZOscFoFjkjRCTgyeey1vF78VkQqa2h2RAJGXpF9"
api_secret = "Soxv6kp2npt9uKkdfaZmzqYb3hRnN69tsqlzkQ7S9lTPeZVHSqOTot7mBG1ZzxVU"

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