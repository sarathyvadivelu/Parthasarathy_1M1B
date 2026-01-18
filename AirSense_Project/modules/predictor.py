import random
from datetime import datetime, timedelta

class EnhancedAQIPredictionEngine:
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher
    
    def predict_next_hours(self, current_aqi, hours=24):
        predictions = []
        current_time = datetime.now()
        start_hour = current_time.replace(minute=0, second=0) + timedelta(hours=1)
        
        for i in range(hours):
            future_time = start_hour + timedelta(hours=i)
            hour_key = future_time.strftime('%Y-%m-%d-%H')
            random.seed(hour_key) # Stability Fix
            
            hour_of_day = future_time.hour
            time_factor = 1.15 if (8<=hour_of_day<=10 or 17<=hour_of_day<=20) else (0.85 if 1<=hour_of_day<=5 else 1.0)
            
            predicted_aqi = max(50, min(300, int(current_aqi * time_factor * random.uniform(0.9, 1.1))))
            category = self.categorize_aqi(predicted_aqi)
            
            predictions.append({
                'time': future_time.strftime('%I:%M %p'),
                'aqi': predicted_aqi,
                'category': category['category'],
                'color': category['color']
            })
        random.seed(None)
        return predictions 
    
    def predict_week(self, current_aqi):
        predictions = []
        for day in range(1, 8):
            date = datetime.now() + timedelta(days=day)
            random.seed(date.strftime('%Y-%m-%d')) # Stability Fix
            
            predicted_aqi = max(50, min(300, int(current_aqi * random.uniform(0.85, 1.15))))
            category = self.categorize_aqi(predicted_aqi)
            
            predictions.append({
                'day': date.strftime('%A'),
                'date': date.strftime('%b %d'),
                'aqi': predicted_aqi,
                'category': category['category'],
                'color': category['color']
            })
        random.seed(None)
        return predictions    

    @staticmethod
    def categorize_aqi(aqi):
        if aqi <= 50: return {'category': 'Good', 'color': '#00E400'}
        elif aqi <= 100: return {'category': 'Satisfactory', 'color': '#4facfe'}
        elif aqi <= 200: return {'category': 'Moderate', 'color': '#43e97b'}
        elif aqi <= 300: return {'category': 'Poor', 'color': '#ffc107'}
        elif aqi <= 400: return {'category': 'Very Poor', 'color': '#f5576c'}
        else: return {'category': 'Severe', 'color': '#8B0000'}
