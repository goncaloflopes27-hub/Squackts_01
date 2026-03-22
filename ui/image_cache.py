from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import tkinter as tk


class ImageCache:
    def __init__(self, max_items: int = 32):
        self.max_items = max_items
        self._cache: OrderedDict[str, tk.PhotoImage] = OrderedDict()

    def get(self, path: str) -> tk.PhotoImage | None:
        key = str(Path(path))
        img = self._cache.get(key)
        if img is not None:
            self._cache.move_to_end(key)
        return img

    def put(self, path: str, image: tk.PhotoImage) -> None:
        key = str(Path(path))
        self._cache[key] = image
        self._cache.move_to_end(key)
        while len(self._cache) > self.max_items:
            self._cache.popitem(last=False)
