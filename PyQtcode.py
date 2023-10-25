import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QTimeEdit, QDateEdit, QMessageBox
from PyQt5.QtCore import QTime, QTimer, QDate
from datetime import datetime

class ToDoListApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Application")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Load the CSS file
        with open('theme.css', 'r') as file:
            style = file.read()
        self.setStyleSheet(style)

        layout = QVBoxLayout()

        self.task_input = QLineEdit()
        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("hh:mm")
        self.time_input.setTime(QTime.currentTime())

        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())

        self.task_list = QListWidget()

        layout.addWidget(QLabel("Task:"))
        layout.addWidget(self.task_input)
        layout.addWidget(QLabel("Time:"))
        layout.addWidget(self.time_input)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.date_input)
        layout.addWidget(self.add_button)
        layout.addWidget(QLabel("To-Do List:"))
        layout.addWidget(self.task_list)

        self.edit_button = QPushButton("Edit Task")
        self.remove_button = QPushButton("Remove Task")
        self.edit_button.clicked.connect(self.edit_task)
        self.remove_button.clicked.connect(self.remove_task)

        layout.addWidget(self.edit_button)
        layout.addWidget(self.remove_button)

        central_widget.setLayout(layout)

        self.alert_timer = QTimer(self)
        self.alert_timer.timeout.connect(self.check_alerts)
        self.alert_timer.start(1000)

        self.tasks = {}
        # Dictionary to store the time of the last alert for each task
        self.last_alert_time = {}

        self.data_folder = "task_data"
        os.makedirs(self.data_folder, exist_ok=True)

        self.load_tasks_from_files()

    def edit_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            new_task = self.task_input.text()
            new_time = self.time_input.time()
            new_date = self.date_input.date()
            # Ensure you correctly access the task text
            task_text = selected_item.text().split(' (Alert at ')[0]
            # Remove the old task entry
            self.remove_task_from_file(task_text)
            # Add the new task entry
            self.tasks[new_task] = (new_date, new_time)
            self.save_task_to_file(new_task, new_date, new_time)
            selected_item.setText(f"{new_task} (Alert at {new_time.toString('hh:mm')}")
            self.task_input.clear()

    def remove_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_text = selected_item.text().split(' (Alert at ')[0]
            if task_text in self.tasks:
                del self.tasks[task_text]
            row = self.task_list.row(selected_item)
            self.task_list.takeItem(row)
            self.remove_task_from_file(task_text)


    def remove_task_from_file(self, task_text):
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        file_name = os.path.join(self.data_folder, f"{date_str}.txt")
    
    # Check if the file exists before trying to open it
        if os.path.exists(file_name):
            # Read the existing file content
            with open(file_name, "r") as file:
                lines = file.readlines()
        # Write back all lines except the one that matches the task_text
            with open(file_name, "w") as file:
                for line in lines:
                    if task_text not in line:
                        file.write(line)


    def add_task(self):
        task = self.task_input.text()
        alert_time = self.time_input.time()
        alert_date = self.date_input.date()

        if task:
            self.tasks[task] = (alert_date, alert_time)
            self.task_list.addItem(f"{task} (Alert at {alert_time.toString('hh:mm')})")
            self.save_task_to_file(task, alert_date, alert_time)
            self.task_input.clear()

    def check_alerts(self):
        current_date = datetime.now().date()
        current_time = QTime.currentTime()

        for task, (alert_date, alert_time) in list(self.tasks.items()):
            if (alert_date == current_date) and (current_time.addSecs(60 * 10) >= alert_time):
                self.show_alert(task, alert_time)
                if self.should_alert(task):
                    self.show_alert(task, alert_time)

    def should_alert(self, task):
        # Check if it's time for a new alert for the task
        current_time = QTime.currentTime()
        last_alert_time = self.last_alert_time.get(task)

        if last_alert_time is None or current_time > last_alert_time.addSecs(60 * 10):
            self.last_alert_time[task] = current_time
            return True
        else:
            return False
        
    def show_alert(self, task, alert_time):
        alert_message = QMessageBox()
        alert_message.setIcon(QMessageBox.Information)
        alert_message.setWindowTitle("Task Alert")
        alert_message.setText(f"It's time for your task:\n{task}\nAlert set for {alert_time.toString('hh:mm')}")
        ok_button = alert_message.addButton(QMessageBox.Ok)
        minimize_button = alert_message.addButton("Minimize", QMessageBox.ActionRole)
    # Connect the clicked signal of the "Ok" button to a method that removes the task and checks for tasks left
        ok_button.clicked.connect(lambda: self.on_ok_pressed(task, alert_message))
    # Connect the clicked signal of the "Minimize" button to minimize the message box
        minimize_button.clicked.connect(alert_message.showMinimized)
    # Disable the timer temporarily to prevent immediate re-triggering
        self.alert_timer.stop()
        alert_message.exec_()
    # Re-enable the timer
        self.alert_timer.start(1000)
    def on_ok_pressed(self, task, alert_message):
    # Remove the task from the tasks dictionary
        if task in self.tasks:
            del self.tasks[task]
    # Remove the task from the corresponding task file
        self.remove_task_from_file(task)
    # Check if there are any tasks left, and stop the timer if not
        if not self.tasks:
            self.alert_timer.stop()
    # Close the alert message
        alert_message.close()

    def save_task_to_file(self, task, alert_date, alert_time):
        date_str = alert_date.toString("yyyy-MM-dd")
        file_name = os.path.join(self.data_folder, f"{date_str}.txt")
        with open(file_name, "a") as file:
            file.write(f"{alert_time.toString('hh:mm')} - {task}\n")

    def load_tasks_from_files(self):
        for filename in os.listdir(self.data_folder):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.data_folder, filename)
                with open(file_path, "r") as file:
                    for line in file:
                        parts = line.strip().split(" - ")
                        if len(parts) == 2:
                            alert_time = QTime.fromString(parts[0], "hh:mm")
                            task = parts[1]
                            self.tasks[task] = (QDate.fromString(filename, "yyyy-MM-dd"), alert_time)
                            self.task_list.addItem(f"{task} (Alert at {alert_time.toString('hh:mm')}")

def launch_todo_app():
    app = QApplication(sys.argv)
    window = ToDoListApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_todo_app()
