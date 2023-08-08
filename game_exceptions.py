from werkzeug.exceptions import HTTPException

class GameNotStartedException(HTTPException):
    description = 'Game not started yet'
    
class GameEndException(HTTPException):
    description = 'Game ended'

class DuplicateWordException(HTTPException):
    description = 'Word dupplicate'