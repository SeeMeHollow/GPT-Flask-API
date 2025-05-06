from flask import Flask, request, jsonify
import openai
import os
import requests

app = Flask(__name__)

# Get environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
power_automate_url = os.getenv("POWER_AUTOMATE_WEBHOOK_URL")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')

    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Generate ChatGPT response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        answer = response['choices'][0]['message']['content']

        # Send to Power Automate
        payload = {
            "prompt": user_input,
            "response": answer
        }

        headers = {"Content-Type": "application/json"}

        if power_automate_url:
            try:
                pa_response = requests.post(power_automate_url, json=payload, headers=headers)
                pa_response.raise_for_status()
            except requests.exceptions.RequestException as err:
                print("Failed to send to Power Automate:", err)

        return jsonify({'response': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# REQUIRED for Render: use dynamic port and 0.0.0.0
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # fallback port if PORT isn't set
    app.run(host='0.0.0.0', port=port)
