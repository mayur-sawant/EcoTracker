from pathlib import Path
from datetime import datetime


class EcoLogger:

    def __init__(self, log_path):

        self.log_path = Path(log_path)

        self.log_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


    def log(
        self,
        message
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        entry = (
            f"[{timestamp}] {message}\n"
        )


        with open(
            self.log_path,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(entry)


    def read_logs(self):

        if not self.log_path.exists():

            return "No logs available."


        with open(
            self.log_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()