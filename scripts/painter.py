from PIL import Image
import numpy as np


class ZonePainter:
    def __init__(self, orig_img: Image.Image, mask_array: np.ndarray):
        self.orig_img = orig_img
        self.mask_array = mask_array
        self.display_img = orig_img.copy()

        # Кэш зон: (r, g, b) -> булев массив (H, W), где True = пиксель этой зоны
        self.zones = self._build_zone_cache(mask_array)

    @staticmethod
    def _build_zone_cache(mask_array: np.ndarray) -> dict:
        """
        Один быстрый проход по маске:
        - каждый пиксель (r,g,b) -> 24-битное число
        - np.unique по одномерному массиву целых (очень быстро)
        - inverse даёт индекс зоны для каждого пикселя
        """
        h, w = mask_array.shape[:2]

        flat = mask_array.reshape(-1, 3).astype(np.uint32)
        keys = (flat[:, 0] << 16) | (flat[:, 1] << 8) | flat[:, 2]

        unique_keys, inverse = np.unique(keys, return_inverse=True)
        inverse = inverse.reshape(h, w)

        cache = {}
        for i, key in enumerate(unique_keys):
            r = int((key >> 16) & 0xFF)
            g = int((key >> 8) & 0xFF)
            b = int(key & 0xFF)
            color = (r, g, b)
            if color == (0, 0, 0):   # чёрный = фон/границы, пропускаем
                continue
            cache[color] = (inverse == i)

        return cache

    def paint_zone(self, zone_id: tuple, color: tuple) -> Image.Image:
        zone_mask = self.zones.get(zone_id)
        if zone_mask is None:
            return self.display_img

        h, w = self.mask_array.shape[:2]
        overlay = np.zeros((h, w, 4), dtype=np.uint8)
        overlay[zone_mask] = color
        overlay_img = Image.fromarray(overlay, "RGBA")

        self.display_img = Image.alpha_composite(self.orig_img, overlay_img)
        return self.display_img

    def reset(self):
        self.display_img = self.orig_img.copy()
        return self.display_img