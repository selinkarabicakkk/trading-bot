from binance.client import Client
import urllib3
import certifi
import ssl
import requests

# SSL uyarılarını devre dışı bırak
urllib3.disable_warnings()

# Binance API Key ve Secret
api_key = "m6exoH1EIHknDl7o4x0rtUvKeVKCChi4cjDN1oDtLygLOlJ6GyKdTYMNo3C8cS49"
api_secret = "1zB94LaPOA90w8omvPMed4PxXuS6pp13hj2WnmFWhAIYvBm7eidKxcXwVmPFP2sx"

# Client oluştur
client = Client(
    api_key, 
    api_secret,
    tld='com',
    testnet=False,  # Mainnet kullan
    requests_params={
        'verify': False,  # SSL doğrulamasını devre dışı bırak
        'timeout': 30
    }
)

# Hata ayıklama için bağlantı testi
try:
    client.ping()
    print("Binance bağlantısı başarılı")
except Exception as e:
    print(f"Binance bağlantı hatası: {str(e)}")