# ✦ STYLEVERSE | AI-Powered Smart Wardrobe & Outfit Stylist

**STYLEVERSE** is a production-grade fashion intelligence platform combining facial colorimetry, deep vision-language representations, and multi-factor outfit compatibility modeling to curate harmonious, personalized looks.

---

## 🌟 Key Architecture & AI Modules

### 1. 🧬 Surgical Facial Landmark & Undertone Extraction
* **Google MediaPipe Face Mesh:** Uses 468 dense 3D facial landmarks to isolate anatomical skin sampling zones:
  * **Cheeks:** Left (`[117, 118, 101, 50, 123, 147]`) and Right (`[346, 347, 330, 280, 352, 376]`).
  * **Forehead:** (`[10, 67, 109, 103, 338, 297, 284]`).
* **Immunity:** Completely bypasses beards, facial hair, glasses, shadow boundaries, and tilted poses.
* **CIELAB Colorimetry:** Computes Individual Typology Angle (ITA) and undertone coordinates ($L^*, a^*, b^*$) to classify Warm, Cool, or Neutral undertones and generate 8-color seasonal palettes.

### 2. 👗 Zero-Shot Apparel Classification & Tagging
* **Hugging Face CLIP (`ViT-B/32`):** Zero-shot vision-language alignment across hierarchical fashion categories:
  * `top` (t-shirt, shirt, blouse, sweater, hoodie)
  * `bottom` (jeans, trousers, skirt, shorts)
  * `footwear` (sneakers, oxfords, boots, sandals)
  * `outerwear` (coat, trench coat, jacket, blazer)
  * `dress` (maxi dress, gown, wrap dress)
* Eliminates geometric and aspect-ratio guessing; handles folded, cropped, and flat-lay garments accurately.

### 3. 🎯 512D Fashion Latent Compatibility Engine ($S$)
Outfits are scored against the academic multi-factor compatibility formulation:
$$S = 0.35C + 0.25K + 0.20O + 0.10P + 0.10V$$

| Metric | Name | Description |
| :--- | :--- | :--- |
| **$C$** | **Color Harmony** | Delta-E ($\Delta E^*$) distance in CIELAB space against the user's seasonal palette. |
| **$K$** | **Style Cohesion** | Pairwise consistency across dress codes (Casual, Formal, Streetwear, Business). |
| **$O$** | **Occasion Match** | Semantic suitability against context (Daily, Date, Office, Party). |
| **$P$** | **Pattern Balance** | Contrast rule preventing conflicting heavy patterns (e.g., solid top + patterned bottom). |
| **$V$** | **Visual Compatibility** | Cosine similarity across 512-dimensional CLIP fashion embedding vectors. |

* **Grammar Constraints:** Strictly enforces 1-piece base looks (Dresses never pair with Bottoms) and 2-piece base looks (Top + Bottom + Footwear + Optional Outerwear).

### 4. ✂️ Studio Garment Cutout & Alpha-Masked Color Clustering
* **U2-Net ONNX (`rembg`):** Automatically isolates clothing items from backgrounds, generating transparent `RGBA` PNG cutouts.
* **Alpha-Masked K-Means:** Dominant color extraction clusters strictly over non-transparent pixels (`alpha > 64`), eliminating background wall, sky, or skin pollution.

---

## 🏗️ Repository Layout

```text
StyleVerse/
├── backend/
│   ├── app/
│   │   ├── routes/         # auth, wardrobe, outfits, skin, users, planner
│   │   ├── schemas/        # Pydantic v2 validation contracts
│   │   ├── utils/          # JWT, bcrypt password hashing
│   │   ├── config.py       # Pydantic Settings
│   │   ├── database.py     # Resilient Atlas / Motor connection with fallback
│   │   └── main.py         # FastAPI application entrypoint
│   └── requirements.txt    # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # Navbar, ProtectedRoute, Canvas elements
│   │   ├── context/        # AuthContext and session state
│   │   ├── pages/          # Landing, AIStylist, Wardrobe, SkinAnalysis, etc.
│   │   └── services/       # Axios API client
│   ├── package.json        # Vite + React + Tailwind CSS
│   └── tailwind.config.js  # Luxury Editorial theme styling
├── ml/
│   ├── inference/          # MediaPipe, CLIP, Recommender, MobileNetV2
│   ├── models/             # Pre-trained task files and model weights
│   └── preprocessing/      # Alpha-masked K-Means color extraction
├── test_samples/           # Studio flat-lays and test portraits
├── .env.example            # Environment variables template
└── .gitignore              # Production gitignore
```

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python 3.10+**
* **Node.js 18+ & npm**
* **Git**

### 1. Clone & Configure Backend

```bash
# Clone the repository
git clone https://github.com/roongtakhushi/StyleVerse.git
cd StyleVerse

# Set up Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env
```

### 2. Launch the Backend Server

```bash
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
* Interactive API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

### 3. Launch the Frontend

```bash
cd frontend
npm install
npm run dev
```
* Web Application: `http://localhost:5173`

---

## 🔒 Security & Data Integrity
* Passwords hashed via salted **Bcrypt** (`passlib`).
* Authentication handled via stateless **JWT** tokens (`python-jose`).
* High-Availability fallback layer (`mongomock-motor`) guarantees zero-downtime execution even during remote network or IP whitelisting restrictions.
