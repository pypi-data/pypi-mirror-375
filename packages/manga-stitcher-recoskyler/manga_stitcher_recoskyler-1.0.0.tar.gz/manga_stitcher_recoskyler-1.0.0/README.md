# Manga Stitcher

Manga Stitcher is a straightforward tool designed to automatically combine manga pages vertically, creating a seamless reading experience. Many manga releases include extra "tail" images—often containing the scanlator's logo or credits—in separate files. This script detects and merges these pages, saving you time and ensuring your manga is presented as intended.

## Features

- Supports input from directories full of CBZ/CBR/ZIP/RAR files.
- Outputs stitched images in the same format.
- Optionally recursive directory traversal.
- Configurable title and series metadata
- Safety checks for width and height mismatches. (skips)

## Requirements

- Python 3.10+
- Pip
  - Pillow
  - tqdm
  - rarfile
  - zipfile
  - cbz

## Installation

### By pip or PipX

You can install Manga Stitcher via pip:

```bash
pip install manga-stitcher
```

 or using PipX:

```bash
pipx install manga-stitcher
```

### By cloning the repository

1. Clone the repository:

   ```bash
   git clone https://github.com/recoskyler/manga-stitcher

   cd manga-stitcher/src/manga_stitcher_recoskyler
   ```

## Usage

Run the script with the desired options. For example:

```bash
manga_stitcher --title "My manga title" --series "My manga series" --recursive /path/to/manga
```

## Development

1. Create a virtual environment, or use the included Dev Container if using VSCode or DevPod.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script with your desired options.

### Building

1. Ensure build tools are installed:

    ```bash
    python3 -m pip install --upgrade build
    ```

2. Build the package:

    ```bash
    python3 -m build
    ```

### Publishing

1. Ensure Twine is installed:

    ```bash
    python3 -m pip install --upgrade twine
    ```

2. Publish the package:

    ```bash
    python3 -m twine upload --repository pypi dist/*
    ```

## About

By Adil Atalay Hamamcıoğlu - [recoskyler](https://github.com/recoskyler) - 2025
