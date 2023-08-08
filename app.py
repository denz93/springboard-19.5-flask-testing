from flask import Flask, render_template, session, jsonify, make_response
from werkzeug.exceptions import BadRequest, HTTPException
from pathlib import Path
from boggle import Boggle
import time 
import json
from game_exceptions import GameNotStartedException, GameEndException, DuplicateWordException

app = Flask(__name__)
app.secret_key = '27f1e04722b9038de89efdb450c9f28eb9bea302b03463b3437a10916e134ce3'
app.static_folder = Path('./static').absolute()

boggle_game = Boggle()

"""
Maximum time (in seconds) to guess a word after the game start 
"""
MAX_GUESS_TIME = 60 

CURRENT_GAME_KEY = 'current'
HISTORY_KEY = 'history'

def set_2_list(o):
  if isinstance(0, set):
    return json.dumps(list(o))
  return json.dumps(o)

@app.get('/')
def home_page():
  return render_template('home.html')

@app.get('/current-game')
def get_current_game():
  if CURRENT_GAME_KEY in session:
    state = session.get(CURRENT_GAME_KEY)
    return jsonify({"state": state})
  return jsonify({"state": None})

@app.post('/start/<int:size>')
def start_game(size):
  if CURRENT_GAME_KEY in session:
    return jsonify(session.get(CURRENT_GAME_KEY))
  board = boggle_game.make_board(size)
  score = 0
  timer = time.time()
  data = {"board": board, "score": score, "timer": timer, "found_words": []}
  session.setdefault(CURRENT_GAME_KEY, data)
  return jsonify(data)

@app.post('/guess/<string:word>')
def guess_word(word):
  if CURRENT_GAME_KEY not in session:
    return GameNotStartedException()
  
  data = session.get(CURRENT_GAME_KEY)

  if time.time() - data['timer'] > MAX_GUESS_TIME:
    return GameEndException()
  
  if word in data['found_words']:
    return DuplicateWordException()
  
  status = boggle_game.check_valid_word(data['board'], word)
  if status == 'ok':
    data["score"] = data["score"] + len(word)
    data["found_words"].append(word)
    session[CURRENT_GAME_KEY] = data
    word_indices = boggle_game.find(data['board'], word.upper())
    
    return jsonify({"found": list(word_indices), "score": data["score"]})
  return jsonify({"found": None, "status": status})

@app.post('/end')
def end_game():
  history = session.get(HISTORY_KEY) if HISTORY_KEY in session else {"highscore": 0, "plays": 0}
  if CURRENT_GAME_KEY in session:
    data = session.get(CURRENT_GAME_KEY)
    history['highscore'] = max(history['highscore'], data['score'])
    history['plays'] += 1
    session.pop(CURRENT_GAME_KEY)
    session.setdefault(HISTORY_KEY, history)

  return jsonify({"history": history})

@app.get('/hint')
def hint():
  if CURRENT_GAME_KEY not in session:
    return jsonify({"hints": []})
  data = session.get(CURRENT_GAME_KEY)
  hints = boggle_game.find_possible_words(data["board"])
  return jsonify({"hints": hints})

@app.errorhandler(HTTPException)
def handle_exception(e):
  response = e.get_response()
  response.content_type = 'application/json'
  response.data = json.dumps({
    "code": e.code,
    "name": e.name,
    "description": e.description
  })
  return response
