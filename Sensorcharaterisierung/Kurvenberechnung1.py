from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt

# ==========================================
# 1. KONFIGURATION & PARAMETER
# ==========================================
base_dir = Path(r"C:\Users\timah\Documents\Optik Labor\Bilder")

# Sensor- und Versuchsspezifische Parameter (Sony IMX540 / IDS U3-31R0CP-C-HQ)
pixel_pitch = 2.74e-6  # Pixelgröße in Metern (2.74 µm)
A_pixel = pixel_pitch ** 2  # Pixelfläche A in m^2
wavelength = 630e-9  # Wellenlänge der LED in Metern (630 nm)
h = 6.62607015e-34  # Planck-Wirkungsquantum
c = 299792458  # Lichtgeschwindigkeit

# Bestrahlungsstärke E [W/m^2] für jede Belichtungsstufe (bitte an Ihre Messungen anpassen)
E_messungen = {
    "05": 0.1,  
    "10": 0.5,  
    "20": 1.0   
}

# ==========================================
# 2. BILDER EINLESEN & AUSWERTEN
# ==========================================
ergebnisse = []

for zustand in ["hell", "dunkel"]:
    zustand_dir = base_dir / zustand
    if not zustand_dir.exists():
        print(f"Ordner nicht gefunden: {zustand_dir}")
        continue

    # Alle Unterordner (Belichtungszeiten) sortiert durchgehen
    ordner_liste = sorted([d for d in zustand_dir.iterdir() if d.is_dir()])

    for folder in ordner_liste:
        belichtungszeit_name = folder.name
        
        # Bilder laden (mindestens 2 Bilder pro Ordner: A und B)
        bilder = sorted(list(folder.glob("*.png")) + list(folder.glob("*.tif*")) + list(folder.glob("*.raw")))
        if len(bilder) < 2:
            print(f"Warnung: Weniger als 2 Bilder in {folder.name} gefunden.")
            continue
            
        # IMREAD_UNCHANGED behält die volle Bittiefe bei
        img_A = cv2.imread(str(bilder[0]), cv2.IMREAD_UNCHANGED)
        img_B = cv2.imread(str(bilder[1]), cv2.IMREAD_UNCHANGED)
        
        if img_A is None or img_B is None:
            print(f"Fehler beim Laden der Bilder in: {folder.name}")
            continue

        # Extraktion der Rot-Pixel (Bayer-Pattern: Start bei [0,0])
        red_A = img_A[0::2, 0::2].astype(np.float64)
        red_B = img_B[0::2, 0::2].astype(np.float64)

        # Mittelwert der Grauwerte (mit ravel() zur Vermeidung von Array-Formfehlern)
        mu_raw = np.mean(np.concatenate([red_A.ravel(), red_B.ravel()]))
        
        # Zeitliche Varianz nach EMVA 1288: sigma^2 = 0.5 * Var(A - B)
        diff = red_A - red_B
        sigma_sq = 0.5 * np.var(diff.ravel(), ddof=1)

        ergebnisse.append({
            "zustand": zustand,
            "folder": belichtungszeit_name,
            "mu": mu_raw,
            "sigma_sq": sigma_sq
        })

print(f"\nErfolgreich {len(ergebnisse)} Datensätze verarbeitet.")

# ==========================================
# 3. DATEN AUFBEREITEN & BERECHNUNGEN
# ==========================================
hell_daten = sorted([d for d in ergebnisse if d["zustand"] == "hell"], key=lambda x: x["folder"])
dunkel_daten = sorted([d for d in ergebnisse if d["zustand"] == "dunkel"], key=lambda x: x["folder"])

