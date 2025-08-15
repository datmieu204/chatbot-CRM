# phase2/sprint1/llm_client/apikey_manager.py

import os
import itertools

from dotenv import load_dotenv
load_dotenv()

class APIKeys:
    def __init__(self, env: str):
        self.keys = []
        self.index_cycle = None

        i = 0
        while True:
            var_name = env if i == 0 else f"{env}_{i}"
            key = os.getenv(var_name)
            if not key:
                break
            self.keys.append(key.strip())
            i += 1

        if not self.keys:
            raise ValueError(f"Not found {env}")

        self.index_cycle = itertools.cycle(range(len(self.keys)))

    def get_next_key(self):
        idx = next(self.index_cycle)
        return self.keys[idx]