# Digital Rain

A recreation of the "digital rain" code effect from *The Matrix*, written in Python with pygame. Mirrored katakana charcaters slide down a black screen in fading streaks of green, with an optional CRT-monitor look (glow, scanlines and dark edges) which can be toggled on/off.

![Digital rain running in fullscreen](media/demo.mp4)

---

## Features

- Columns of mirrored katakana, digits and symbols, inspired by the characters used in the film
- Near-white "heads" with trails that fade from pale green to lime to black
- More than one streak can run down the same column at once
- Heads flicker and characters glitch at random, so the screen never repeats itself
- CRT effect: soft glow (bloom), scanlines and a vignette, switchable on and off
- Live controls for speed, character size, pause and fullscreen
- Steady 60 fps, thanks to pre-rendered (cached) characters
- Japanese font bundled with the project.

---


## Running from source

Requires Python 3.10 or newer.

```bash
git clone https://github.com/YOUR-USERNAME/matrix_rain.git
cd matrix_rain
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Controls

| Key | Action |
|---|---|
| `F` or `F11` | Toggle fullscreen |
| `Space` | Pause / resume |
| `+` / `-` | Speed up / slow down |
| `[` / `]` | Smaller / larger characters |
| `C` | Toggle the CRT effect (glow, scanlines, vignette) |
| `Esc` | Quit |

The window can also be resized or maximised.

---

## How it works

The effect has two separate layers.

**1. A grid of characters that barely changes.** The screen is divided into cells, and each cell holds a random character, stored as a list of columns (`grid[col][row]`). The characters don't fall. They stay in place.

**2. Drops: bars of light sliding down the columns.** Each drop is an object with a column, a position, a speed and a trail length, all chosen at random. Wherever a drop is, it lights up the characters already sitting in those cells. Cells that no drop is passing over aren't drawn, so they stay black. Each column gets one to three drops, which is how several separate streaks can share one column.

**The fading trail.** For a cell `k` rows behind the head of a drop of length `L`:

```
t = 1 - k / L                    # 1 at the head, 0 at the end of the trail
brightness = 0.95·t² + 0.05·t
```

Squaring makes the brightness drop off quickly, so each drop shows as a short bright chunk that fades into black, rather than a long smear. Colours are blended with linear interpolation: from a pale near-white close to the head, to lime green further down, then towards black as the brightness falls. Where two drops overlap, the brighter value wins, so heads are never covered by another drop's tail.

**Frame-rate independent movement.** Drops move at a speed in rows per second, multiplied by the time since the last frame (`dt`), so the rain falls at the same speed on different machines.

**Flicker and glitches.** When a head moves into a new cell, that cell gets a new random character, so each drop rewrites its column as it falls. A small number of random cells across the screen also change every frame, which makes the trails shimmer.

**Performance: the glyph cache.** Turning text into an image is slow and drawing thousands of characters per frame this way may drop frame rate. Instead, every character is rendered once at start-up, at 25 brightness levels plus the head colours, mirrored, and stored in a dictionary. Drawing a cell is then just a lookup and a copy.

**CRT effect.**
- **Glow:** each frame is shrunk down (which blurs it), stretched back up, and added on top of the sharp original, so bright characters bleed light into the dark around them.
- **Scanlines:** a see-through overlay with a faint dark line every 3 pixels.
- **Vignette:** an overlay that darkens towards the edges and corners, like a curved tube. It's built small and stretched up to full size, because calculating it pixel by pixel at full resolution would be slow.

The scanlines and vignette are built once and only rebuilt when the window size changes.

---

## Customising

All the settings are at the top of `main.py`:

| Setting | What it does |
|---|---|
| `char_size` | Starting character size in pixels |
| `speed_min`, `speed_max` | Range of drop speeds (rows per second) |
| `length_min`, `length_max` | Range of trail lengths (cells) |
| `trail_colour` | Main trail colour (more red = more yellow/lime) |
| `highlighted`, `near_colour` | Colours of the head and the cell just behind it |
| `pale_falloff` | How quickly the trail turns from pale to lime (higher = sooner) |
| `steps` | Number of brightness levels in the cache |
| `show_grid` | Debug: show every character dimly, to see the grid behind the drops |

The glitch rate is the `0.005` in the glitch loop.

---

## Project structure

```
matrix_rain/
├── main.py   # The whole program
├── requirements.txt   # Python dependencies 
├── assets/
│   └── fonts/
│       ├── NotoSansJP-Regular.ttf
│       └── OFL.txt   # The font's licence
├── media/
│ └── demo.mp4   # The recording at the top of this README
└── README.md   # This file
```

---

## How I built it

I built this in stages, getting each one working before moving on, with one commit per stage:

1. A window and the game loop
2. Drawing text, with a bundled Japanese font
3. The character grid
4. One falling drop with frame-rate independent timing
5. The fading trail
6. Many drops, using a `Drop` class
7. Details: head flicker, glitches, mirrored and centred characters
8. Performance: the glyph cache
9. Controls: fullscreen, pause, speed, size
10. CRT effect: glow, scanlines, vignette

The commit history shows the project at each stage.

## Possible improvements

- Reorganise the code into a `Rain` class, so the setup function doesn't need to return ten separate values
- Make the glitch rate frame-rate independent, using `dt`
- Make switchable colour schemes (classic green, red, blue)

---

## Credits

- Font: [Noto Sans JP](https://fonts.google.com/noto/specimen/Noto+Sans+JP) by Google, used under the SIL Open Font License (see `assets/fonts/OFL.txt`)
- Built with [Python](https://www.python.org/) and [pygame](https://www.pygame.org/)
- Inspired by the digital rain in *The Matrix* (1999). This is a fan recreation and is not affiliated with Warner Bros.
