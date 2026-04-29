# Research Section Update

This folder contains the redesigned Research section for your Jekyll site, matching your existing `_projects` format.

## Contents

```
research_update/
├── _pages/
│   └── 3_research.md              # Updated main research page
├── _projects/
│   ├── 10_moon.markdown           # Planetary body: Moon
│   ├── 11_mars.markdown           # Planetary body: Mars
│   ├── 12_satellites.markdown     # Planetary body: Giant planet satellites
│   ├── 13_asteroids.markdown      # Planetary body: Asteroids & Comets
│   ├── 14_missions.markdown       # Unified missions page (with anchor links)
│   ├── 20_diviner-h-parameter.markdown   # Dataset: Diviner H-parameter
│   ├── 21_lamp-water.markdown            # Dataset: LAMP water
│   ├── 22_cassini-vims-titan.markdown    # Dataset: Cassini VIMS
│   ├── 23_galileo-nims-europa.markdown   # Dataset: Galileo NIMS
│   └── 24_galileo-ppr.markdown           # Dataset: Galileo PPR
└── assets/img/research/           # Placeholder for thumbnail images
```

## Installation

From your `jekyll-site` directory:

```bash
# 1. Replace the main research page
cp research_update/_pages/3_research.md _pages/

# 2. Add the new project pages
cp research_update/_projects/*.markdown _projects/

# 3. Create the research images directory
mkdir -p assets/img/research/
```

## Required Images

Add 80×80px thumbnail images to `assets/img/research/`:

- `moon.jpg` — Moon thumbnail
- `mars.jpg` — Mars thumbnail  
- `satellites.jpg` — Icy moons thumbnail
- `asteroids.jpg` — Asteroids thumbnail
- `missions.jpg` — Missions page thumbnail (optional)
- `diviner-h.jpg` — Diviner dataset thumbnail (optional)
- `lamp-water.jpg` — LAMP dataset thumbnail (optional)
- `vims-titan.jpg` — VIMS Titan thumbnail (optional)
- `nims-europa.jpg` — NIMS Europa thumbnail (optional)
- `ppr-thermal.jpg` — PPR thermal thumbnail (optional)

The existing images in your `assets/img/` folder can be reused where appropriate.

## URLs Generated

After building, pages will be available at:

**Planetary Bodies:**
- `/projects/10_moon/`
- `/projects/11_mars/`
- `/projects/12_satellites/`
- `/projects/13_asteroids/`

**Missions:**
- `/projects/14_missions/` (with anchor links like `#lro`, `#europa-clipper`, etc.)

**Datasets:**
- `/projects/20_diviner-h-parameter/`
- `/projects/21_lamp-water/`
- `/projects/22_cassini-vims-titan/`
- `/projects/23_galileo-nims-europa/`
- `/projects/24_galileo-ppr/`

## Model Links

Models link directly to GitHub repositories:
- heat1d → `https://github.com/phayne/heat1d`
- PTM3D → `https://github.com/phayne/PTM3D`
- Atmospheric RT → `https://github.com/phayne/atmospheric-rt`
- Spectroscopy → `https://github.com/phayne/spectroscopy`

Update these URLs in `3_research.md` if your repository names differ.

## Notes

- The page numbering (10_, 11_, etc.) controls the sort order if your site displays projects in filename order
- All pages use your existing `layout: page` and match the format of your other project files
- Scientific descriptions are placeholders — customize with your actual research content
- Four dataset pages show "Coming soon" notices; update when data is available
- The missions page uses HTML anchor IDs for direct linking from the research overview

## Build & Deploy

```bash
# Build with Docker (from jekyll-site directory)
docker run --rm -v "$PWD":/srv/jekyll jekyll/jekyll:4.2.0 jekyll build

# Or with your existing docker-compose
docker-compose up

# Copy to deployment repo
cp -r _site/* ../phayne.github.io/
cd ../phayne.github.io
git add -A && git commit -m "Update research section" && git push
```
