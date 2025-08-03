from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

answers = {}

@app.route('/')
def home():
    return redirect(url_for('player'))

@app.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        name = request.form['name']
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

        answers[name] = {
            "image": image_data,
            "text": text_answer,
            "score": answers.get(name, {}).get("score", 0)
        }

    return render_template('quiz.html', name=name)

@app.route('/host')
def host():
    return render_template('host.html', answers=answers)

@app.route('/reset')
def reset():
    answers.clear()
    return redirect(url_for('host'))

@app.route('/update_score', methods=['POST'])
def update_score():
    name = request.form['name']
    score = int(request.form['score'])

    if name in answers:
        answers[name]['score'] = score

    return redirect(url_for('host'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
