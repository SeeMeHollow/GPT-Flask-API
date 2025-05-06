from flask import Flask, request, jsonify
import os
import requests
import openai

app = Flask(__name__)

# OpenAI client (NEW SDK FORMAT)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your Power Automate webhook URL
power_automate_url = os.getenv("POWER_AUTOMATE_WEBHOOK_URL")


@app.route('/', methods=['GET'])
def home():
    return "✅ ChatGPT Flask API is running", 200


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    # Accepts "message" or "prompt"
    user_input = data.get('message') or data.get('prompt')

    if not user_input:
        return jsonify({'error': 'No message or prompt provided'}), 400

    try:
        # Generate ChatGPT response (NEW SYNTAX)
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )

        answer = chat_response.choices[0].message.content

        # Send prompt + response to Power Automate
        if power_automate_url:
            payload = {
                "prompt": user_input,
                "response": answer
            }
            headers = {"Content-Type": "application/json"}
            try:
                r = requests.post(power_automate_url, json=payload, headers=headers)
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                print("⚠️ Failed to send to Power Automate:", e)

        return jsonify({'response': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# For local testing
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
