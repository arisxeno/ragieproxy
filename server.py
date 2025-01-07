from flask import Flask, request, jsonify
import requests
import logging
import os
from dotenv import load_dotenv
from pyngrok import ngrok  # Import for ngrok

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/api/forward', methods=['POST'])
def forward_request():
    try:
        # Log the incoming request
        logging.info("Received request at /api/forward")
        logging.info("Request headers: %s", request.headers)
        logging.info("Raw request body: %s", request.data.decode('utf-8'))

        # Parse JSON payload
        data = request.get_json()
        if not data:
            logging.error("No JSON payload found in the request")
            return jsonify({'error': 'Invalid JSON payload'}), 400

        # Log parsed payload
        logging.info("Parsed JSON payload: %s", data)

        # Extract required fields
        api_url = data.get('apiUrl')
        method = data.get('method', 'GET')
        headers = data.get('headers', {})
        body = data.get('body', None)

        # Validate required fields
        if not api_url:
            logging.error('Missing "apiUrl" field in payload')
            return jsonify({'error': 'Missing "apiUrl" field'}), 400

        # Log outgoing request details
        logging.info("Forwarding request to API URL: %s", api_url)
        logging.info("HTTP Method: %s", method)
        logging.info("Headers: %s", headers)
        logging.info("Body: %s", body)

        # Forward the request to the target API
        response = requests.request(
            method=method,
            url=api_url,
            headers=headers,
            json=body
        )

        # Log the response from the target API
        logging.info("Response status code: %s", response.status_code)
        logging.info("Response headers: %s", response.headers)
        logging.info("Response body: %s", response.text)

        # Return the response back to the client
        return jsonify({
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'data': response.json() if response.headers.get('Content-Type', '').startswith('application/json') else response.text
        })
    except Exception as e:
        logging.exception("Error occurred while forwarding the request")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logging.info("Starting server on port %s", port)

    # Start the Flask server
    public_url = ngrok.connect(port)
    logging.info(f"ngrok tunnel created: {public_url}")
    logging.info("You can access your API publicly at this URL.")

    app.run(host='0.0.0.0', port=port)
