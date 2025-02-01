from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import openai
import re
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

def parse_openai_response(response_text):
    # Initialize result structure
    result = {
        'business_type': '',
        'description': '',
        'metrics': []
    }
    
    # Split into lines and process each line
    lines = [line.strip() for line in response_text.split('\n') if line.strip()]
    
    current_section = None
    metrics_started = False
    
    for line in lines:
        if 'business type' in line.lower():
            current_section = 'business_type'
            result['business_type'] = line.split(':', 1)[1].strip() if ':' in line else line
        elif 'product description' in line.lower():
            current_section = 'description'
            result['description'] = line.split(':', 1)[1].strip() if ':' in line else line
        elif 'metrics' in line.lower():
            current_section = 'metrics'
            metrics_started = True
        elif metrics_started and re.match(r'^\d+\.', line):
            # Extract metric name without the number prefix
            metric_name = re.sub(r'^\d+\.\s*', '', line).strip()
            result['metrics'].append({
                'name': metric_name,
                'tooltip': generate_metric_tooltip(metric_name)
            })
    
    return result

def generate_metric_tooltip(metric_name):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Explain in 2-3 sentences why '{metric_name}' is an important metric for measuring product success. Focus on business impact and value. Keep it concise."
            }]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        return f"This metric helps measure product success and business impact."

def generate_metric_details(metric_name, product_type, product_description):
    try:
        prompt = f"""For a {product_type} product that {product_description}, provide the following about the metric '{metric_name}':
1. A practical example of how this metric specifically applies to this product (1 sentence, be very specific)
2. A clear explanation of what this metric means in general and why it matters (2-3 sentences)

Format:
Example: [specific example for this product]
Explanation: [general explanation of the metric]"""

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = completion.choices[0].message['content']
        
        # Parse the response
        example = ""
        explanation = ""
        
        for line in response.split('\n'):
            if line.lower().startswith('example:'):
                example = line.split(':', 1)[1].strip()
            elif line.lower().startswith('explanation:'):
                explanation = line.split(':', 1)[1].strip()
        
        return {
            'example': example,
            'tooltip': explanation
        }
    except Exception as e:
        return {
            'example': f'Example for {metric_name} not available',
            'tooltip': f'Explanation of {metric_name} not available'
        }

def is_product_company(soup, text_content):
    # Keywords that indicate a product company
    product_keywords = [
        'pricing', 'features', 'product', 'platform', 'trial',
        'download', 'subscribe', 'software', 'app', 'solution',
        'dashboard', 'integration', 'api', 'signup', 'demo'
    ]
    
    # Check meta tags
    meta_tags = soup.find_all('meta', attrs={'name': ['description', 'keywords']})
    meta_content = ' '.join([tag.get('content', '').lower() for tag in meta_tags])
    
    # Check for keywords in text and meta content
    text_content = text_content.lower()
    keyword_count = sum(1 for keyword in product_keywords if keyword in text_content or keyword in meta_content)
    
    # If we find at least 3 product-related keywords, consider it a product company
    return keyword_count >= 3

