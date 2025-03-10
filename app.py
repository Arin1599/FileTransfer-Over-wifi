from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import zipfile
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key

# Path to the data folder
DATA_FOLDER = 'data'
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, 'uploads')

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # List all files in the data folder (excluding the uploads folder)
    files = []
    for root, _, filenames in os.walk(DATA_FOLDER):
        if os.path.basename(root) != 'uploads':
            for filename in filenames:
                relative_path = os.path.join(os.path.relpath(root, DATA_FOLDER), filename)
                files.append(relative_path)
    return render_template('index.html', files=files)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(os.path.join(DATA_FOLDER, filename), as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))

    # Save the uploaded file
    file.save(os.path.join(UPLOAD_FOLDER, (file.filename)))
    flash('File uploaded successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/download_all')
def download_all():
    # Prepare ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # Walk through the data folder and add all files (excluding uploads folder)
        for root, _, filenames in os.walk(DATA_FOLDER):
            if os.path.basename(root) != 'uploads':
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.join(os.path.relpath(root, DATA_FOLDER), filename)
                    zip_file.write(file_path, relative_path)
    
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, 
                     download_name='data_files.zip', 
                     mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)