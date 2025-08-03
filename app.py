from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

answers = {}  # {name: {"image":..., "text":..., "score":...}}

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

    name = session['name']

    if request.method == 'POST':
        image_data = request.form.get('image_data')
        text_answer = request.form.get('text_answer')

        if name in answers:
            # 既存更新（スコアは維持）
            answers[name]['image'] = image_data
            answers[name]['text'] = text_answer
        else:
            # 新規登録
            answers[name] = {"image": image_data, "text": text_answer, "score": 0}

        return redirect(url_for('quiz'))

    return render_template('quiz.html', username=name)

@app.route('/host')
def host():
    sorted_answers = sorted(
        [(name, data["image"], data["text"], data["score"]) for name, data in answers.items()],
        key=lambda x: x[3],
        reverse=True
    )
    return render_template('host.html', answers=sorted_answers)

@app.route('/score', methods=['POST'])
def score():
    name = request.form.get('name')
    score = int(request.form.get('score', 0))
    if name in answers:
        answers[name]['score'] = score
    return '', 204

@app.route('/reset')
def reset():
    # 確定処理を必要ならここに追加
    answers.clear()
    session.clear()
    return redirect(url_for('host'))

@app.route('/scores')
def scores():
    # プレイヤー用にスコアだけ返す
    return jsonify({name: data['score'] for name, data in answers.items()})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
