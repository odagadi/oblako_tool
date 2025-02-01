# Oblako - Product Analytics Intelligence Tool

Oblako is a web-based tool that analyzes product websites and provides insights about their business model and key metrics. It helps you understand whether a product is B2B, B2C, or both, and suggests the most relevant metrics for measuring success.

## Features

- URL analysis to determine business type (B2B/B2C)
- Product context extraction from web content
- Intelligent suggestion of key product-specific metrics
- Modern, responsive web interface

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Technology Stack

- Flask (Python web framework)
- OpenAI GPT-3.5 (for content analysis)
- TailwindCSS (styling)
- AlpineJS (frontend interactivity)

## Note

This tool requires an OpenAI API key to function. Make sure to keep your API key secure and never commit it to version control.
