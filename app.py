from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

answers = {}

@app.route('/')
def index():
    return redirect('/quiz')  # ← または /host にリダイレクトするように変更

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        session['name'] = request.form['name']
        answers[session['name']] = {"image": None, "score": 0}
        return redirect(url_for('quiz'))
    if 'name' not in session:
        return redirect(url_for('index'))
    return render_template('quiz.html', name=session['name'])

@app.route('/submit', methods=['POST'])
def submit():
    name = session.get('name')
    if not name:
        return 'No name in session', 400
    image_data = request.json.get('image')
    answers[name]['image'] = image_data
    return 'Image received', 200

@app.route('/score', methods=['POST'])
def score():
    name = session.get('name')
    if not name:
        return 'No name in session', 400
    point = request.json.get('point', 0)
    answers[name]['score'] += point
    return 'Score updated', 200

@app.route('/scores', methods=['GET'])
def scores():
    return jsonify(answers)

@app.route('/host')
def host():
    sorted_answers = sorted(
        [(name, data["image"], data["score"]) for name, data in answers.items()],
        key=lambda x: x[2],
        reverse=True
    )
    return render_template('host.html', answers=sorted_answers)

@app.route('/reset', methods=['POST'])
def reset():
    for data in answers.values():
        data["image"] = None
        data["score"] = 0
    return 'Reset done', 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
