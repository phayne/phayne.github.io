# Research Section Pages

This folder contains the redesigned Research section for your Jekyll site.

## File Structure

```
research_pages/
├── 3_research.md              # Main research page (replaces existing)
└── research/
    ├── moon.md                # Planetary body: Moon
    ├── mars.md                # Planetary body: Mars
    ├── satellites.md          # Planetary body: Giant planet satellites
    ├── asteroids.md           # Planetary body: Asteroids & Comets
    ├── missions.md            # Unified missions page
    └── datasets/
        ├── diviner-h-parameter.md
        ├── lamp-water.md
        ├── cassini-vims-titan.md
        ├── galileo-nims-europa.md
        └── galileo-ppr.md
```

## Installation

1. **Replace the main research page:**
   ```bash
   cp 3_research.md /path/to/jekyll-site/_pages/
   ```

2. **Add the new research subpages:**
   ```bash
   mkdir -p /path/to/jekyll-site/_pages/research/datasets
   cp research/*.md /path/to/jekyll-site/_pages/research/
   cp research/datasets/*.md /path/to/jekyll-site/_pages/research/datasets/
   ```

3. **Add placeholder images** (80×80px recommended):
   ```bash
   mkdir -p /path/to/jekyll-site/img/research/
   ```
   Add images: `moon.jpg`, `mars.jpg`, `satellites.jpg`, `asteroids.jpg`

## URLs Generated

After building, these pages will be available at:

- `/research/` — Main research overview
- `/research/moon/` — Moon research
- `/research/mars/` — Mars research
- `/research/satellites/` — Giant planet satellites
- `/research/asteroids/` — Asteroids & comets
- `/research/missions/` — All missions (with anchor links)
- `/research/datasets/diviner-h-parameter/` — Diviner dataset
- `/research/datasets/lamp-water/` — LAMP dataset
- `/research/datasets/cassini-vims-titan/` — VIMS Titan dataset
- `/research/datasets/galileo-nims-europa/` — NIMS Europa dataset
- `/research/datasets/galileo-ppr/` — PPR thermal maps

## Model Links

The models section links directly to GitHub repositories:
- heat1d → `https://github.com/phayne/heat1d`
- PTM3D → `https://github.com/phayne/PTM3D`
- Atmospheric RT → `https://github.com/phayne/atmospheric-rt`
- Spectroscopy → `https://github.com/phayne/spectroscopy`

**Note:** Update these URLs if your repositories have different names.

## Customization

- **Content:** All pages contain placeholder scientific descriptions — update with your actual research content
- **Dataset pages:** Four datasets show "Coming soon" notices; update when data is available
- **Mission links:** External links point to official mission pages where available
- **Styling:** CSS is embedded in each page; consider moving to your site's main stylesheet
