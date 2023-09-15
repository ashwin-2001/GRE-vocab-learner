import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QShortcut, QVBoxLayout, QWidget, \
    QHBoxLayout, QGridLayout, QRadioButton, QMessageBox
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtCore import Qt, QSize
import pandas as pd
from random import sample, choice


class SynonymExplorer(QMainWindow):
    def __init__(self, data, num_pairs=1):
        super().__init__()
        self.data = data
        self.index = 0
        self.dark_mode = False
        self.group_buttons = []
        self.num_pairs = num_pairs
        self.correct_word = ""
        self.initUI()

    def initUI(self):
        # Window settings
        self.setWindowTitle("Synonym Explorer")
        self.setGeometry(100, 100, 800, 900)
        self.set_theme()

        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Dynamic island panel with 18 blocks
        self.island_layout = QGridLayout()
        for i in range(18):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(70, 100)  # Mobile screen-like vertical arrangement
            btn.clicked.connect(self.make_group_jump(i + 1))
            btn.setFont(QFont('Arial', 16))
            self.group_buttons.append(btn)
            self.island_layout.addWidget(btn, i // 6, i % 6)
        self.main_layout.addLayout(self.island_layout)

        # Group ID label
        self.group_label = QLabel()
        self.group_label.setFont(QFont('Arial', 18))
        self.main_layout.addWidget(self.group_label, alignment=Qt.AlignCenter)

        # Word and Synonym display
        self.word_label = QLabel()
        self.word_label.setFont(QFont('Arial', 48))
        self.main_layout.addWidget(self.word_label, alignment=Qt.AlignCenter)

        # Arrow buttons and word counter
        self.navigation_layout = QHBoxLayout()
        self.left_button = QPushButton("<")
        self.left_button.setFont(QFont('Arial', 36))
        self.left_button.clicked.connect(self.prev_word)
        self.navigation_layout.addWidget(self.left_button)
        self.word_counter = QLabel()
        self.navigation_layout.addWidget(self.word_counter, alignment=Qt.AlignCenter)
        self.right_button = QPushButton(">")
        self.right_button.setFont(QFont('Arial', 36))
        self.right_button.clicked.connect(self.next_word)
        self.navigation_layout.addWidget(self.right_button)
        self.main_layout.addLayout(self.navigation_layout)

        # Test and Theme Toggle Button
        self.button_layout = QHBoxLayout()
        self.test_button = QPushButton("Start Test")
        self.test_button.clicked.connect(self.start_test)
        self.button_layout.addWidget(self.test_button)
        self.theme_toggle = QPushButton("Toggle Theme")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        self.button_layout.addWidget(self.theme_toggle)
        self.main_layout.addLayout(self.button_layout)

        # Keyboard shortcuts for navigation
        self.shortcut_next = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut_next.activated.connect(self.next_word)
        self.shortcut_prev = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut_prev.activated.connect(self.prev_word)

        self.update_display()


    def set_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {background-color: #2c2c2c;}
                QLabel {color: white;}
                QPushButton {background-color: #3c3c3c; border: 2px solid #555; border-radius: 10px;}
            """)
            for btn in self.group_buttons:
                btn.setStyleSheet("background-color: #444444; border-radius: 10px;")
        else:
            self.setStyleSheet("""
                QMainWindow {background-color: #f8f8f8;}
                QLabel {color: black;}
                QPushButton {background-color: #e8e8e8; border-radius: 10px;}
            """)
            for btn in self.group_buttons:
                btn.setStyleSheet("background-color: #eeeeee; border-radius: 10px;")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.set_theme()

    def make_group_jump(self, group_num):
        def jump():
            self.index = self.data[self.data['Group ID'] == f'Group {group_num}'].index[0]
            self.update_display()
        return jump

    def update_display(self):
        current_group = self.data.iloc[self.index]['Group ID']
        word_syn_pairs = [f"{self.data.iloc[i]['Word']} : {self.data.iloc[i]['Synonyms']}" for i in
                          range(self.index, min(self.index + self.num_pairs, len(self.data)))]

        # Adjust font size based on number of pairs
        if self.num_pairs > 1:
            self.word_label.setFont(QFont('Arial', 36))
        else:
            self.word_label.setFont(QFont('Arial', 48))

        for btn in self.group_buttons:
            if btn.text() == current_group.split(' ')[1]:
                btn.setStyleSheet("background-color: #bdbbbb; border-radius: 15px; font-size: 18px;")
            else:
                btn.setFont(QFont('Arial', 16))
                btn.setStyleSheet(
                    btn.styleSheet().replace("background-color: #bdbbbb; border-radius: 15px; font-size: 18px;", ""))
        self.group_label.setText(current_group)
        self.word_label.setText("\n".join(word_syn_pairs))
        self.word_counter.setText(f"{self.index + 1} of {len(self.data)}")

    def next_word(self):
        self.index = (self.index + self.num_pairs) % len(self.data)
        self.update_display()

    def prev_word(self):
        if self.index - self.num_pairs < 0:
            self.index = 0
        else:
            self.index -= self.num_pairs
        self.update_display()


    def start_test(self):
        # Hide other elements
        for widget in [self.group_label, self.word_label, self.left_button, self.right_button, self.word_counter, self.theme_toggle, self.test_button]:
            widget.setVisible(False)
        for btn in self.group_buttons:
            btn.setVisible(False)

        # Filter data based on the current group
        self.group_data = self.data[self.data['Group ID'] == self.group_label.text()]
        self.test_index = 0  # to track our position in the group for the quiz

        self.show_question()

    def show_question(self):
        # Check if there are more words in the current group for testing
        if self.test_index < len(self.group_data):
            test_row = self.group_data.iloc[self.test_index]
            self.correct_word = test_row['Word']
            synonym = test_row['Synonyms']

            # Select three other random words as distractors from the current group
            distractors = self.group_data[self.group_data['Word'] != self.correct_word].sample(3)['Word'].tolist()
            options = distractors + [self.correct_word]

            # Randomize the order of the options
            options = sample(options, len(options))

            # Display the synonym
            self.synonym_label = QLabel(f"Synonym: {synonym}")
            self.synonym_label.setFont(QFont('Arial', 40))
            self.main_layout.addWidget(self.synonym_label, alignment=Qt.AlignCenter)

            # Create radio buttons for the options
            self.option_buttons = []
            for opt in options:
                rb = QRadioButton(opt)
                rb.setFont(QFont('Arial', 24))
                # If dark mode is enabled, set the text color to white
                if self.dark_mode:
                    rb.setStyleSheet("color: white;")
                else:
                    rb.setStyleSheet("color: black;")
                self.option_buttons.append(rb)
                self.main_layout.addWidget(rb, alignment=Qt.AlignCenter)

            # Add a submit button to check the answer
            self.submit_button = QPushButton("Submit Answer")
            self.submit_button.setFont(QFont('Arial', 36))
            self.submit_button.setStyleSheet("""
                QPushButton {background-color: #e8e8e8; border-radius: 10px;}
            """)
            self.submit_button.clicked.connect(self.check_answer)
            self.main_layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

            # Add a back button to return to the normal view
            self.back_button = QPushButton("Back")
            self.back_button.setFont(QFont('Arial', 36))
            self.back_button.setStyleSheet("""
                QPushButton {background-color: #e8e8e8; border-radius: 10px;}
            """)
            self.back_button.clicked.connect(self.back_to_normal)
            self.main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

            # Increase the test index for next question
            self.test_index += 1
        else:
            # If no more words are left in the group, show a message and revert to normal view
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("You've completed the test for this group!")
            msg.setWindowTitle("Done")
            msg.exec_()
            self.back_to_normal()

    def check_answer(self):
        selected_option = ""
        for btn in self.option_buttons:
            if btn.isChecked():
                selected_option = btn.text()

        if not selected_option:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select an option!")
            msg.setWindowTitle("Warning")
            msg.exec_()
            return

        # Check if the selected option is correct
        if selected_option == self.correct_word:
            result_msg = "Correct!"
        else:
            result_msg = f"Incorrect! The correct word for the synonym is: {self.correct_word}"

        # Display the result in a message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(result_msg)
        msg.setWindowTitle("Result")
        msg.exec_()

        # Cleanup for next question
        self.synonym_label.deleteLater()
        for btn in self.option_buttons:
            btn.deleteLater()
        self.submit_button.deleteLater()
        self.back_button.deleteLater()

        # Show next question
        self.show_question()

    def back_to_normal(self):
        # Remove test elements if they exist
        if hasattr(self, 'synonym_label'):
            self.synonym_label.deleteLater()
        for btn in self.option_buttons:
            btn.deleteLater()
        if hasattr(self, 'submit_button'):
            self.submit_button.deleteLater()
        if hasattr(self, 'back_button'):
            self.back_button.deleteLater()

        # Show other elements
        self.island_layout.setParent(self.main_layout)  # Re-attach the layout to the main layout
        self.navigation_layout.setParent(self.main_layout)  # Re-attach the layout to the main layout
        self.button_layout.setParent(self.main_layout)  # Re-attach the layout to the main layout
        for widget in [self.group_label, self.word_label, self.left_button, self.right_button, self.word_counter,
                       self.theme_toggle, self.test_button]:
            widget.setVisible(True)
        for btn in self.group_buttons:
            btn.setVisible(True)

        self.update_display()




app = QApplication(sys.argv)
data = pd.read_csv('final_updated_vocab_with_all_groups.csv')

# Allow only till synonym column is not null
data = data[data['Synonyms'].notnull()].reset_index(drop=True)
window = SynonymExplorer(data, num_pairs=1)
window.show()
sys.exit(app.exec_())
