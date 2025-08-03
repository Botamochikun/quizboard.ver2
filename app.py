from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

answers = {}

@app.route('/')
def home():
    return redirect(url_for('player'))

from flask import Flask, render_template, request, redirect, session, url_for
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

answers = {}

@app.route('/')
def index():
    return redirect('/player')

@app.route('/player', methods=['GET', 'POST'])
def player():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            error = "名前を入力してください"
        else:
            session['name'] = name
            if name not in answers:
                answers[name] = {'image_data': None, 'text_answer': None, 'score': 0}
            return redirect('/quiz')
    score = answers.get(session.get('name', ''), {}).get('score', 0)
    return render_template('player.html', error=error, score=score)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    name = session.get('name')
    if not name:
        return redirect('/player')

    if request.method == 'POST':
        image_data = request.form.get('image_data')
        text_answer = request.form.get('text_answer')
        answers[name]['image_data'] = image_data
        answers[name]['text_answer'] = text_answer

    return render_template('quiz.html', name=name, score=answers[name]['score'])

@app.route('/host')
def host():
    answer_list = [
        (name, data['image_data'], data['text_answer'], data['score'])
        for name, data in answers.items()
    ]
    return render_template('host.html', answers=answer_list)

@app.route('/score', methods=['POST'])
def score():
    name = request.form.get('name')
    score = int(request.form.get('score'))
    if name in answers:
        answers[name]['score'] = score
    return redirect('/host')

@app.route('/reset')
def reset():
    # スコアを固定するが、状態は維持
    return redirect('/host')

@app.route('/update_score', methods=['POST'])
def update_score():
    name = request.form['name']
    score = int(request.form['score'])

    if name in answers:
        answers[name]['score'] = score

    return redirect(url_for('host'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
