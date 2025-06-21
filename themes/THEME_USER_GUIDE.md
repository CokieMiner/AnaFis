# Adding More Themes to AnaFis

AnaFis now uses a lightweight theme system that loads themes from Python packages instead of custom TCL files. This provides better performance and access to many professional themes.

## Quick Start

### 1. Install the ttkthemes package (Recommended)
```bash
pip install ttkthemes
```
This gives you access to 25+ professional themes including:
- **arc** - Modern flat theme
- **breeze** - KDE-style theme  
- **equilux** - Dark theme
- **ubuntu** - Ubuntu-style theme
- **yaru** - Modern Ubuntu theme
- And many more!

### 2. Install ttkbootstrap (Optional)
```bash
pip install ttkbootstrap
```
This provides Bootstrap-inspired modern themes.

## Adding Custom Theme Packages

1. Edit the `theme_packages.txt` file in the AnaFis directory
2. Add one package name per line (packages you can install with pip)
3. Restart AnaFis to load the new themes

Example `theme_packages.txt`:
```
ttkthemes
ttkbootstrap
azure-theme
forest-theme
sun-valley-theme
```

## Available Themes

### Built-in TTK Themes (Always Available)
- alt, clam, classic, default, vista, winnative, xpnative

### From ttkthemes Package
- adapta, arc, black, blue, breeze, clearlooks, elegance, equilux
- itft1, keramik, kroc, plastik, radiance, scidblue, scidgreen, scidgrey
- scidmint, scidpink, scidpurple, scidsand, smog, ubuntu, winxpblue, yaru

### From ttkbootstrap Package  
- cosmo, flatly, journal, literal, lumen, minty, pulse, sandstone
- united, yeti, morph, simplex, cerculean

## Selecting a Theme

1. Open AnaFis
2. Go to **Settings** (gear icon in toolbar)
3. Click the **Interface** tab
4. Choose your theme from the dropdown
5. Click **OK** to apply

The theme will be saved and restored when you restart AnaFis.

## Performance Notes

- Theme loading is now very fast (no directory scanning)
- Only packages that are actually installed will be loaded
- No more lag from custom TCL theme files
- All themes are professional quality and well-tested

## Troubleshooting

**Q: I installed a theme package but don't see new themes**
- Make sure you restarted AnaFis after installing the package
- Check that the package name is correctly spelled in theme_packages.txt

**Q: Can I still use custom TCL themes?**
- Custom TCL theme loading has been disabled for performance
- Use established theme packages instead (better quality and support)

**Q: How do I find more theme packages?**
- Search PyPI for "ttk theme" or "tkinter theme"
- Check the ttkthemes documentation for the latest themes
- Popular packages: ttkthemes, ttkbootstrap, azure-theme

## Benefits of Package-Based Themes

- ✅ **Fast loading** - No file scanning or TCL compilation
- ✅ **Professional quality** - Themes are maintained and tested
- ✅ **Easy installation** - Simple pip install commands
- ✅ **Better compatibility** - Designed for modern Python/Tkinter
- ✅ **No errors** - No more TclError messages from malformed themes
