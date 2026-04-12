import numpy as np
import random
import time

def bezier_curve(p0, p1, p2, t):
    return (1-t)**2 * np.array(p0) + 2*(1-t)*t*np.array(p1) + t**2*np.array(p2)

def human_click(device, x, y, tolerance=5):
    time.sleep(random.uniform(0.3, 0.8))
    x1 = x + random.randint(-tolerance, tolerance)
    y1 = y + random.randint(-tolerance, tolerance)
    ctrl_x = (x + x1) // 2 + random.randint(-tolerance, tolerance)
    ctrl_y = (y + y1) // 2 + random.randint(-tolerance, tolerance)
    points = [bezier_curve((x, y), (ctrl_x, ctrl_y), (x1, y1), t) for t in np.linspace(0, 1, 10)]
    for px, py in points:
        device.shell(f'input swipe {int(px)} {int(py)} {int(px)} {int(py)} 10')
        time.sleep(0.01)
    device.shell(f'input tap {x1} {y1}')
