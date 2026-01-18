from flask import Flask, render_template, request, jsonify
from datetime import datetime

# IMPORT OUR CUSTOM MODULES
from modules.data_fetcher import RealDataFetcher
from modules.predictor import EnhancedAQIPredictionEngine
from modules.ai_advisor import RealAIAdvisor

app = Flask(__name__)

# Initialize Components
data_fetcher = RealDataFetcher()
predictor = EnhancedAQIPredictionEngine(data_fetcher)
advisor = RealAIAdvisor()

@app.route('/')
def index():
    return render_template('final.html') # Ensure your HTML is named 'final.html'

@app.route('/widget')
def widget():
    return render_template('widget.html')

@app.route('/api/current')
def get_current_aqi_route():
    city = request.args.get('city', 'chennai')
    
    current_data = data_fetcher.get_current_aqi(city)
    current_aqi = current_data['aqi']
    
    return jsonify({
        'current': {
            'aqi': current_aqi,
            'pm25': current_data.get('pm25', 0),
            'pm10': current_data.get('pm10', 0),
            'temp': current_data.get('temp', '--'),
            'category': predictor.categorize_aqi(current_aqi)['category'],
            'color': predictor.categorize_aqi(current_aqi)['color'],
            'location': current_data.get('location', city.title()),
            'timestamp': datetime.now().strftime('%I:%M %p'),
            'source': current_data.get('source', 'Unknown')
        },
        'hourly': predictor.predict_next_hours(current_aqi),
        'weekly': predictor.predict_week(current_aqi)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question', '')
    city = data.get('city', 'chennai')
    
    current_data = data_fetcher.get_current_aqi(city)
    current_aqi = current_data['aqi']
    current_temp = current_data.get('temp', 'unknown')
    
    weekly_forecast = predictor.predict_week(current_aqi)
    hourly_forecast = predictor.predict_next_hours(current_aqi)
    
    response = advisor.get_ai_response(question, current_aqi, current_temp, weekly_forecast, hourly_forecast)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    print("=" * 50)
    print("🌍 AirSense AI - MODULAR VERSION LAUNCHED")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
