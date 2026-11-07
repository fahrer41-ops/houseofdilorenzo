#!/usr/bin/env python3
"""
Viking Film Look - 3D LUT generator (.cube, 33x33x33)

Designed for Rec.709 / sRGB display-referred input (apply after your
camera-to-709 transform, not on raw log footage).

Grade recipe
  1. Global desaturation to a gritty, earthy low-mid chroma level.
  2. Shadows split-toned: neutral/cool shadows -> cold muted blue-cyan,
     warm shadows (wood, leather, fire-lit) -> mahogany.
  3. Greens and yellows desaturated hard for bleak, overcast landscapes.
  4. Skin tone zone (orange hues, mids) protected: saturation and tonal
     contrast retained so faces don't go grey.
  5. Highlights softened with a shoulder roll-off; blacks deepened with a
     crushed toe and a mild S-curve for a heavy, moody image.
"""
import numpy as np

SIZE = 33
OUT = "viking_film_look_33.cube"


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def hue_bump(h, center, width):
    """Smooth 0..1 weight around a hue center (degrees), width = half-width."""
    d = np.abs(((h - center + 180.0) % 360.0) - 180.0)
    return 1.0 - smoothstep(0.0, width, d)


def rgb_to_hsv(r, g, b):
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    c = mx - mn
    h = np.zeros_like(r)
    safe = c > 1e-6
    rc = np.where(safe, (mx - r) / np.where(safe, c, 1), 0)
    gc = np.where(safe, (mx - g) / np.where(safe, c, 1), 0)
    bc = np.where(safe, (mx - b) / np.where(safe, c, 1), 0)
    h = np.where(mx == r, bc - gc, np.where(mx == g, 2.0 + rc - bc, 4.0 + gc - rc))
    h = np.where(safe, (h / 6.0) % 1.0, 0.0) * 360.0
    s = np.where(mx > 1e-6, c / np.maximum(mx, 1e-6), 0.0)
    return h, s, mx


def luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def tone_curve(y):
    """Deep blacks, mild S contrast, soft highlight shoulder (0..1 in/out)."""
    # 1. toe: sink the bottom ~2% to true black, then a shadow-darkening gamma
    y = np.clip((y - 0.018) / (1.0 - 0.018), 0.0, 1.0)
    y = y ** 1.12
    # 2. gentle smooth S-curve for midtone bite (zero at 0, 0.5 and 1)
    y = y + 0.15 * 4.0 * y * (1.0 - y) * (y - 0.5)
    y = np.clip(y, 0.0, 1.0)
    # 3. soft shoulder: tanh roll-off above the knee, peak white ~0.94
    knee = 0.70
    peak = 0.995
    rng = peak - knee
    hi = y > knee
    y = np.where(hi, knee + rng * np.tanh((y - knee) / rng * 1.2), y)
    return y


