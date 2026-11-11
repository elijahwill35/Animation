"""Build a 2D puppet rig from the single avatar still.

Outputs (in assets/rig/):
  base.png        body without arms; phone/hand removed and face/neck rebuilt
  upper_L.png     viewer-left upper arm (incl. deltoid)
  fore_L.png      viewer-left forearm + hand
  upper_R.png / fore_R.png   mirrored copies used for the other arm
  masks_*.png     muscle masks (biceps / triceps / forearm) for the glow effect
  rig.json        pivot coordinates
"""
import json
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(ASSETS, "rig")
os.makedirs(OUT, exist_ok=True)

rgb = np.array(Image.open(os.path.join(ASSETS, "avatar.png")).convert("RGB")).astype(np.float32)
alpha = np.array(Image.open(os.path.join(ASSETS, "avatar_cut.png")).split()[-1]).astype(np.float32) / 255.0
H, W = alpha.shape

# Clean the cutout alpha a little (u2net leaves soft haze).
alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)

AXIS_FACE = 590.0   # nose line, used to rebuild the hidden cheek
AXIS_BODY = 545.0   # torso centre line, used for neck/trap and the mirrored arm


def poly_mask(points, feather=0):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    m = np.array(m).astype(np.float32) / 255.0
    if feather:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


def remap_x(img, src_x):
    """Sample img at (src_x[y,x], y) with bilinear filtering."""
    map_y = np.repeat(np.arange(H, dtype=np.float32)[:, None], W, axis=1)
    return cv2.remap(img, src_x.astype(np.float32), map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


xs = np.repeat(np.arange(W, dtype=np.float32)[None, :], H, axis=0)
ys = np.repeat(np.arange(H, dtype=np.float32)[:, None], W, axis=1)

# ---------------------------------------------------------------- left arm
ARM_UPPER = [(352, 238), (395, 228), (432, 248), (446, 300), (444, 380), (436, 470),
             (432, 560), (395, 580), (348, 560), (336, 470), (334, 380), (334, 300)]
ARM_FORE = [(346, 515), (430, 515), (440, 600), (446, 690), (466, 742), (494, 790),
            (504, 850), (486, 888), (440, 892), (402, 872), (390, 800), (390, 735), (368, 640), (348, 580)]
SHOULDER_L = (392.0, 292.0)
ELBOW_L = (388.0, 535.0)
WRIST_L = (428.0, 735.0)
HAND_L = (440.0, 820.0)

m_upper = poly_mask(ARM_UPPER, 1.2)
m_fore = poly_mask(ARM_FORE, 1.2)
arm_any = np.maximum(m_upper, m_fore)

# Torso / pants boundary on the left: anything right of it belongs to the body.
left_edge = np.where(ys < 600, 434.0, 452.0)
torso_side = (xs >= left_edge).astype(np.float32)

# ---------------------------------------------------------------- rebuild right side
# A: compressed mirror for the cheek hidden by the phone
src_face = np.maximum(AXIS_FACE - (xs - AXIS_FACE) / 0.42, 504.0)
face_A = remap_x(rgb, np.where(xs > AXIS_FACE, src_face, xs))
JAW = [(586, 146), (612, 144), (628, 147), (636, 165), (633, 192), (622, 220),
       (606, 244), (590, 258), (584, 258)]
m_jaw = poly_mask(JAW, 3.0) * (xs > AXIS_FACE - 2)

# B: plain mirror about torso centre for neck / trap / upper chest
src_body = AXIS_BODY - (xs - AXIS_BODY)
neck_B = remap_x(rgb, np.where(xs > AXIS_FACE, src_body, xs))
alpha_B = remap_x(alpha, np.where(xs > AXIS_FACE, src_body, xs))
# B must not contain the (not yet removed) left arm beyond the shoulder
left_arm_mirror = remap_x(arm_any * (1 - torso_side), np.where(xs > AXIS_FACE, src_body, xs))

def smooth(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# RGB blend weight for the mirrored neck/trap: soft on the left seam and at the bottom
wB = smooth(578, 606, xs) * (ys >= 196) * (1 - smooth(332, 356, ys))
wB = cv2.GaussianBlur(wB.astype(np.float32), (0, 0), 1.5)

rebuilt = rgb.copy()
rebuilt = rebuilt * (1 - wB[..., None]) + neck_B * wB[..., None]
rebuilt = rebuilt * (1 - m_jaw[..., None]) + face_A * m_jaw[..., None]

# Hard region that used to contain the phone, hand and raised right arm.
K = np.zeros_like(alpha)
K[150:196, 596:730] = 1
K[196:360, 590:830] = 1
K[360:586, 660:830] = 1
new_alpha = np.zeros_like(alpha)
new_alpha = np.maximum(new_alpha, m_jaw)
neckA = alpha_B * (1 - left_arm_mirror) * (ys >= 196)
new_alpha = np.maximum(new_alpha, neckA)
new_alpha = np.where((ys >= 300) & (xs < 658), 1.0, new_alpha)   # solid torso under old hand
new_alpha = np.where(ys >= 360, 0.0, new_alpha)                   # beside torso: empty
base_alpha = alpha * (1 - K) + new_alpha * K

# remove left arm (everything left of the torso edge), keep a static deltoid cap
cap_L = np.zeros((H, W), np.float32)
cv2.ellipse(cap_L, (392, 300), (58, 62), 0, 0, 360, 1.0, -1)
cap_L = cv2.GaussianBlur(cap_L, (0, 0), 6) * (ys < 400)
left_zone = (ys > 225) & (ys < 900)
base_alpha = np.where(left_zone, base_alpha * np.maximum(torso_side, cap_L), base_alpha)
inpaint_mask = ((arm_any > 0.3) & (torso_side > 0) & (cap_L < 0.5)).astype(np.uint8) * 255
inpaint_mask = cv2.dilate(inpaint_mask, np.ones((5, 5), np.uint8))
reb8 = np.clip(rebuilt, 0, 255).astype(np.uint8)
reb8 = cv2.inpaint(reb8, inpaint_mask, 9, cv2.INPAINT_TELEA)
# darken inpainted fabric towards the tank/pants black so no skin smears remain
fab = (inpaint_mask > 0)[..., None]
reb8 = np.where(fab, (reb8 * 0.25 + 12).astype(np.uint8), reb8)
rebuilt = reb8.astype(np.float32)

# torso alpha where the arm sat over it: solid body
base_alpha = np.where(inpaint_mask > 0, 1.0, base_alpha)
base_alpha = np.clip(base_alpha, 0, 1)

src_m = 2 * AXIS_BODY - xs
cap_R = remap_x(cap_L, src_m) * remap_x(alpha, src_m)
mir_rgb = np.dstack([remap_x(rgb[..., c], src_m) for c in range(3)])
rebuilt = rebuilt * (1 - cap_R[..., None]) + mir_rgb * cap_R[..., None]
base_alpha = np.maximum(base_alpha, cap_R)


def save_rgba(path, color, a):
    out = np.dstack([np.clip(color, 0, 255), np.clip(a, 0, 1) * 255]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(path)


save_rgba(os.path.join(OUT, "base.png"), rebuilt, base_alpha)

# ---------------------------------------------------------------- arm layers
orig8 = rgb
upper_a = alpha * m_upper
fore_a = alpha * m_fore
# drop the black pants pixels that sit between the fingers / beside the hand
luma = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
skin = np.clip((luma - 45) / 30, 0, 1)
skin = cv2.GaussianBlur(skin, (0, 0), 1.0)
fore_a = np.where((xs > 446) & (ys > 690), fore_a * skin, fore_a)
save_rgba(os.path.join(OUT, "upper_L.png"), orig8, upper_a)
save_rgba(os.path.join(OUT, "fore_L.png"), orig8, fore_a)


def mirror(arr):
    # mirror about AXIS_BODY: x' = 2*AXIS - x
    src = 2 * AXIS_BODY - xs
    if arr.ndim == 3:
        return np.dstack([remap_x(arr[..., c], src) for c in range(arr.shape[2])])
    return remap_x(arr, src)


save_rgba(os.path.join(OUT, "upper_R.png"), mirror(orig8), mirror(upper_a))
save_rgba(os.path.join(OUT, "fore_R.png"), mirror(orig8), mirror(fore_a))

# ---------------------------------------------------------------- muscle masks (left arm coords)
def ellipse_mask(cx, cy, rx, ry, ang=0, feather=10):
    m = np.zeros((H, W), np.float32)
    cv2.ellipse(m, (int(cx), int(cy)), (int(rx), int(ry)), ang, 0, 360, 1.0, -1)
    return cv2.GaussianBlur(m, (0, 0), feather)


biceps = ellipse_mask(406, 420, 26, 82, -4) * upper_a
triceps = ellipse_mask(352, 415, 20, 95, 3) * upper_a
forearm = ellipse_mask(410, 630, 30, 95, -14) * fore_a
for name, m in [("biceps", biceps), ("triceps", triceps), ("forearm", forearm)]:
    Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, f"mask_{name}_L.png"))
    Image.fromarray((np.clip(mirror(m), 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, f"mask_{name}_R.png"))


def mx(p):
    return (2 * AXIS_BODY - p[0], p[1])


rig = {
    "size": [W, H],
    "shoulder_L": SHOULDER_L, "elbow_L": ELBOW_L, "wrist_L": WRIST_L, "hand_L": HAND_L,
    "shoulder_R": mx(SHOULDER_L), "elbow_R": mx(ELBOW_L), "wrist_R": mx(WRIST_L), "hand_R": mx(HAND_L),
    "head": (560.0, 150.0), "chest": (545.0, 400.0), "feet_y": 1440.0,
}
with open(os.path.join(OUT, "rig.json"), "w") as f:
    json.dump(rig, f, indent=1)
print("rig built", W, H)
