from enum import Enum

class State(Enum):
    not_started = 0
    finished = 1
    launched = 2
    failed = 3