def grade(r, g, b):
    r, g, b = [np.clip(x, 0, 1) for x in (r, g, b)]
    h, s, v = rgb_to_hsv(r, g, b)
    y_in = luma(r, g, b)

    # ---- tonal shaping (hue-preserving, ratio based) -------------------
    # tone-map on a luma/max blend so saturated reds and blues keep their
    # brightness instead of collapsing with pure luma ratios
    norm = 0.5 * y_in + 0.5 * v
    n_out = tone_curve(norm)
    ratio = np.where(norm > 1e-5, n_out / np.maximum(norm, 1e-5), 0.0)
    r, g, b = [np.clip(x * ratio, 0, 1) for x in (r, g, b)]

    # ---- hue weights -----------------------------------------------------
    w_skin = hue_bump(h, 28.0, 22.0)       # oranges / skin
    w_red = hue_bump(h, 2.0, 18.0)         # reds (blood, banners, fire core)
    w_yellow = hue_bump(h, 58.0, 18.0)     # yellows
    w_green = hue_bump(h, 112.0, 48.0)     # greens (grass, moss, foliage)
    w_cyan = hue_bump(h, 195.0, 30.0)
    w_blue = hue_bump(h, 232.0, 30.0)
    w_mag = hue_bump(h, 300.0, 35.0)

    # ---- saturation map --------------------------------------------------
    sat = 0.70 * np.ones_like(h)                       # global earthy base
    sat = sat + w_skin * (0.93 - 0.70)                 # protect skin
    sat = sat + w_red * (0.80 - 0.70)
    sat = sat - w_yellow * (0.70 - 0.48)               # bleak yellows
    sat = sat - w_green * (0.70 - 0.42)                # bleak greens
    sat = sat + w_cyan * (0.74 - 0.70)
    sat = sat + w_blue * (0.76 - 0.70)
    sat = sat - w_mag * (0.70 - 0.60)
    # skin only protected in the mids; very bright or very dark skin
    # zone falls back toward the global level
    y = luma(r, g, b)
    mid_w = smoothstep(0.08, 0.30, y) * (1.0 - smoothstep(0.65, 0.92, y))
    sat = sat - w_skin * (1.0 - mid_w) * 0.12
    # highlights lose a little chroma (softened, airy top end)
    hi_w = smoothstep(0.62, 1.0, y)
    sat = sat * (1.0 - 0.22 * hi_w)
    # deep shadows lose chroma too (muted, heavy)
    lo_w = 1.0 - smoothstep(0.0, 0.22, y)
    sat = sat * (1.0 - 0.18 * lo_w)

    r = y + (r - y) * sat
    g = y + (g - y) * sat
    b = y + (b - y) * sat

    # ---- shadow split tone -----------------------------------------------
    y = luma(r, g, b)
    sh_w = (1.0 - smoothstep(0.02, 0.48, y)) ** 1.4 * smoothstep(0.0, 0.025, y)
    warm_w = np.clip(w_skin + w_red + 0.5 * w_yellow, 0, 1) * smoothstep(0.08, 0.35, s)
    cool_w = 1.0 - warm_w
    # cold muted blue/cyan for neutral and cool shadows
    r = r + sh_w * cool_w * (-0.017)
    g = g + sh_w * cool_w * (+0.003)
    b = b + sh_w * cool_w * (+0.031)
    # mahogany for warm shadows (desaturated red-brown)
    r = r + sh_w * warm_w * (+0.016)
    g = g + sh_w * warm_w * (-0.004)
    b = b + sh_w * warm_w * (-0.016)
    # skin in the shadow zone is protected from the cold cast
    r = r + sh_w * w_skin * mid_w * (+0.012)
    b = b + sh_w * w_skin * mid_w * (-0.016)

    # ---- highlight bias: slightly cool-neutral, overcast sky feel ---------
    r = r + hi_w * (-0.006)
    b = b + hi_w * (+0.004)

    # ---- skin texture contrast: micro-boost local contrast in skin mids --
    y2 = luma(r, g, b)
    skin_c = w_skin * mid_w * 0.10
    y_boost = 0.40 + (y2 - 0.40) * (1.0 + skin_c)
    ratio2 = np.where(y2 > 1e-5, y_boost / np.maximum(y2, 1e-5), 1.0)
    r, g, b = r * ratio2, g * ratio2, b * ratio2

    return [np.clip(x, 0.0, 1.0) for x in (r, g, b)]


def main():
    n = SIZE
    idx = np.arange(n) / (n - 1)
    # .cube ordering: red varies fastest, then green, then blue
    bb, gg, rr = np.meshgrid(idx, idx, idx, indexing="ij")
    r, g, b = grade(rr.ravel(), gg.ravel(), bb.ravel())
    with open(OUT, "w") as f:
        f.write(f"LUT_3D_SIZE {n}\n")
        f.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        f.write("DOMAIN_MAX 1.0 1.0 1.0\n")
        for i in range(n ** 3):
            f.write(f"{r[i]:.6f} {g[i]:.6f} {b[i]:.6f}\n")
    print(f"wrote {OUT}: {n ** 3} entries")


if __name__ == "__main__":
    main()
