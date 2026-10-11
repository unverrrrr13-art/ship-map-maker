import json
from pathlib import Path
from PIL import Image
import numpy as np

from paths import project_root


class ZonePainter:
    STATE_FILE = "state.json"   # лежит в корне проекта

    def __init__(self, orig_img: Image.Image, mask_array: np.ndarray):
        self.orig_img = orig_img
        self.mask_array = mask_array
        self.display_img = orig_img.copy()

        self._inverse = None
        self._zone_index = None

        # Состояние: (r, g, b) зоны -> (r, g, b, a) цвет заливки
        self.painted = {}
        self.load_state()

    # === ИНДЕКС ЗОН ===

    def _ensure_index(self):
        if self._inverse is not None:
            return

        h, w = self.mask_array.shape[:2]
        flat = self.mask_array.reshape(-1, 3).astype(np.uint32)
        keys = (flat[:, 0] << 16) | (flat[:, 1] << 8) | flat[:, 2]
        unique_keys, inverse = np.unique(keys, return_inverse=True)

        self._inverse = inverse.reshape(h, w)
        self._zone_index = {}
        for i, key in enumerate(unique_keys):
            r = int((key >> 16) & 0xFF)
            g = int((key >> 8) & 0xFF)
            b = int(key & 0xFF)
            self._zone_index[(r, g, b)] = i

    # === ЗАЛИВКА ===

    def paint_zone(self, zone_id: tuple, color: tuple) -> Image.Image:
        """
        Красит зону zone_id в цвет color.
        Цвет запоминается; при повторной покраске той же зоны — заменяет.
        """
        self.painted[zone_id] = color
        self._rebuild()
        return self.display_img

    def _rebuild(self):
        """
        Строит display_img из оригинала + всех текущих заливок.
        Каждая заливка накладывается на предыдущую.
        """
        self._ensure_index()

        h, w = self.mask_array.shape[:2]
        result = self.orig_img.copy()

        for zone_id, color in self.painted.items():
            idx = self._zone_index.get(zone_id)
            if idx is None:
                continue

            zone_mask = (self._inverse == idx)
            overlay = np.zeros((h, w, 4), dtype=np.uint8)
            overlay[zone_mask] = color
            overlay_img = Image.fromarray(overlay, "RGBA")
            result = Image.alpha_composite(result, overlay_img)

        self.display_img = result

    def reset(self):
        self.painted.clear()
        self.display_img = self.orig_img.copy()
        self.save_state()
        return self.display_img

    # === СОХРАНЕНИЕ / ЗАГРУЗКА ===

    @property
    def _state_path(self) -> Path:
        return project_root() / self.STATE_FILE

    def save_state(self):
        """
        Ключи JSON должны быть строками, поэтому (r,g,b) превращаем в 'r,g,b'.
        """
        data = {
            "painted": {
                f"{z[0]},{z[1]},{z[2]}": list(color)
                for z, color in self.painted.items()
            }
        }
        with open(self._state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_state(self):
        if not self._state_path.is_file():
            return

        try:
            with open(self._state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Не удалось загрузить state.json: {e}")
            return

        painted = data.get("painted", {})
        self.painted = {}
        for key, color in painted.items():
            try:
                r, g, b = (int(x) for x in key.split(","))
                self.painted[(r, g, b)] = tuple(color)
            except (ValueError, TypeError):
                continue

        if self.painted:
            self._rebuild()
    
    def erase_zone(self, zone_id: tuple) -> bool:
        """
        Снимает заливку с зоны zone_id.
        Возвращает True, если зона была покрашена и её удалили.
        """
        if zone_id not in self.painted:
            return False
        del self.painted[zone_id]
        self._rebuild()
        return True