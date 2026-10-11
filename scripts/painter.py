from PIL import Image
import numpy as np


class ZonePainter:
    def __init__(self, orig_img: Image.Image, mask_array: np.ndarray):
        self.orig_img = orig_img
        self.mask_array = mask_array
        self.display_img = orig_img.copy()

    def paint_zone(self, zone_id: tuple, color: tuple) -> Image.Image:
        """
        Заливает зону с заданным zone_id (RGB-кортеж из маски) указанным цветом (RGBA).
        Возвращает новый display_img.
        """
        h, w = self.mask_array.shape[:2]

        zone_mask = np.all(self.mask_array == np.array(zone_id), axis=-1)

        overlay = np.zeros((h, w, 4), dtype=np.uint8)
        overlay[zone_mask] = color
        overlay_img = Image.fromarray(overlay, "RGBA")

        self.display_img = Image.alpha_composite(self.orig_img, overlay_img)
        return self.display_img

    def reset(self):
        """Сбросить все заливки."""
        self.display_img = self.orig_img.copy()
        return self.display_img