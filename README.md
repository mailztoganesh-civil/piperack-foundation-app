# Piperack Pedestal Foundation Design

Static web app for isolated pedestal footing design under biaxial eccentric load.

Matches the methodology of **AD204-601-G-03378** (SARB Field Development Project) and follows ACI 318 style checks.

## Features

- **Geometry** tab – Footing, pedestal, soil, materials
- **Load cases** tab – Add / edit multiple primary reactions from structural analysis
- **Combinations** tab – Elastic & Ultimate combinations with soil/foundation factor
- **Results** tab – Live calculation of:
  - Self-weight
  - Bearing pressure (σmax / σmin)
  - Overturning & Sliding Factors of Safety
  - Simplified design moments & required reinforcement

## How to use on iPad / phone

1. Host this folder on **GitHub Pages** (free)
2. Open the link in Safari

### Deploy to GitHub Pages (from iPad)

1. Create a new public repository on GitHub
2. Upload `index.html` (and this README)
3. Go to **Settings → Pages**
4. Source = Deploy from a branch → `main` / root
5. Save → wait 1 minute
6. Open the link shown (usually `https://YOUR-USERNAME.github.io/REPO-NAME/`)

## Disclaimer

Educational prototype. Always verify results with a licensed structural engineer and the project design basis.
