import time
from config import Config


class InterviewTimer:

    def __init__(self):
        self.start_time = None
        self.duration = Config.INTERVIEW_DURATION_MINUTES * 60

    def start(self):
        self.start_time = time.time()

    def remaining(self):

        if not self.start_time:
            return self.duration

        elapsed = time.time() - self.start_time

        remaining = self.duration - elapsed

        return max(0, int(remaining))

    def is_finished(self):

        if not self.start_time:
            return False

        return (time.time() - self.start_time) >= self.duration