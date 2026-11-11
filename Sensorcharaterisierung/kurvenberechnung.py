import numpy as np
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

# =====================================================
# Parameter (anpassen!)
# =====================================================
DATA_DIR   = Path("Bilder/1.3 16 Aufnahmen/Hell")   # messdaten/<t_exp_us>/A.png, B.png
DARK_DIR   = DATA_DIR / "dark"   # messdaten/dark/A.png, B.png (Kamera abgedeckt)

WAVELENGTH = 640e-9              # m
PIXEL_AREA = (4.8e-6) ** 2       # m^2 -> Pixelgröße aus Datenblatt eintragen
IRRADIANCE = 1e-3                # W/m^2 -> gemessene Bestrahlungsstärke am Sensor
                                 # (ohne Messung: kein absolutes mu_p möglich!)

BIT_DEPTH  = 12
MAX_DN     = 2**BIT_DEPTH - 1    # 4095
SATURATION = 0.95 * MAX_DN       # Auswertegrenze
SHIFT      = 0                   # 4, falls 12 Bit MSB-aligned in 16 Bit gespeichert sind
LINEAR_FRACTION = 0.7            # Fit nur bis 70 % des Signalbereichs

h = 6.62607015e-34
c = 299792458.0
E_PHOTON = h * c / WAVELENGTH    # J


# =====================================================
# Hilfsfunktionen
# =====================================================
def load_gray(path, shift=SHIFT):
    """Mono12-Bild laden (16-Bit-PNG/TIFF), Rückgabe als float64 in DN."""
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(path)
    if img.ndim == 3:
        img = img[:, :, 0]
    img = img.astype(np.float64)
    if shift:
        img /= 2**shift
    return img


def mean_and_var(yA, yB):
    """mu_y und zeitliche Varianz sigma_y^2 aus einem Bildpaar (Formeln aus dem Skript)."""
    mu = np.mean(yA + yB) / 2.0
    var = np.mean((yA - yB) ** 2) / 2.0
    return mu, var


def find_image(folder, name):
    """Findet A.* bzw. B.* unabhängig von der Dateiendung."""
    matches = sorted(folder.glob(f"{name}.*"))
    if not matches:
        raise FileNotFoundError(f"{name}.* nicht in {folder}")
    return matches[0]


# =====================================================
# Dunkelsignal
# =====================================================
dA = load_gray(find_image(DARK_DIR, "A"))
dB = load_gray(find_image(DARK_DIR, "B"))
mu_dark, var_dark = mean_and_var(dA, dB)
print(f"Dunkelwert: {mu_dark:.2f} DN, Dunkelrauschen: {np.sqrt(var_dark):.3f} DN")

# =====================================================
# Messungen bei verschiedenen Belichtungszeiten
# =====================================================
t_exp, mu_y, var_y = [], [], []

folders = sorted(
    [p for p in DATA_DIR.iterdir() if p.is_dir() and p.name.isdigit()],
    key=lambda p: int(p.name),
)
if not folders:
    raise RuntimeError(f"Keine Belichtungsordner in {DATA_DIR} gefunden")

for folder in folders:
    t_us = int(folder.name)
    yA = load_gray(find_image(folder, "A"))
    yB = load_gray(find_image(folder, "B"))
    mu, var = mean_and_var(yA, yB)
    t_exp.append(t_us * 1e-6)    # s
    mu_y.append(mu)
    var_y.append(var)

t_exp = np.array(t_exp)
mu_y = np.array(mu_y)
var_y = np.array(var_y)

# Dunkelkorrektur
signal = mu_y - mu_dark                 # DN
noise = var_y - var_dark                # DN^2

# Photonen pro Pixel: mu_p = A * E * t / (h*c/lambda)
mu_p = PIXEL_AREA * IRRADIANCE * t_exp / E_PHOTON

# Sättigung ausschließen
valid = mu_y < SATURATION
print(f"Max. mittlerer Grauwert: {mu_y.max():.1f} DN von {MAX_DN}")
print(f"{valid.sum()} von {len(valid)} Punkten unterhalb der Sättigungsgrenze")

# =====================================================
# Fits im linearen Bereich
# =====================================================
lin = valid & (signal < LINEAR_FRACTION * (SATURATION - mu_dark))
if lin.sum() < 3:
    raise RuntimeError("Zu wenige Punkte im linearen Bereich für den Fit")

# Sensitivität: signal = R * mu_p + off   (R = K*eta)
R, off = np.polyfit(mu_p[lin], signal[lin], 1)

# PTC: noise = K * signal + off_n   (K = Systemverstärkung)
K, off_n = np.polyfit(signal[lin], noise[lin], 1)

eta = R / K
print(f"\nSystemverstärkung K   = {K:.4f} DN/e-")
print(f"Responsivität K*eta   = {R:.3e} DN/Photon")
print(f"Quanteneffizienz eta  = {eta * 100:.1f} %")

# =====================================================
# Plots
# =====================================================
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))

ax[0].plot(mu_p[valid], signal[valid], "o", label="Messung")
xs = np.linspace(0, mu_p[lin].max(), 100)
ax[0].plot(xs, R * xs + off, "-", label=rf"Fit: $K\cdot\eta$ = {R:.2e} DN/Photon")
ax[0].set_xlabel(r"$\mu_p$ (Photonen/Pixel)")
ax[0].set_ylabel(r"$\mu_y - \mu_{y,dark}$ (DN)")
ax[0].set_title("Sensitivitätskurve")
ax[0].grid(True)
ax[0].legend()

ax[1].plot(signal[valid], noise[valid], "o", label="Messung")
xs = np.linspace(0, signal[lin].max(), 100)
ax[1].plot(xs, K * xs + off_n, "-", label=rf"Fit: $K$ = {K:.3f} DN/e$^-$")
ax[1].set_xlabel(r"$\mu_y - \mu_{y,dark}$ (DN)")
ax[1].set_ylabel(r"$\sigma_y^2 - \sigma_{y,dark}^2$ (DN$^2$)")
ax[1].set_title("Photonentransferkurve")
ax[1].grid(True)
ax[1].legend()

plt.tight_layout()
plt.savefig("kurven.png", dpi=200)
plt.show()