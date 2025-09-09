RecipeScraper

Version: 0.1.0

RecipeScraper is a Python tool that extracts recipe information from a given recipe URL.
Currently, it supports PreppyKitchen.com, with plans to expand support for more recipe websites in future versions.

Features:
Prompts the user for a recipe URL.

Scrapes and extracts:
Recipe title
Equipment list
Ingredients
Instructions

Saves the recipe in a formatted .txt file inside the txt_files/ folder.

Requirements:
Python 3.13.3 or higher
uv (https://github.com/astral-sh/uv) for virtual environment and dependency management

Installation:
Clone this repository:
git clone https://github.com/yourusername/RecipeScraper.git
cd RecipeScraper

Create and sync the virtual environment with uv:
uv sync

Activate the environment:
source .venv/bin/activate (Linux / macOS)
.venv\Scripts\activate (Windows)

Usage:
Run the program:
python main.py

You will be prompted to enter a recipe URL (currently only works with PreppyKitchen.com).
After running, a .txt file will be generated in the txt_files/ directory containing the scraped recipe.

Example Output File:
Recipe Title: Rice Pudding
Equipment: saucepan, whisk, spatula
Ingredients:
1 cup rice
2 cups milk
1/2 cup sugar

Instructions:
Heat the milk...
Stir in the rice...

Limitations (v0.1.0):
Only works with PreppyKitchen.com
Basic scraping (does not handle images, nutrition info, etc.)
Planned Features
Support for more recipe websites (using JSON-LD structured data).
Better error handling and validation.
Option to export recipes in JSON or Markdown format.
CLI arguments instead of interactive input.

Dependencies:
bs4>=0.0.2
requests>=2.32.5
validators>=0.35.0

Dependencies are managed automatically with uv.

License:
MIT License