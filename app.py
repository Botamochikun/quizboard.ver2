import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "your-secret-key"  # セッションを使うには必要

# [(name, image_base64, score)]
answers = []
confirmed_scores = {}  # リセット時に確定する点数を保存

@app.route('/')
def index():
    return redirect('/player')

# セッションで保持する回答者名
@app.route("/player", methods=["GET", "POST"])
def player():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return render_template("player.html", error="名前を入力してください")
        session["player_name"] = name
        return redirect(url_for("player_quiz"))
    if "player_name" in session:
        return redirect(url_for("player_quiz"))
    return render_template("player.html")

@app.route("/player/quiz", methods=["GET", "POST"])
def player_quiz():
    if "player_name" not in session:
        return redirect(url_for("player"))

    if request.method == "POST":
        image = request.files["image"]
        # プレイヤー名を取得して画像処理に使う
        name = session["player_name"]
        image.save(f"uploads/{name}.png")
        return redirect(url_for("player_quiz"))  # 名前入力に戻らず、クイズページに留まる

    return render_template("quiz.html", player_name=session["player_name"])

@app.route('/host')
def host():
    return render_template('host.html', answers=answers)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    image = request.form['image']
    # 新規はscore=0で登録。すでに名前があれば上書きしない簡易版
    found = False
    for i, (n, img, sc) in enumerate(answers):
        if n == name:
            answers[i] = (n, image, sc)  # 画像だけ上書き（score維持）
            found = True
            break
    if not found:
        answers.append((name, image, 0))
    return redirect('/player')

@app.route('/score', methods=['POST'])
def score():
    name = request.form['name']
    score = int(request.form['score'])
    for i, (n, img, sc) in enumerate(answers):
        if n == name:
            answers[i] = (n, img, score)
            break
    return '', 204

@app.route('/reset')
def reset():
    global confirmed_scores
    confirmed_scores = {name: score for name, _, score in answers}
    answers.clear()
    return redirect('/host')

@app.route('/scores')
def scores():
    return jsonify(confirmed_scores)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)