import hashlib
import math
import re


class EmbeddingService:
    dimensions = 96

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in self._tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [round(value / norm, 6) for value in vector]

    def similarity(self, left: list[float], right: list[float]) -> float:
        return sum(a * b for a, b in zip(left, right))

    def _tokens(self, text: str) -> list[str]:
        lowered = text.lower()
        words = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", lowered)
        bigrams = [lowered[index : index + 2] for index in range(max(len(lowered) - 1, 0)) if not lowered[index : index + 2].isspace()]
        return words + bigrams
