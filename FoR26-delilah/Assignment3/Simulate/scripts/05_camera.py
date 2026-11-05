"""Take one picture with every camera and save them as PNG files. Works over SSH."""
from PIL import Image

from lekiwi_sim import LeKiwiSim

sim = LeKiwiSim()
sim.set_command(arm=[0, 35, -10, 70, 90, 100])   # reach forward and down over the table
sim.step(100)

for camera in sim.camera_names:
    image = sim.get_image(camera, width=640, height=480)
    print(f"{camera:9s} image shape {image.shape}, type {image.dtype}, "
          f"pixel in the centre (red, green, blue) = {image[240, 320]}")
    Image.fromarray(image).save(f"camera_{camera}.png")
print("saved:", ", ".join(f"camera_{c}.png" for c in sim.camera_names))