def analyze_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'title'])])
        
        # Check if it's a product company
        if not is_product_company(soup, text_content):
            return {
                'error': 'not_product_company',
                'message': f'This tool is designed for product companies. It looks like {url} might be a service-based company or not a product website. Try a product-based URL.'
            }
        
        # Use OpenAI to analyze the content
        analysis_prompt = f"""Based on this website content, provide a structured analysis with exactly these components:

1. Business type (B2B, B2C, or both): [your answer]
2. Brief product description: [your answer]
3. The three most important metrics specific to this type of product (be very specific to the product):
   1. [first metric name]
   2. [second metric name]
   3. [third metric name]

Content to analyze: {text_content[:1000]}

Note: For metrics, provide specific, measurable metrics that directly relate to this product's success. Avoid generic metrics."""
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": analysis_prompt}]
        )
        
        # Parse and structure the response
        result = parse_openai_response(completion.choices[0].message['content'])
        
        # Generate detailed metrics with examples
        enhanced_metrics = []
        for metric in result['metrics']:
            details = generate_metric_details(
                metric['name'], 
                result['business_type'], 
                result['description']
            )
            enhanced_metrics.append({
                'name': metric['name'],
                'example': details['example'],
                'tooltip': details['tooltip']
            })
        
        # Ensure we have exactly 3 metrics
        if len(enhanced_metrics) < 3:
            default_metrics = [
                {
                    'name': 'User Engagement Rate',
                    'example': f'Tracking how often users interact with key features of {url}',
                    'tooltip': 'Measures the frequency and depth of user interactions with a product. High engagement often correlates with user satisfaction and product stickiness.'
                },
                {
                    'name': 'Customer Retention Rate',
                    'example': f'Percentage of users who continue using {url} after their first month',
                    'tooltip': 'Shows how well the product retains its users over time. Higher retention indicates strong product-market fit and user satisfaction.'
                },
                {
                    'name': 'Feature Adoption Rate',
                    'example': f'Percentage of users utilizing the core features of {url}',
                    'tooltip': 'Tracks how many users are taking advantage of key product features. Higher adoption rates suggest better product understanding and value delivery.'
                }
            ]
            
            while len(enhanced_metrics) < 3:
                enhanced_metrics.append(default_metrics[len(enhanced_metrics)])
        
        result['metrics'] = enhanced_metrics[:3]  # Ensure exactly 3 metrics
        return result
    except Exception as e:
        return str(e)

# Common domains and popular websites for suggestions
POPULAR_DOMAINS = ['.com', '.org', '.net', '.io', '.co', '.app']
POPULAR_WEBSITES = [
    {'name': 'Slack', 'domain': 'slack.com'},
    {'name': 'GitHub', 'domain': 'github.com'},
    {'name': 'Notion', 'domain': 'notion.so'},
    {'name': 'Figma', 'domain': 'figma.com'},
    {'name': 'Dropbox', 'domain': 'dropbox.com'},
    {'name': 'Zoom', 'domain': 'zoom.us'},
    {'name': 'Linear', 'domain': 'linear.app'},
    {'name': 'Asana', 'domain': 'asana.com'},
    {'name': 'Trello', 'domain': 'trello.com'},
    {'name': 'Jira', 'domain': 'atlassian.com'},
    {'name': 'Monday', 'domain': 'monday.com'},
    {'name': 'Miro', 'domain': 'miro.com'}
]

def get_url_suggestions(query):
    query = query.lower().strip()
    if not query:
        return []
        
    suggestions = []
    
    # If query doesn't have a dot, suggest domain extensions
    if '.' not in query:
        # Suggest domain extensions
        for domain in POPULAR_DOMAINS:
            suggestions.append({
                'url': f'https://{query}{domain}',
                'displayText': f'{query}{domain}'
            })
            
        # Suggest matching popular websites
        for site in POPULAR_WEBSITES:
            if query in site['name'].lower() or query in site['domain'].lower():
                suggestions.append({
                    'url': f'https://{site["domain"]}',
                    'displayText': f'{site["name"]} ({site["domain"]})'
                })
    else:
        # If query has a dot, suggest only matching popular websites
        base_query = query.split('.')[0]
        for site in POPULAR_WEBSITES:
            if (base_query in site['name'].lower() or 
                base_query in site['domain'].lower() or 
                query in site['domain'].lower()):
                suggestions.append({
                    'url': f'https://{site["domain"]}',
                    'displayText': f'{site["name"]} ({site["domain"]})'
                })
                
        # Also suggest the query itself with different protocols
        if not query.startswith(('http://', 'https://')):
            suggestions.insert(0, {
                'url': f'https://{query}',
                'displayText': query
            })
    
    return suggestions[:5]  # Return top 5 suggestions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    result = analyze_website(url)
    return jsonify({'result': result})

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').lower()
    if not query or len(query) < 2:
        return jsonify([])
        
    suggestions = get_url_suggestions(query)
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
