from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_structure", methods=["POST"])
def get_structure():
    chemical_name = request.form.get("chemical_name", "").strip()
    
    if not chemical_name:
        return jsonify({"error": "Please enter a chemical name."})

    # PubChem URLs
    sdf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/SDF?record_type=3d"
    image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/PNG"

    # Fetch data
    sdf_response = requests.get(sdf_url)
    image_response = requests.get(image_url)

    if sdf_response.status_code == 200 and image_response.status_code == 200:
        return jsonify({
            "sdf_data": sdf_response.text,
            "image_url": image_url
        })
    else:
        return jsonify({"error": "Chemical structure not found. Please check the name and try again."})

if __name__ == "__main__":
    app.run(debug=True)
