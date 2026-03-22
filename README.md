# PaceCraft — Minecraft Speedrun Cover Maker

**PaceCraft** is a desktop application that automatically generates professional cover images for Minecraft speedruns. Enter your split times (pace), seed information, match ID, and more—the tool composes a clean, customizable overlay on top of your chosen background.

---

## ✨ Features

- **Flexible seed input**  
  - Single seed code or advanced mode (Overworld / Nether / End / RNG seeds)  
  - Match ID, start type, bastion type, and speedrun category support

- **Split times (pace)**  
  - 7 progress stages: Nether, Bastion, Fortress, Blind, Stronghold, End, Finish  
  - Check/uncheck completed stages; times are sorted automatically

- **Background selection**  
  - **Auto mode**: picks the matching background based on the last completed stage  
  - **Manual mode**: choose from built‑in backgrounds or any local image (original resolution preserved, no stretching)

- **Text styling**  
  - Alignment (left / center / right), font size, line spacing, color  
  - X/Y position adjustment  
  - Bold / italic support (if font allows)  
  - Custom TTF font file support

- **Real‑time preview**  
  - Adjust any setting and see the result instantly in the preview area

- **Flexible file naming**  
  - Choose which elements to include: seed, match ID, start type, bastion type, speedrun category, final time, final progress  
  - Output as `element1_element2_...png`

- **Auto‑saved settings**  
  - All text style preferences are stored in `config.json` and restored on next launch



---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 – 3.11  
- [Pillow](https://python-pillow.org/) library

### Installation

1. **Clone or download** this repository.
2. **Install the required Python package** (open a terminal in the project folder):
   ```bash
   pip install pillow
   ```
3. **Place your background images** (optional).  
   The built‑in backgrounds must be named:
   - `1nether.png`
   - `2bastion.png`
   - `3fortress.png`
   - `4blind.png`
   - `5stronghold.png`
   - `6end.png`
   - `7finish.png`

   They can be any resolution – the tool uses the original size.

4. **Run the application**:
   ```bash
   python PaceCraft.py
   ```
## 🎮 How to Use

1. **Enter seed information**  
   - Single seed: paste or type the seed code.  
   - Advanced mode: enable it to enter up to four different seeds (Overworld, Nether, The End, RNG).  
   - Optionally fill in Match ID, start type, bastion type, and speedrun category.

2. **Input your split times**  
   - For each progress, enter minutes and seconds, and check the “Completed” box if that stage was reached.  
   - If you didn’t reach a stage, leave it unchecked.

3. **Choose a background**  
   - **Auto**: the tool will automatically use the background corresponding to the last completed stage (sorted by time).  
   - **Manual**: pick one of the built‑in backgrounds or click “Choose local image” to use any picture on your computer.

4. **Customize text style**  
   - Adjust alignment, font size, line spacing, color, and position (X/Y).  
   - Use bold/italic or load a custom TTF font.

5. **Set output filename**  
   - Check the boxes for the information you want in the filename.  
   - The final name will be generated automatically.

6. **Save the image**  
   - Click **Generate & Save**, choose a location, and the cover will be saved as a PNG file with your chosen name.

---

## ⚙️ Configuration

- All text style settings are automatically saved in `config.json` in the same folder.  
- You can delete this file to reset all styles to default values.

---

## 📂 File Structure

- PaceCraft/
- ├── PaceCraft.py          # Main application script
- ├── config.json           # Saved style preferences (auto‑generated)
- ├── 1nether.png           # Optional built‑in backgrounds
- ├── 2bastion.png
- ├── ...
- └── README.md             # This file

## 🛠️ Dependencies

- Python 3.8+
- [Pillow](https://python-pillow.org/) – image processing

---

## 📝 Notes

- The application does **not** modify your original background images.  
- When using a local image, the text position resets to (100,100) to help you reposition comfortably, but the other style settings remain unchanged.  
- The tool supports any image resolution; it will not stretch or crop your backgrounds.

---

## 📄 License

This project is open‑source and available under the [MIT License](LICENSE).

---
