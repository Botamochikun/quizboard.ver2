import os
import base64
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "your-secret-key"

answers = []
confirmed_scores = {}

@app.route('/')
def index():
    return redirect('/player')

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

    return render_template("quiz.html", player_name=session["player_name"])

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form['name']
    image_data = request.form['image']

    # image_data が "data:image/png;base64,..." の形式で送られてくるので、ヘッダを削除して保存
    header, encoded = image_data.split(",", 1)
    image_binary = base64.b64decode(encoded)
    filename = f"uploads/{name}.png"
    with open(filename, "wb") as f:
        f.write(image_binary)

    # 回答記録
    found = False
    for i, (n, img, sc) in enumerate(answers):
        if n == name:
            answers[i] = (n, image_data, sc)
            found = True
            break
    if not found:
        answers.append((name, image_data, 0))
    return jsonify({"success": True})

@app.route("/host")
def host():
    return render_template("host.html", answers=answers)

@app.route("/score", methods=["POST"])
def score():
    name = request.form['name']
    score = int(request.form['score'])
    for i, (n, img, sc) in enumerate(answers):
        if n == name:
            answers[i] = (n, img, score)
            break
    return '', 204

@app.route("/reset")
def reset():
    global confirmed_scores
    confirmed_scores = {name: score for name, _, score in answers}
    answers.clear()
    return redirect('/host')

@app.route("/scores")
def scores():
    return jsonify(confirmed_scores)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
