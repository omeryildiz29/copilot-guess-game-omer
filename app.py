import os
import random
from flask import Flask, render_template, request, redirect, url_for, session

from db import init_db, insert_score, get_top_scores

# ---- PATH SETTINGS ----
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")
DB_PATH = os.path.join(os.path.dirname(__file__), "game.db")

# ---- FLASK APP ----
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.secret_key = "copilot-secret-key"

# ---- INIT DATABASE ----
init_db(DB_PATH)


# ---- ROUTES ----
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    player = request.form.get("player", "").strip()

    if not player:
        return render_template("index.html", error="Please enter your name.")

    session["player"] = player
    session["secret"] = random.randint(1, 100)
    session["attempts"] = 0
    session["message"] = "Game started! Guess a number between 1 and 100."

    return redirect(url_for("game"))


@app.route("/game", methods=["GET"])
def game():
    if "secret" not in session:
        return redirect(url_for("index"))

    return render_template(
        "game.html",
        player=session.get("player"),
        attempts=session.get("attempts"),
        message=session.get("message"),
    )


@app.route("/guess", methods=["POST"])
def guess():
    if "secret" not in session:
        return redirect(url_for("index"))

    try:
        guess_value = int(request.form.get("guess"))
    except (TypeError, ValueError):
        session["message"] = "Please enter a valid number."
        return redirect(url_for("game"))

    session["attempts"] += 1
    secret = session["secret"]

    if guess_value < secret:
        session["message"] = "Higher ⬆️"
    elif guess_value > secret:
        session["message"] = "Lower ⬇️"
    else:
        player = session["player"]
        attempts = session["attempts"]

        insert_score(DB_PATH, player, attempts)
        session.clear()

        return redirect(
            url_for(
                "leaderboard",
                winner=player,
                attempts=attempts
            )
        )

    return redirect(url_for("game"))


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    scores = get_top_scores(DB_PATH, limit=10)
    return render_template(
        "leaderboard.html",
        scores=scores,
        winner=request.args.get("winner"),
        attempts=request.args.get("attempts"),
    )


# ---- RUN APP ----
if __name__ == "__main__":
    app.run(debug=True)
