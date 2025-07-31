from PIL import Image
import mss
import numpy as np

def capture_region(region=(0, 0, 1920, 1080)) -> Image.Image:
    with mss.mss() as sct:
        monitor = {
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3]
        }
        img = sct.grab(monitor)
        img_np = np.array(img)
        img_rgb = img_np[:, :, :3][:, :, ::-1]
        return Image.fromarray(img_rgb)