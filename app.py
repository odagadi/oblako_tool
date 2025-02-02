from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import openai
import re
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Check if OpenAI API key is available
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    print("WARNING: OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")

def parse_openai_response(response_text):
    # Initialize result structure
    result = {
        'website_type': '',
        'description': '',
        'metrics': []
    }
    
    # Split into lines and process each line
    lines = [line.strip() for line in response_text.split('\n') if line.strip()]
    
    current_section = None
    metrics_started = False
    
    for line in lines:
        if 'website type' in line.lower():
            current_section = 'website_type'
            result['website_type'] = line.split(':', 1)[1].strip() if ':' in line else line
        elif 'description' in line.lower():
            current_section = 'description'
            result['description'] = line.split(':', 1)[1].strip() if ':' in line else line
        elif 'metrics' in line.lower() or re.match(r'^\d+\.', line):
            if not metrics_started:
                metrics_started = True
                continue
            # Extract metric name without the number prefix
            metric_name = re.sub(r'^\d+\.\s*', '', line).strip()
            if metric_name:
                result['metrics'].append({
                    'name': metric_name,
                    'tooltip': f'Important metric for understanding the website\'s performance and user engagement.'
                })
    
    return result

def analyze_website(url):
    try:
        print(f"\n=== Starting analysis for URL: {url} ===")
        print(f"OpenAI API Key present: {bool(openai.api_key)}")
        
        if not openai.api_key:
            print("Error: OpenAI API key is missing")
            return {
                'error': 'api_key_missing',
                'message': 'OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file.'
            }
            
        print("Fetching website content...")
        response = requests.get(url)
        print(f"Website response status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'title'])])
        print(f"Extracted text content length: {len(text_content)}")
        
        print("Preparing OpenAI analysis...")
        analysis_prompt = f"""Analyze this website content and provide:

1. Website type: [Describe the type of website (e.g., e-commerce, blog, social media, corporate, etc.)]
2. Description: [A brief description of what the website does or offers]
3. Key metrics that would be important to track for this type of website:
   1. [First important metric]
   2. [Second important metric]
   3. [Third important metric]

Content to analyze: {text_content[:1000]}

Note: Provide specific, measurable metrics that would be relevant for this type of website."""
        
        print("Calling OpenAI API...")
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            print("OpenAI API call successful")
            
            # Parse and structure the response
            print("Parsing OpenAI response...")
            result = parse_openai_response(completion.choices[0].message['content'])
            print(f"Parsed result: {result}")
            return result
            
        except Exception as e:
            print(f"Error during OpenAI processing: {str(e)}")
            return {
                'error': 'openai_error',
                'message': f'Error processing with OpenAI: {str(e)}'
            }
            
    except Exception as e:
        print(f"Error in analyze_website: {str(e)}")
        return {
            'error': 'analysis_error',
            'message': str(e)
        }

# API endpoints
@app.route('/api/analyze', methods=['POST'])
def analyze():
    print("Received analyze request")  # Debug print
    try:
        data = request.get_json()
        if not data:
            print("No JSON data received")  # Debug print
            return jsonify({'error': 'No data provided'}), 400
            
        url = data.get('url')
        if not url:
            print("No URL provided")  # Debug print
            return jsonify({'error': 'URL is required'}), 400
            
        print(f"Analyzing URL: {url}")  # Debug print
        result = analyze_website(url)
        print(f"Analysis result: {result}")  # Debug print
        
        if not result:
            return jsonify({'error': 'Failed to analyze website'}), 400
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
