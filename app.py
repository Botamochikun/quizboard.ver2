from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return redirect(url_for('player'))

@app.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            return render_template('player.html', error='名前を入力してください')
        session['name'] = name
        return redirect(url_for('quiz'))
    return render_template('player.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'name' not in session:
        return redirect(url_for('player'))
    if request.method == 'POST':
        # 回答処理など
        pass
    return render_template('quiz.html', username=session['name'])

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
