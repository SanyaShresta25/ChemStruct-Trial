import rdkit
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
import py3Dmol
from openbabel import pybel
import cv2
import pytesseract
from flask import Flask, request, render_template, send_file
from io import BytesIO
import requests

app = Flask(__name__)

# Function to convert chemical name to SMILES using PubChem
def name_to_smiles(name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/CanonicalSMILES/TXT"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    return None

# Generate 2D structure from SMILES
def smiles_to_2d_structure(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            img = Draw.MolToImage(mol, size=(300, 300))
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png')
        else:
            return "Invalid SMILES structure"
    except Exception as e:
        return str(e)

# Generate 3D structure (PDB format) using Open Babel
def smiles_to_3d_structure(smiles):
    try:
        mol = pybel.readstring("smi", smiles)
        mol.make3D()
        return mol.write("pdb")
    except Exception as e:
        return str(e)

# Image to text extraction
def image_to_text(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return text.strip()
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('chemical_name')
        smiles = name_to_smiles(name)

        if not smiles:
            return "Error: Chemical name not found in PubChem."

        structure_2d = smiles_to_2d_structure(smiles)
        structure_3d = smiles_to_3d_structure(smiles)

        return render_template('index.html', img=structure_2d, model=structure_3d)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
import rdkit
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
import py3Dmol
from openbabel import pybel
import cv2
import pytesseract
from flask import Flask, request, render_template, send_file, jsonify
from io import BytesIO
import requests
import logging

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
logging.basicConfig(level=logging.INFO)

# Function to convert chemical name to SMILES using PubChem
def name_to_smiles(name):
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/CanonicalSMILES/TXT"
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching SMILES from PubChem: {e}")
        return None

# Generate 2D structure from SMILES
def smiles_to_2d_structure(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            img = Draw.MolToImage(mol, size=(300, 300))
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png')
        else:
            return jsonify({"error": "Invalid SMILES structure"}), 400
    except Exception as e:
        logging.error(f"Error generating 2D structure: {e}")
        return jsonify({"error": str(e)}), 500

# Generate 3D structure (PDB format) using Open Babel
def smiles_to_3d_structure(smiles):
    try:
        mol = pybel.readstring("smi", smiles)
        mol.make3D()
        return mol.write("pdb")
    except Exception as e:
        logging.error(f"Error generating 3D structure: {e}")
        return jsonify({"error": str(e)}), 500

# Image to text extraction
def image_to_text(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('chemical_name')
        if not name:
            return jsonify({"error": "Chemical name is required"}), 400

        smiles = name_to_smiles(name)

        if not smiles:
            return jsonify({"error": "Chemical name not found in PubChem"}), 404

        structure_2d = smiles_to_2d_structure(smiles)
        structure_3d = smiles_to_3d_structure(smiles)

        return render_template('index.html', img=structure_2d, model=structure_3d)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)