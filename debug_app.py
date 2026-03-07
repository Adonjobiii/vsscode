from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return "DEBUG HOME"

@app.route('/api/test')
def test():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5002, debug=True)
