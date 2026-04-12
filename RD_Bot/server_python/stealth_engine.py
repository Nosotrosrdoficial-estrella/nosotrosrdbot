import numpy as np
import random
import adbutils
import time

def bezier_curve(p0, p1, p2, t):
    return (1-t)**2 * np.array(p0) + 2*(1-t)*t*np.array(p1) + t**2*np.array(p2)

def human_click(device, x, y, tolerance=10):
    x1 = x + random.randint(-tolerance, tolerance)
    y1 = y + random.randint(-tolerance, tolerance)
    ctrl_x = (x + x1) // 2 + random.randint(-tolerance, tolerance)
    ctrl_y = (y + y1) // 2 + random.randint(-tolerance, tolerance)
    points = [bezier_curve((x, y), (ctrl_x, ctrl_y), (x1, y1), t) for t in np.linspace(0, 1, 10)]
    for px, py in points:
        device.shell(f'input swipe {int(px)} {int(py)} {int(px)} {int(py)} 10')
        time.sleep(random.uniform(0.01, 0.03))
    device.shell(f'input tap {x1} {y1}')

def variable_sleep(min_s=0.3, max_s=0.8):
    time.sleep(random.uniform(min_s, max_s))

# Ejemplo de uso
if __name__ == "__main__":
    device = adbutils.adb.device()
    human_click(device, 500, 1000)
    variable_sleep()
