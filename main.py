from flask import Flask, render_template, request, jsonify
import openai
import pandas as pd
from openai.embeddings_utils import get_embedding
import numpy as np
from openai.embeddings_utils import cosine_similarity
from pathlib import Path

app = Flask(__name__)

# get openai jkey from openaikey.txt
openai.api_key = open('openaikey.txt', 'r').read()



# Your existing Python code for recommendations
def get_recommendations(search_term):


    THIS_FOLDER = Path(__file__).parent.resolve()
    embeddings_file = THIS_FOLDER / "vendors_embeddings.csv"
    df = pd.read_csv(embeddings_file)
    search_term_vector = get_embedding(search_term, 'text-embedding-ada-002')

    df['embedding'] = df['embedding'].apply(lambda x: x[1:-1].strip('()').split(','))
    df['embedding'] = df['embedding'].apply(lambda x: [float(i) for i in x])

    df['similarity'] = df['embedding'].apply(lambda x: cosine_similarity(x, search_term_vector))
    df = df.sort_values(by=['similarity'], ascending=False)

    return df[['Name', 'Description', 'Logo URL', 'Website URL']].head(10)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        if search_term:  # Check if search_term is not None
            recommendations = get_recommendations(search_term)
            return jsonify(recommendations.to_dict(orient='records'))
        else:
            return jsonify({"error": "Invalid search term"})

    return render_template('index.html')
import compliance
from flask_cors import CORS
# Enable CORS for the entire app. Alternatively, you can specify which routes you want CORS enabled for.
CORS(app, resources={r"/*": {"origins": "https://www.cledara.com"}})

@app.route('/gdpr', methods=['GET'])
def gdpr():
    return render_template('gdpr.html')

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

        data_response = compliance.get_information_from_web(relevant_links, data_request)

        return jsonify({"data": data_response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)