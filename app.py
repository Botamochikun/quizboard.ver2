import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "your-secret-key"

answers = []  # [(name, image_base64 or None, text_answer or None, score)]
confirmed_scores = {}

@app.route('/')
def index():
    return redirect('/player')

@app.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            return render_template('player.html', error='名前を入力してください')
        session['username'] = name
        return redirect(url_for('quiz'))
    if 'username' in session:
        return redirect(url_for('quiz'))
    return render_template('player.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect(url_for('player'))

    if request.method == 'POST':
        # キャンバスからのBase64画像か、テキスト回答を受け取る
        image_data = request.form.get('image_data')
        text_answer = request.form.get('text_answer')

        name = session['username']

        # 既に同じ名前の回答があれば上書き、なければ追加。scoreは維持
        found = False
        for i, (n, img, txt, sc) in enumerate(answers):
            if n == name:
                answers[i] = (n, image_data, text_answer, sc)
                found = True
                break
        if not found:
            answers.append((name, image_data, text_answer, 0))

        return redirect(url_for('quiz'))

    return render_template('quiz.html', username=session['username'])

@app.route('/host')
def host():
    return render_template('host.html', answers=answers)

@app.route('/score', methods=['POST'])
def score():
    name = request.form['name']
    score = int(request.form['score'])
    for i, (n, img, txt, sc) in enumerate(answers):
        if n == name:
            answers[i] = (n, img, txt, score)
            break
    return '', 204

@app.route('/reset')
def reset():
    global confirmed_scores
    confirmed_scores = {name: score for name, _, _, score in answers}
    answers.clear()
    session.clear()
    return redirect('/host')

@app.route('/scores')
def scores():
    return jsonify(confirmed_scores)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
