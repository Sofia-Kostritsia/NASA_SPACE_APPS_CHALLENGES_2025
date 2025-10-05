# AstroAtlas

A lightweight Python (pywebview) desktop wrapper for exploring the night sky with ready-made scene presets (Sun, Moon, Pleiades). The app displays **publicly available NASA scientific imagery and datasets** in an interactive view.

## Features
- One-click jump to curated scenes (Sun, Moon, Pleiades).
- Adjustable UI scale via the `ZOOM_PCT` variable.

## Data Sources
The scenes in this demo are based on **public NASA data**.

> Note: The project does **not** store copies of these datasets locally. It displays publicly available NASA materials accessible online.

## Requirements
- Python 3.9+
- Internet connection

## Installation
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
