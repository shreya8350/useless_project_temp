# DEAD PIXEL FORENSICS 🔬📱

> *"Because someone had to count the lines."*

A complete, functional, highly polished web application built for **Tinker Useless Project 3.0**.

**Dead Pixel Forensics** is an interactive Computer Vision-based forensic analytics dashboard that transforms broken-display images into a detailed dataset of geometric, color, spatial, and pixel-level abnormalities. It visualizes them through interactive charts and heatmaps, and generates intentionally useless but accurately derived metrics and reports.

---

## 🌟 Key Features

1. **Digital Forensic Dashboard**: Designed like a high-tech forensic lab dashboard featuring glassmorphism, dark mode aesthetics, dynamic animations, and interactive visualizations.
2. **Real Computer Vision Pipeline**:
   - **Line Detection & Classification**: Hough Line Transform & Contour analysis classify lines into Horizontal, Vertical, Diagonal, Curved, and Irregular.
   - **Line Measurements**: Calculates length, width, angle, brightness, intensity, screen percentage, center distance, nearest line proximity, and intersection count.
   - **Color Analysis**: Samples RGB/HSV color spaces across 12 distinct color categories.
   - **Pixel Cluster Analysis**: Detects dead/stuck pixel clusters, isolated pixels, and damage areas using Otsu thresholding, Canny edge detection, and morphological operations.
   - **3×3 Screen Region Analysis**: Divides the screen into 9 equal quadrants to map damage density, dominant colors, and line counts per zone.
   - **Curved & Parallel Line Analysis**: Fits curves, calculates curvature and turning points, and groups parallel lines into organized damage sets.
   - **Intersection Analysis**: Identifies multi-line intersection coordinates and angles ("The Intersection Crisis").
3. **Heatmaps & Image Overlays**:
   - Interactive overlay toggles: Original Image, Annotated Line Detection Overlay, Damage Mask Overlay.
   - Switchable heatmaps: Damage Heatmap, Line Density Heatmap, Intersection Heatmap, Pixel Cluster Heatmap.
4. **Rich Data Visualization**:
   - 4 Interactive Donut/Pie Charts (Orientation, Color Distribution, Damage vs Unaffected Area, Pixel Cluster Types).
   - 8 Interactive Bar Charts (Lines by Color, Total Length by Color, Damage by Region, Orientation, Cluster Sizes, Top 10 Longest, Top 10 Thickest, Intersections by Region).
   - 4 Histograms (Line Width, Line Length, Angle, Pixel Intensity).
   - 3 Scatter Plots (Length vs Width, Length vs Brightness, Width vs Intensity).
5. **Custom Useless Metrics & Gamification**:
   - **Uselessness Score™ (0–100)**: Deterministic weighted metric based on line density, color diversity, orientation entropy, intersection density, curvature, cluster complexity, and spatial irregularity.
   - **Display Chaos Index™ (0–100)**: Quantifies structural randomness and complexity.
   - **Symmetry Score (0–100%)**: Measures horizontal, vertical, and radial symmetry of damage.
   - **Breakage Level™ (1–10)**: Categorizes severity with entertaining descriptors ("1 — Barely broken", "8 — Extremely broken", "10 — Congratulations").
   - **Display Personality**: Algorithmically classifies screen into profiles like *THE BARCODE*, *THE RAINBOW*, *THE SPIDER*, *THE GRID*, *THE CHAOS MONSTER*, *THE MINIMALIST*, or *THE ABSTRACT ARTIST*.
   - **The Useless Awards™**: Awards trophies for 🏆 Longest Line, 🏆 Thickest Line, 🏆 Thinnest Line, 🏆 Loneliest Line, 🏆 Most Social Line, 🏆 Most Dramatic Color, 🏆 Most Popular Angle, 🏆 Most Damaged Zone, 🏆 Most Chaotic Region.
   - **Interactive Line Explorer**: Sortable, searchable forensic table linked directly to image overlay highlights and zoom stats.
   - **Line Social Network**: Node-graph representation ("THE SOCIAL LIFE OF BROKEN PIXELS").
   - **Display DNA™**: Generates a unique visual fingerprint ID (e.g., `DPF-8A42-91`) and barcode graphic.
6. **Uselessness Battle (Compare Mode)**: Compare two broken display images side-by-side to objectively crown the more useless display.
7. **Downloadable Forensic PDF Report**: Automatically generates a complete multi-page PDF forensic report using ReportLab.
8. **Demo Mode**: Built-in sample broken screens for instant evaluation during competition judging.

---

## 🏗️ Architecture & Project Structure

