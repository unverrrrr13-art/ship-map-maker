import json
from pathlib import Path
from PIL import Image
import numpy as np

from paths import storage_dir


class ZonePainter:
    STATE_FILE = "state.json"

    def __init__(self, orig_img: Image.Image, mask_array: np.ndarray):
        self.orig_img = orig_img
        self.mask_array = mask_array
        self.display_img = orig_img.copy()

        self._inverse = None
        self._zone_index = None
        self._zone_cache = {}        # zone_id -> (x0, y0, x1, y1, mask_crop)
        self._orig_crop_cache = {}   # zone_id -> np.ndarray (H'×W'×4, оригинал)

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

    def _get_zone_data(self, zone_id):
        """Возвращает (x0, y0, x1, y1, mask_crop) или None."""
        if zone_id in self._zone_cache:
            return self._zone_cache[zone_id]

        self._ensure_index()
        idx = self._zone_index.get(zone_id)
        if idx is None:
            return None

        zone_mask = (self._inverse == idx)
        ys, xs = np.where(zone_mask)
        if len(xs) == 0:
            return None

        x0, x1 = int(xs.min()), int(xs.max()) + 1
        y0, y1 = int(ys.min()), int(ys.max()) + 1
        mask_crop = zone_mask[y0:y1, x0:x1]

        data = (x0, y0, x1, y1, mask_crop)
        self._zone_cache[zone_id] = data
        return data

    def _get_orig_crop(self, zone_id, x0, y0, x1, y1):
        """Оригинал вырезанного прямоугольника (RGBA)."""
        if zone_id in self._orig_crop_cache:
            return self._orig_crop_cache[zone_id]

        crop = np.array(self.orig_img.crop((x0, y0, x1, y1)), dtype=np.uint8)
        self._orig_crop_cache[zone_id] = crop
        return crop

    # === ЗАЛИВКА ===

    def paint_zone(self, zone_id: tuple, color: tuple) -> Image.Image:
        data = self._get_zone_data(zone_id)
        if data is None:
            return self.display_img

        x0, y0, x1, y1, mask_crop = data
        self._apply_zone(zone_id, x0, y0, x1, y1, mask_crop, color)
        self.painted[zone_id] = color
        return self.display_img

    def erase_zone(self, zone_id: tuple) -> bool:
        if zone_id not in self.painted:
            return False

        data = self._get_zone_data(zone_id)
        if data is None:
            del self.painted[zone_id]
            return True

        x0, y0, x1, y1, mask_crop = data
        orig_crop = self._get_orig_crop(zone_id, x0, y0, x1, y1)

        # Возвращаем кусок оригинала обратно
        restored = orig_crop.copy()
        self.display_img.paste(Image.fromarray(restored, "RGBA"), (x0, y0))

        del self.painted[zone_id]
        return True

    def _apply_zone(self, zone_id, x0, y0, x1, y1, mask_crop, color):
        orig_crop = self._get_orig_crop(zone_id, x0, y0, x1, y1)
        disp_crop = np.array(self.display_img.crop((x0, y0, x1, y1)), dtype=np.uint8)

        # Смешивание через numpy
        alpha = color[3] / 255.0
        color_rgb = np.array(color[:3], dtype=np.float32)
        orig_rgb = orig_crop[..., :3].astype(np.float32)

        blended = (orig_rgb * (1.0 - alpha) + color_rgb * alpha).astype(np.uint8)

        # Применяем только к пикселям маски
        m = mask_crop[..., None]  # H'×W'×1 для broadcasting
        disp_crop[..., :3] = np.where(m, blended, disp_crop[..., :3])
        disp_crop[..., 3] = np.where(mask_crop, 255, disp_crop[..., 3])

        self.display_img.paste(Image.fromarray(disp_crop, "RGBA"), (x0, y0))

    def _rebuild(self):
        """Используется только при загрузке состояния — собирает всё разом."""
        self.display_img = self.orig_img.copy()
        for zone_id, color in self.painted.items():
            data = self._get_zone_data(zone_id)
            if data is None:
                continue
            x0, y0, x1, y1, mask_crop = data
            self._apply_zone(zone_id, x0, y0, x1, y1, mask_crop, color)

    def reset(self):
        self.painted.clear()
        self.display_img = self.orig_img.copy()
        self.save_state()
        return self.display_img

    # === СОХРАНЕНИЕ / ЗАГРУЗКА ===

    @property
    def _state_path(self) -> Path:
        return storage_dir() / self.STATE_FILE

    def save_state(self):
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
            print(f"Не удалось загрузить {self._state_path}: {e}")
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