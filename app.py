from flask import Flask
import os

app = Flask(__name__)

VERSION = os.environ.get('APP_VERSION', 'unknown')
VARIANT = os.environ.get('APP_VARIANT', 'stable')

@app.route('/')
def home():
    color = '#E3F2FD' if VARIANT == 'stable' else '#FFF9C4'
    text_color = '#1565C0' if VARIANT == 'stable' else '#F57F17'
    return f'''
    <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;
                     background-color: {color}">
            <h1>Flask Canary Demo</h1>
            <h2 style="color: {text_color}">
                {VARIANT.upper()} variant
            </h2>
            <p>Version: {VERSION}</p>
            <p>Deployed via Jenkins Canary pipeline</p>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "healthy", "version": VERSION, "variant": VARIANT}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
