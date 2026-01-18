import requests
import random
from datetime import datetime
from functools import lru_cache
import pandas as pd
import config  # Import your keys

class RealDataFetcher:
    def __init__(self):
        self.base_url = "https://api.waqi.info"
        self.api_key = config.WAQI_API_KEY

    def calculate_concentration(self, aqi_score, pollutant='pm25'):
        try:
            score = float(aqi_score)
            if pollutant == 'pm25':
                if score <= 50: return round(score * (12.0 / 50.0), 1)
                elif score <= 100: return round(12.1 + (score - 51) * (23.3 / 49.0), 1)
                elif score <= 150: return round(35.5 + (score - 101) * (19.9 / 49.0), 1)
                elif score <= 200: return round(55.5 + (score - 151) * (94.9 / 49.0), 1)
                else: return round(score, 1)
            elif pollutant == 'pm10':
                if score <= 50: return round(score * (54.0 / 50.0), 1)
                elif score <= 100: return round(55 + (score - 51) * (99.0 / 49.0), 1)
                else: return round(score, 1)
            return score
        except:
            return aqi_score

    def get_station_uid(self, keyword):
        try:
            url = f"{self.base_url}/search/?token={self.api_key}&keyword={keyword}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                results = response.json()
                if results['status'] == 'ok' and results['data']:
                    return results['data'][0]['uid']
        except Exception as e:
            print(f"Search failed: {e}")
        return None

    @lru_cache(maxsize=20) 
    def fetch_waqi_data(self, city="chennai"):
        if not self.api_key or "PASTE" in self.api_key:
            return self.get_simulated_data()
        
        try:
            # Try Direct Fetch
            url = f"{self.base_url}/feed/{city}/?token={self.api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            # Try Smart Search if failed
            if data['status'] != 'ok':
                station_uid = self.get_station_uid(city)
                if station_uid:
                    url = f"{self.base_url}/feed/@{station_uid}/?token={self.api_key}"
                    response = requests.get(url, timeout=10)
                    data = response.json()

            if data['status'] == 'ok':
                aqi = data['data']['aqi']
                if not isinstance(aqi, (int, float)): aqi = 0 

                iaqi = data['data'].get('iaqi', {})
                city_name = data['data'].get('city', {}).get('name', city)
                
                return {
                    'aqi': int(aqi),
                    'pm25': self.calculate_concentration(iaqi.get('pm25', {}).get('v', 0), 'pm25'),
                    'pm10': self.calculate_concentration(iaqi.get('pm10', {}).get('v', 0), 'pm10'),
                    'temp': iaqi.get('t', {}).get('v', "N/A"),
                    'location': city_name, 
                    'source': 'WAQI (Real)',
                    'timestamp': datetime.now()
                }
            return self.get_simulated_data()

        except Exception as e:
            print(f"Error: {e}")
            return self.get_simulated_data()

    def get_current_aqi(self, city='chennai'):
        data = self.fetch_waqi_data(city)
        return data if data else self.get_simulated_data()
    
    def get_simulated_data(self):
        hour = datetime.now().hour
        base = 165 if (8 <= hour <= 10 or 18 <= hour <= 20) else (95 if (23 <= hour or hour <= 5) else 130)
        aqi = max(50, min(300, int(base + random.gauss(0, 15))))
        pm25 = aqi * 0.6 if aqi <= 50 else (30 + (aqi - 50) * 0.6)
        return {'aqi': aqi, 'pm25': round(pm25, 1), 'pm10': round(pm25 * 1.8, 1), 'temp': 30.5, 'source': 'Simulated', 'timestamp': datetime.now()}

    def get_historical_data(self, days=7):
        dates = pd.date_range(end=datetime.now(), periods=days*24, freq='h')
        data = []
        for date in dates:
            aqi = 120 + random.gauss(0, 15)
            data.append({'timestamp': date, 'aqi': int(aqi)})
        return pd.DataFrame(data)
