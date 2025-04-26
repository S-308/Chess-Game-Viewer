import sys
import io
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, \
    QTextBrowser
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QFont
import chess.pgn
import chess.svg

class ChessInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Game Viewer")
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Arial", 10))
        layout.addWidget(self.text_edit)
        load_button = QPushButton("Load PGN")
        load_button.clicked.connect(self.load_pgn)

        self.prev_button = QPushButton("Previous Move")
        self.prev_button.clicked.connect(self.show_prev_move)
        self.prev_button.setEnabled(False)
        self.next_button = QPushButton("Next Move")
        self.next_button.clicked.connect(self.show_next_move)
        self.next_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(load_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        layout.addLayout(button_layout)

        self.board_widget = QSvgWidget()
        self.board_widget.setMinimumSize(600, 600)
        layout.addWidget(self.board_widget)

        self.notation_text = QTextBrowser()
        layout.addWidget(self.notation_text)

        self.setLayout(layout)
        self.game = None
        self.current_node = None
        self.moves_history = []

    def load_pgn(self):
        pgn_text = self.text_edit.toPlainText()
        self.game = chess.pgn.read_game(io.StringIO(pgn_text))
        if self.game:
            self.current_node = self.game
            self.moves_history = [self.current_node]
            self.show_current_position()
            self.update_buttons()

    def show_current_position(self):
        board = self.game.board()
        moves = []
        for node in self.moves_history:
            move = node.variation(0)
            board.push(move.move)
            moves.append(move)

        svg_board = chess.svg.board(board=board)
        self.board_widget.load(svg_board.encode())
        notation = self.get_notation_text(moves)
        self.notation_text.setHtml(notation)

    def get_notation_text(self, moves):
        notation = ""
        for i, move in enumerate(moves):
            if i % 2 == 0:
                notation += f"<b>{self.game.headers['White']}</b> "
            else:
                notation += f"<b>{self.game.headers['Black']}</b> "
            notation += move.san() + "<br/>"
        return notation

    def show_next_move(self):
        next_node = self.current_node.variation(0)
        if next_node is not None:
            self.current_node = next_node
            self.moves_history.append(self.current_node)
            self.show_current_position()
            self.update_buttons()

    def show_prev_move(self):
        if len(self.moves_history) > 1:
            self.moves_history.pop()
            self.current_node = self.moves_history[-1]
            self.show_current_position()
            self.update_buttons()

    def update_buttons(self):
        self.prev_button.setEnabled(len(self.moves_history) > 1)
        self.next_button.setEnabled(self.current_node.variation(0) is not None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    interface = ChessInterface()
    interface.show()
    sys.exit(app.exec_())