```
dead-pixel-forensics/
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Animated counters, gauges, DNA, awards, explorer, network
│   │   ├── pages/            # LandingPage, UploadPage, DashboardPage, ComparePage
│   │   ├── charts/           # Donut, Bar, Histogram, Scatter charts (Recharts)
│   │   ├── overlays/         # Image overlays, heatmaps, 3x3 region grid
│   │   ├── services/         # API client & endpoints
│   │   ├── utils/            # Formatting helpers
│   │   ├── App.jsx           # Routing & global theme
│   │   └── App.css           # Glassmorphism & forensic styling
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── main.py               # FastAPI application entrypoint
│   ├── requirements.txt      # Python dependencies
│   │
│   ├── api/
│   │   ├── analyzer.py       # Main CV orchestration & data assembly
│   │   └── routes.py         # REST API endpoints (/analyze, /compare, /report, /demo)
│   │
│   ├── cv/                   # Modular OpenCV & Computer Vision engines
│   │   ├── preprocessing.py
│   │   ├── line_detection.py
│   │   ├── color_analysis.py
│   │   ├── pixel_analysis.py
│   │   ├── region_analysis.py
│   │   ├── intersection_analysis.py
│   │   ├── curve_analysis.py
│   │   └── spatial_analysis.py
│   │
│   ├── metrics/              # Custom deterministic metric engines
│   │   ├── uselessness.py
│   │   ├── chaos.py
│   │   ├── symmetry.py
│   │   ├── personality.py
│   │   ├── awards.py
│   │   └── display_dna.py
│   │
│   ├── reports/
│   │   └── report_generator.py # ReportLab PDF generator
│   │
│   └── utils/                # Base64, Math, Image helpers
│
├── demo_images/              # Built-in synthetic demo samples
├── uploads/                  # Temporary image uploads
├── outputs/                  # Analysis JSON & PDF reports
├── run_backend.bat           # Windows quick-start script for backend
├── run_frontend.bat          # Windows quick-start script for frontend
└── README.md
```

---

## 🛠️ Technology Stack

- **Frontend**: React 19 + Vite, Framer Motion, Recharts, Axios, CSS3 (Glassmorphism & Dark Mode).
- **Backend**: Python 3.13 + FastAPI, Uvicorn, Pydantic.
- **Computer Vision & Processing**: OpenCV (`opencv-python-headless`), NumPy, SciPy, Pandas, Pillow.
- **Reporting & Visualization**: ReportLab (PDF), Plotly, Matplotlib.

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### Option A: Using Quick-Start Scripts (Windows)

1. **Start Backend**:
   Double click `run_backend.bat` or run:
   ```cmd
   run_backend.bat
   ```
   *The backend starts at `http://127.0.0.1:8000`.*

2. **Start Frontend**:
   Double click `run_frontend.bat` or run:
   ```cmd
   run_frontend.bat
   ```
   *The frontend starts at `http://localhost:5173` (or 5174).*

---

### Option B: Manual Command Setup

#### 1. Setup Backend

```bash
# Navigate to project root
cd uselessproject

# Activate virtual environment
venv\Scripts\activate

# Install requirements
pip install -r backend/requirements.txt

# Launch FastAPI server
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. Setup Frontend

```bash
# Navigate to frontend folder
cd frontend

# Install node packages (if needed)
npm install

# Launch Vite dev server
npm run dev
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | API health check |
| `POST` | `/api/analyze` | Upload image & return complete forensic analysis JSON |
| `POST` | `/api/compare` | Upload two images and return side-by-side comparison & winner |
| `GET` | `/api/analysis/{id}` | Retrieve cached analysis JSON by ID |
| `GET` | `/api/report/{id}` | Generate and download forensic PDF report |
| `GET` | `/api/demo-list` | List available demo sample images |
| `GET` | `/api/demo/{sample}` | Run instant analysis on a demo sample image |

---

## 📐 Custom Metric Formulas

### Uselessness Score™ (0–100)
$$\text{Uselessness Score} = \text{Clamp}\left( \sum_{i=1}^8 w_i \cdot C_i, 0, 100 \right)$$
Where components $C_i$ represent normalized:
- Line Density ($20\%$)
- Color Diversity ($15\%$)
- Orientation Entropy ($15\%$)
- Intersection Density ($15\%$)
- Damage Complexity ($15\%$)
- Curvature ($10\%$)
- Cluster Complexity ($5\%$)
- Spatial Irregularity ($5\%$)

---

## ⚠️ Scientific Disclaimer

> **Image-Based Analysis Disclaimer**: This application analyzes visual pixel patterns, contrast anomalies, and geometric lines present within uploaded digital images. It is an image-based visual analysis tool and does not replace hardware diagnostic tools.

---

*Dead Pixel Forensics — Built for Tinker Useless Project 3.0.*
