# Student Focus Monitor
### AI-Powered Distraction Detection & Analysis System
> HNS Major Project | B.Tech CSE | Semester 6 | NSUT Delhi

An end-to-end student distraction monitoring system that detects attention loss using computer vision, logs it in real-time, visualizes it using R and Power BI, processes it at scale using Apache Spark, and deploys the entire pipeline inside Docker.

## Problem Statement
In modern educational institutions, monitoring student attention and engagement during classroom sessions remains a significant challenge. Traditional teaching methods provide no mechanism for teachers to quantitatively measure how focused students are during different types of sessions — whether theory lectures, problem-solving periods, or laboratory practicals. Research consistently shows that student attention drops significantly during long theory lectures, particularly after the first 20 minutes, yet institutions lack real-time data to act on this.
This project addresses the need for an automated, scalable student focus monitoring system by integrating concepts from all 5 units of the Hardware and Software Tools Workshop (HNS) into a single cohesive pipeline.
Specifically, the system:

|Unit|Purpose|
|----|-------|
|Unit I: Uses TinyML and embedded systems | to detect distraction at the edge using computer vision and an ESP32 microcontroller|
|Unit II/III: Generates visual reports | using R and Microsoft Power BI to present focus patterns to educators|
|Unit IV: Employs Apache Spark | to process distraction logs from multiple students simultaneously at scale|
|Unit V: Deploys the entire pipeline using Docker | to ensure portability and reproducibility across any machine|

The result is an end-to-end system that captures, logs, analyzes, visualizes, and deploys student attention data — demonstrating practical integration of edge computing, big data, visualization, and DevOps in a single real-world application.

---

## Project Structure

```
Major Project/
├── data/                        
│   └── distraction_log.csv
├── Dockerfile                   
├── docker-compose.yml           
├── analysis.py                  
├── dashboard.py                 
├── distraction_monitor.py       
├── analysis.R                
└── README.md
```

---

## Dataset

The distraction log dataset (598,001 rows, 2000 students) is available here:

