### A basic chess engine written by Edward Hicks

Ensure you have uv sync (or equivalent) to recreate the python virtual environment.  PyGame 2.6.1 runs on python 3.12 but I have encountered errors on later versions of python.

To play:
1) In ChessMain.py set the whitePlayer and blackPlayer Booleans.  True = Human player.  False = AI player.  Two humans and two AIs can play against each other.
2) In ChessAI.py set the difficulty of the AI by raising/lowering the AI player depth (WhiteDepth/BlackDepth).  Max depth is currently 4 before the engine takes so long the game is unplayable.
3) When it is a human's turn, you can undo a move by pressing the 'z' key.  This will undo the last human player's move (as well as the last AI's move if playing an AI).


ChessMain.py is the main driver for the game.

ChessGameState.py is the GameState class that holds the board information.

ChessAI.py controls how the Engine plays.

Move.py holds the Move and Castle classes.

PieceScore.py stores the piece and position scores that the engine uses to decide on the best moves.

DisplayFuncs.py controls how PyGame loads and displays the board and images.

RedundantChessAI.py holds less efficient, now redundant, move algorithms.