if len(hell_daten) > 0:
    # Mittelwert des Dunkelsignals und der Dunkelvarianz
    mu_dark = np.mean([d["mu"] for d in dunkel_daten])
    sigma_dark_sq = np.mean([d["sigma_sq"] for d in dunkel_daten])

    mu_y_list = []
    sigma_y_sq_list = []
    mu_p_list = []

    for h_item, d_item in zip(hell_daten, dunkel_daten):
        # Bereinigter Grauwert & bereinigte Varianz
        mu_y_cleaned = h_item["mu"] - mu_dark
        sigma_y_cleaned_sq = h_item["sigma_sq"] - sigma_dark_sq
        
        mu_y_list.append(mu_y_cleaned)
        sigma_y_sq_list.append(sigma_y_cleaned_sq)
        
        # Belichtungszeit basierend auf Ordnernamen zuordnen (05=0.5ms, 10=10ms, 20=20ms)
        folder_name = h_item["folder"]
        if folder_name == "05":
            t_exp_ms = 0.5
        elif folder_name == "10":
            t_exp_ms = 10.0
        elif folder_name == "20":
            t_exp_ms = 20.0
        else:
            clean_name = folder_name.lower().replace("ms", "").replace("_", ".").strip()
            t_exp_ms = float(clean_name)
            
        t_exp = t_exp_ms / 1000.0  # Umrechnung von Millisekunden in Sekunden
        
        # Bestrahlungsstärke E holen
        E = E_messungen.get(h_item["folder"], 0.0)
        
        # Photonen pro Pixel berechnen
        mu_p = (A_pixel * E * t_exp) / (h * c / wavelength)
        mu_p_list.append(mu_p)

    mu_y = np.array(mu_y_list)
    sigma_y_sq = np.array(sigma_y_sq_list)
    mu_p = np.array(mu_p_list)

    # ==========================================
    # 4. SÄTTIGUNGSPUNKT & LINEARE REGRESSION
    # ==========================================
    sat_index = np.argmax(sigma_y_sq)
    sat_grauwert = mu_y[sat_index]
    print(f"Sättigungspunkt erkannt bei Grauwert: {sat_grauwert:.2f}")

    # Linearen Bereich eingrenzen (< 70% der Sättigung)
    linear_mask = mu_y < (0.7 * sat_grauwert)
    
    # Fallback, falls Maske durch wenige Testpunkte zu strikt ist
    if not np.any(linear_mask):
        linear_mask = np.ones_like(mu_y, dtype=bool)

    mu_y_lin = mu_y[linear_mask]
    sigma_y_sq_lin = sigma_y_sq[linear_mask]
    mu_p_lin = mu_p[linear_mask]

    # A) Photonentransferkurve: Steigung = Kameraverstärkung K
    K, c_ptc = np.polyfit(mu_y_lin, sigma_y_sq_lin, 1)

    # B) Sensitivitätskurve: Steigung = Responsivität R
    R, c_sens = np.polyfit(mu_p_lin, mu_y_lin, 1)

    # Quanteneffizienz eta = R / K
    eta = R / K if K != 0 else 0

    print("\n--- ERGEBNISSE DER EMVA 1288 AUSWERTUNG ---")
    print(f"Kameraverstärkung K: {K:.4f}")
    print(f"Responsivität R: {R:.4f} DN/Photon")
    print(f"Quanteneffizienz eta: {eta * 100:.2f} %")
    print(f"Dunkelrauschen (sigma_d^2): {sigma_dark_sq:.4f}")

    # ==========================================
    # 5. DIAGRAMME PLOTTEN
    # ==========================================
    plt.figure(figsize=(12, 5))

    # Photonentransferkurve
    plt.subplot(1, 2, 1)
    plt.plot(mu_y, sigma_y_sq, 'bo', label='Messpunkte')
    plt.plot(mu_y_lin, K * mu_y_lin + c_ptc, 'r-', label=f'Linear Fit (K={K:.3f})')
    plt.axvline(sat_grauwert, color='gray', linestyle='--', label='Sättigung')
    plt.xlabel(r'Bereinigter Grauwert $\mu_y - \mu_{y,dark}$')
    plt.ylabel(r'Bereinigte Varianz $\sigma_y^2 - \sigma_{y,dark}^2$')
    plt.title('Photonentransferkurve')
    plt.legend()
    plt.grid(True)

    # Sensitivitätskurve
    plt.subplot(1, 2, 2)
    plt.plot(mu_p, mu_y, 'go', label='Messpunkte')
    plt.plot(mu_p_lin, R * mu_p_lin + c_sens, 'r-', label=f'Linear Fit (R={R:.3f})')
    plt.xlabel(r'Einfallende Photonen $\mu_p$ [Photonen/Pixel]')
    plt.ylabel(r'Bereinigter Grauwert $\mu_y - \mu_{y,dark}$')
    plt.title('Sensitivitätskurve')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
else:
    print("Keine Hell-Daten gefunden. Bitte Ordnerstruktur überprüfen.")