📥 [Download distraction_log.csv](https://drive.google.com/drive/folders/1_epE49p34jNHiG9sM1cDqrDeqgN39zmC?usp=sharing)

After downloading, place it inside the `data/` folder:
```
Major Project/
└── data/
    └── distraction_log.csv
```

---

## Hardware Requirements (Unit I)

| Component | Specification | Quantity |
|-----------|--------------|----------|
| ESP32 DevKit v4 | 11th Gen, 8 CPUs | 1 |
| Webcam | Any USB webcam | 1 |
| Red LED | 5mm standard | 1 |
| Green LED | 5mm standard | 1 |
| Active Buzzer | 5V active buzzer | 1 |
| Resistors | 220Ω (for LEDs), 100Ω (for buzzer) | 3 |
| Breadboard | Full size | 1 |
| Jumper Wires | Male-to-male | As needed |
| USB Cable | USB-A to Micro-USB | 1 |

---

## Hardware Connections (ESP32 Wiring)

```
ESP32 Pin    →    Component
─────────────────────────────────────────
GPIO 5       →    Buzzer (+) via 100Ω resistor → GND
GPIO 19      →    Red LED (+) via 220Ω resistor → GND
GPIO 21      →    Green LED (+) via 220Ω resistor → GND
GPIO 2       →    Onboard LED (no wiring needed)
GND          →    Common GND for all components
USB          →    Laptop (power + serial communication)
```

**LED wiring note:** Long leg (+) of LED faces the resistor side, short leg (-) faces GND.

**Buzzer note:** Use an active buzzer — it beeps with just HIGH/LOW signal. Passive buzzers require PWM.

---

## Step 1 — Upload Arduino Code to ESP32

1. Download and install [Arduino IDE](https://www.arduino.cc/en/software)
2. Install ESP32 board support:
   - Open Arduino IDE → File → Preferences
   - Add this URL to "Additional Board Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Go to Tools → Board → Board Manager → search "esp32" → Install
3. Connect ESP32 to laptop via USB
4. Select the correct board and port:
   - Tools → Board → ESP32 Arduino → ESP32 Dev Module
   - Tools → Port → select your COM port (e.g. COM9)
5. Open `arduino_code.ino` (the Arduino file)
6. Click **Upload** (→ arrow button)
7. Wait for "Done uploading" message
8. The onboard LED (GPIO 2) will turn ON — ESP32 is ready and waiting

---

## Step 2 — Install Python Dependencies

Open PowerShell and run:

```powershell
pip install opencv-python pyserial pyautogui
```

---

## Step 3 — Run the Distraction Monitor (Unit I)

1. Make sure ESP32 is connected and Arduino code is uploaded
2. Check which COM port your ESP32 is on:
   - Device Manager → Ports (COM & LPT)
   - Update `PORT = "COM9"` in `distraction_monitor.py` to match
3. Check your webcam index — default is `cv2.VideoCapture(1)`, change to `0` if webcam not detected
4. Update your Student ID in `distraction_monitor.py`:
   ```python
   STUDENT_ID = "S001"  # change per student machine
   ```
5. Run the script:
   ```powershell
   python distraction_monitor.py
   ```
6. A window will open showing the webcam feed with FOCUSED/DISTRACTED status overlay
7. Data gets logged to `data/distraction_log.csv` every 2 seconds
8. Press `Q` to quit

**How it works:**
- Face not detected → DISTRACTED (NO_FACE)
- Face detected but no mouse movement for 60 seconds → DISTRACTED (PASSIVE)
- Face detected + mouse moving → FOCUSED
- ESP32 triggers buzzer + popup alert after sustained distraction

---

## Step 4 — Run R Visualization (Unit II/III)

1. Install [R](https://cran.r-project.org/) and [RStudio](https://posit.co/download/rstudio-desktop/)
2. Open `analysis.R` in RStudio
3. Run the install commands (first time only):
   ```r
   install.packages("ggplot2")
   install.packages("dplyr")
   ```
4. Update the CSV path in the script:
   ```r
   data <- read.csv("data/distraction_log.csv")
   ```
5. Click **Run All** or press Ctrl+Shift+Enter
6. A bar chart showing Focus vs Distraction by Hour will appear in the Plots panel

---

## Step 5 — Power BI Dashboard (Unit III)

1. Download and install [Power BI Desktop](https://powerbi.microsoft.com/desktop/)
2. Open Power BI → Get Data → Text/CSV → select `data/distraction_log.csv`
3. Click Load
4. Go to Transform Data:
   - Select Timestamp → change type to Date/Time
   - Select Distraction_Count → Whole Number
   - Click Close & Apply
5. Create a new column (Modeling → New Column):
   ```
   Hour = HOUR('distraction_log'[Timestamp])
   ```
6. Create measures (Modeling → New Measure):
   ```
   Total_Entries = COUNTROWS('distraction_log')
   Total_Distraction = CALCULATE(COUNTROWS('distraction_log'), 'distraction_log'[Status] = "DISTRACTED")
   Total_Focus = CALCULATE(COUNTROWS('distraction_log'), 'distraction_log'[Status] = "FOCUSED")
   ```
7. Add visuals: Clustered Bar Chart, Line Chart, Card visuals, Pie Chart

---

## Step 6 — Run Docker Dashboard (Unit IV + V)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Make sure Docker Desktop is running (whale icon in taskbar)
3. Make sure `data/distraction_log.csv` is in the project folder
4. Open PowerShell in the project folder and run:
   ```powershell
   docker-compose up --build
   ```
5. Wait for the build to complete (first time takes 3-5 minutes)
6. Open your browser and go to:
   ```
   http://localhost:5000
   ```
7. The dashboard will show:
   - KPI cards (Focused, Distracted, Focus Rate, Students Monitored)
   - Focus vs Distraction by Hour
   - Focus by Session Type
   - Focus Trend over the Day
   - Focus vs Distraction by Student Archetype
8. Click **Re-run Spark Analysis** to reprocess the dataset with latest data
9. To stop: press `Ctrl+C` in PowerShell, then run:
   ```powershell
   docker-compose down
   ```

---

## Technologies Used

| Unit | Technology |
|------|-----------|
| Unit I | Python, OpenCV, PySerial, PyAutoGUI, ESP32, Arduino IDE, Haar Cascade |
| Unit II | R, ggplot2, dplyr |
| Unit III | Microsoft Power BI, DAX |
| Unit IV | Apache Spark, PySpark, Parquet |
| Unit V | Docker, docker-compose, Flask, Plotly |

---

## Architecture

```
[Webcam + ESP32]          ← Unit I: Edge device, runs on host
        ↓
[distraction_log.csv]     ← Shared data backbone
      ↙        ↓
[R + Power BI]      [Docker Container]
 Unit II/III          ↙            ↘
 runs on host   [Spark - Unit IV]  [Flask - Unit V]
                processes CSV      serves dashboard
                saves Parquet      localhost:5000
```

---

## Team

| Name | Role |
|------|------|
| Sneha | Hardware, Firmware, TinyML, Docker, Spark |
| Aashna | R Visualization & Power BI Dashboard |

---
