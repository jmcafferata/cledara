from flask import Flask, render_template, request, jsonify, abort, Response
import openai
import pytz
import requests
timezone = pytz.timezone('America/Argentina/Buenos_Aires')
import json
import compliance


app = Flask(__name__)

openai.api_key_path = "openai_api_key.txt"

# FOR DEBUG 👇


# Show index.html
@app.route('/', methods=['GET'])
def index():

    return render_template('index.html')


from flask import Response

@app.route('/get_web_data', methods=['POST'])
def get_web_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        homepage_url = data.get('url')
        data_request = data.get('prompt')

        if not homepage_url or not data_request:
            return jsonify({"error": "Incomplete data received"}), 400

        all_links = compliance.fetch_links_from_homepage(homepage_url)
        relevant_links = compliance.get_relevant_links_via_openai(homepage_url, all_links)

        def generate_data():
            for data_response in compliance.get_information_from_web(relevant_links, data_request):
                yield json.dumps(data_response) + "\n"

        return Response(generate_data(), content_type="application/json")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=5123)