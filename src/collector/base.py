from typing import Dict, Any


class Collector:
    def collect(self, run_date: str) -> Dict[str, Any]:
        raise NotImplementedError
