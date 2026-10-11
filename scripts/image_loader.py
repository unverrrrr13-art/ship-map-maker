from PIL import Image
import numpy as np

from paths import image_path
import config


class LoadedImages:
    def __init__(self, orig: Image.Image, mask: Image.Image):
        self.orig = orig
        self.mask = mask
        self.mask_array = np.array(mask)


def load_images() -> LoadedImages:
    orig = Image.open(image_path(config.IMAGE)).convert("RGBA")
    mask = Image.open(image_path(config.MASK)).convert("RGB")

    if orig.size != mask.size:
        print("Внимание: размеры основного изображения и маски не совпадают!")

    return LoadedImages(orig, mask)