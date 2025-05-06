from flask import Flask, request, jsonify
import openai
import os
import requests  # for outbound HTTP requests

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace this with your actual Power Automate webhook URL
POWER_AUTOMATE_WEBHOOK_URL = os.getenv("POWER_AUTOMATE_WEBHOOK_URL")

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

        # Push response to Power Automate via HTTP POST
        payload = {
            "prompt": user_input,
            "response": answer
        }
        headers = {'Content-Type': 'application/json'}

        try:
            pa_response = requests.post(POWER_AUTOMATE_WEBHOOK_URL, json=payload, headers=headers)
            pa_response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("Error posting to Power Automate:", err)

        return jsonify({'response': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
