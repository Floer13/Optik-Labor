# Sensorcharakterisierung

Stand: 11.11.2026
aktualisiert: 11.11.2026

Pfad: `\\Laboraufgaben\1_franz_char_radiom.pdf`  

## Inhaltsverzeichnis
- [Sensorcharakterisierung](#sensorcharakterisierung)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Versuchsaufbau](#versuchsaufbau)
  - [Messdaten](#messdaten)
  - [Aufgabe 1](#aufgabe-1)
    - [1.2 Berechnung der mittleren Anzahl der einfallender Photonen $\\mu\_p$](#12-berechnung-der-mittleren-anzahl-der-einfallender-photonen-mu_p)
    - [1.3 Aufnahme von Hell-/Dunkelbilder für 12 Belichtungszeiten](#13-aufnahme-von-hell-dunkelbilder-für-12-belichtungszeiten)
    - [1.4 Photonentransfermethode - Plot der Graphen](#14-photonentransfermethode---plot-der-graphen)
    - [1.5 Interpretation der Plots](#15-interpretation-der-plots)
  - [Aufgabe 2](#aufgabe-2)
    - [2.1 Bestimmung der SNR-Kurve](#21-bestimmung-der-snr-kurve)
    - [2.2 Sättigungspunkt und nutzbare Bestrahlungsstärke](#22-sättigungspunkt-und-nutzbare-bestrahlungsstärke)
    - [2.3 Dynamik der Kamera bestimmen](#23-dynamik-der-kamera-bestimmen)
  - [Aufgabe 3](#aufgabe-3)
  - [Aufgabe 4](#aufgabe-4)

---

## Versuchsaufbau
 <img src="Bilder/aufbau1.jpg" height="400" > <img src="Bilder/aufbau2.jpg" height="400" >


**Wichtig**  
    alle Automatikeinstellungen in IDS Peak Cockpit müssen abgeschaltet werden!  
    Verstärkungen auf 1 setzen, BayerRG12 als Quelle, RGB12 als Ziel  
    Die Ergebnisse vom 11.11.2026 sind alle direkt als Grauwertbilder durch die Kamera entwickelt werden (Mono12 als Ziel). Das Ergebnis mit diesen Daten wird vermutlich vom Ergebnis mit Farbbildern und nachträglicher Grauwertberechnung durch python und opencv mehr oder weniger deutlich abweichen. So oder so ist das Ergebnis numerisch berechnet und bildet die Realität nur eingeschränkt ab. Am besten VOR der Entwicklung der Messreihe abwägen, welche Abweichungen akzeptabel oder überhaupt relevant sind.


---

## Messdaten
 * Wellenlänge  = 640 [nm] (Annahme!)
 * Sensordiagonale = 19,3 [mm]
 * Pixelanzahl = $24,47 * 10^6$ []
 * Pixelfläche = 14,599 x 12,626 [$mm^2$] * $10^-6$ [$m^2$]  
 * Sensorentfernung zu Papier &asymp; 25 [cm] (Annahme!)  
 * Bestrahlungsstärke E = 0,33 [$\frac{W}{m^2}$]
 * Pixelfläche A = 0,000184326974 [$m^2$] &asymp; 0,000184 [$m^2$]
  
## Aufgabe 1

### 1.2 Berechnung der mittleren Anzahl der einfallender Photonen $\mu_p$
 * Belichtungszeit = 15 [ms] / 1000 = $15 * 10^{-3}$ [s] 

 <img src="Bilder/1.2_einfallendephotonen_image2d.png" width="400" >  


 $\mu_p = 5.034 \cdot 10^{24} A \cdot E \cdot t_{exp} = 8,907859076313599 * 10^{22} \approx 8,908 *10^{22}$  

 Rechnungen `\\rechnung.py`

---

### 1.3 Aufnahme von Hell-/Dunkelbilder für 12 Belichtungszeiten  

 gewählte Belichtungszeiten:
 * 0.1 ms, 9 ms, 17 ms, 25 ms, 34 ms, 42 ms, 50 ms, 55 ms, 60 ms, 65 ms, 70 ms, 100 ms
 * je zwei Hell- und zwei Dunkelbilder

---
### 1.4 Photonentransfermethode - Plot der Graphen

 Graphen der Sensitivitätskurve und Photonentransferkurve
 [HIER EINSETZEN!]

---
### 1.5 Interpretation der Plots
 Für die folgenden Werte müssen die Kurven aus [1.4](#14)  ausgewertet und interpretiert werden. Näheres steht in den Vorlesungsunterlagen von Herrn Franz.  
 * Responsivität $R$ =
 * Kameravestärkung $K$ = 
 * Quanteneffizienz $\eta$ = 
 * Dunkelsignal $\sigma^{2}_{d}$ = 

---

## Aufgabe 2
 
### 2.1 Bestimmung der SNR-Kurve

doppelt logarithmisches Diagramm

Rechnung `Pfad des Scripts hier einfügen`

---

### 2.2 Sättigungspunkt und nutzbare Bestrahlungsstärke
 Einzeichen des Sättigungspunkts, kleinster nutzbarer Bestrahlungsstärke, SNR-Kurve eines idealen Sensors, theoretische SNR-Kurve der Daten aus [Aufgabe 1](#aufgabe-1)

---

### 2.3 Dynamik der Kamera bestimmen

---

## Aufgabe 3

## Aufgabe 4