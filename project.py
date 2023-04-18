# The project.py is the main file that invokes all the necessary procedures
import sys
from interface import Ui_Dialog
from PyQt6.QtWidgets import QApplication, QDialog
import logging
import argparse

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--port", type=str, required=True)
    parser.add_argument("--database", type=str, required=True)
    parser.add_argument("--user", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    args = parser.parse_args()
    app = QApplication(sys.argv)
    Dialog = QDialog()
    ui = Ui_Dialog(
        Dialog, args.host, args.port, args.database, args.user, args.password
    )
    Dialog.show()
    sys.exit(app.exec())
