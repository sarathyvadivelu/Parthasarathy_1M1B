import requests
import random
import config # Import API Keys

class RealAIAdvisor:
    def __init__(self):
        self.quiz_topics = [
            "Microplastics in Rain", "Electric Vehicles vs Gas", "Indoor Air Pollution", 
            "The Ozone Layer", "PM2.5 vs Human Hair", "Deforestation Effects", 
            "Ocean Acidification", "Recycling Facts", "Carbon Footprint"
        ]
        self._cache = {}

    def get_ai_response(self, user_message, current_aqi, current_temp, weekly_forecast, hourly_forecast):
        daily_topic = random.choice(self.quiz_topics)

        system_rules = (
            "You are AirSense AI. Be EXTREMELY CONCISE (Max 30 words). "
            f"SECRET INSTRUCTION: If asking a quiz, it MUST be about: {daily_topic}. "
            "RULES: "
            "1. IF USER WANTS A QUIZ: Just ask a True/False question. DO NOT give the answer yet. "
            "2. IF USER ANSWERS (True/False): Start with 'Correct!' or 'Incorrect!', then give 1 short fact. "
            "3. FOR TREES: Say 'Plant [AQI/10] trees per person.' Do not explain the math."
            "4. SAFETY CHECK: If AQI < 100, say 'Yes, it is safe.' If AQI > 150, say 'No, avoid outdoors.' "
            "5. SMALL TALK: If user says 'ok'/'thanks', reply 'Stay safe!'"
            "6. NEVER repeat the same question twice in a row."
        )

        weekly_text = "\n".join([f"- {d['day']}: AQI {d['aqi']}" for d in weekly_forecast[:3]]) if weekly_forecast else "No Data"
        
        context = f"""
        DATA:
        • AQI: {current_aqi}
        • Temp: {current_temp}°C
        • Forecast: {weekly_text}
        
        USER QUESTION: "{user_message}"
        """

        if config.GROQ_API_KEY:
            return self.call_groq(system_rules, context)
        return {'recommendation': '⚠️ API Key Missing', 'details': ['Please add Groq Key']}    
        
    def call_groq(self, system_prompt, user_context):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile", # Updated Model
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                "temperature": 0.8,
                "max_tokens": 150
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                text = response.json()['choices'][0]['message']['content']
                return self.parse_response(text)
            return {'recommendation': 'Error', 'details': ['AI Provider Error']}
                
        except Exception as e:
            print(f"Groq connection error: {e}")
            return None

    def parse_response(self, text):
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return {
            'recommendation': lines[0] if lines else text[:50],
            'details': [l.lstrip('-•* ') for l in lines[1:] if l],
            'source': 'AI (Llama 3.3)'
        }
