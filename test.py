from unittest import TestCase, main
from app import app, CURRENT_GAME_KEY
from flask import session
from boggle import Boggle
import json 
from collections import OrderedDict
class FlaskTests(TestCase):
    bg = Boggle(5)
    board =  [
        ["N","V","C","N","Z"],
        ["E","H","R","X","N"],
        ["D","Z","C","N","N"],
        ["N","E","I","F","W"],
        ["F","F","P","R","J"]]
    def test_boggle_find(self):
        self.assertListEqual(self.bg.find(self.board, "END"), [(3,1), (3, 0), (2, 0)])
        self.assertListEqual(self.bg.find(self.board, "IN"), [(3, 2), (2, 3)])
        self.assertEqual(self.bg.find(self.board, "APPLE"), False)
    
    def test_boggle_check_valid_word(self):
        self.assertEqual(self.bg.check_valid_word(self.board, "pic"), "ok")
        self.assertEqual(self.bg.check_valid_word(self.board, "apple"), "not-on-board")
        self.assertEqual(self.bg.check_valid_word(self.board, "kic"), "not-word")

    def test_start_game(self):
        with app.test_client() as client:
            res = client.post('/start/5')
            data = res.get_json()
            self.assertIn("board", data)
            self.assertIn("found_words", data)
            self.assertIn("timer", data)
            self.assertIn("score", data)

            self.assertIn(CURRENT_GAME_KEY, session)
            self.assertDictEqual(data, session[CURRENT_GAME_KEY])
    def test_get_current_game(self):
        with app.test_client() as client:
            res = client.get('/current-game')
            data = res.get_json()
            self.assertIn("state", data)
            self.assertEqual(data["state"], None)

            client.post('/start/5')
            res = client.get('/current-game')
            data = res.get_json()
            self.assertIn("state", data)
            self.assertIsNotNone(data["state"])

    def test_guess_word(self):
        with app.test_client() as client:
            client.post('/start/5')
            # state = session[CURRENT_GAME_KEY]
            with client.session_transaction() as sess:
                sess[CURRENT_GAME_KEY]["board"] = self.board
                sess.modified = True
            res = client.post('/guess/end')
            data = res.get_json()
            self.assertDictEqual(data, {
                "found": [[3, 1], [3, 0], [2, 0]],
                "score": 3
            })
        