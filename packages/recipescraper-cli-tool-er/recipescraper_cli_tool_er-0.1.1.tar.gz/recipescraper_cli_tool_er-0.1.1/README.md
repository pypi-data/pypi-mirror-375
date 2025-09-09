RecipeScraper CLI Tool

Version: 0.1.1
Python: >= 3.13

RecipeScraper is a Python command-line tool that extracts recipe information from a given recipe URL. It supports most popular recipe websites that use structured data (JSON-LD) and saves the results in a structured text format.

Features:
CLI prompts for a recipe URL, or pass it as an argument
Scrapes and extracts:
Recipe title
Ingredients
Instructions (including nested sections)
Optional: Equipment list, nutrition info if available
Saves the recipe in a formatted .txt file in the current directory
Works with most websites that provide recipe metadata in structured formats

Requirements:
Python >= 3.13

Dependencies (managed automatically with uv):
argparse>=1.4.0
bs4>=0.0.2
requests>=2.32.5
validators>=0.35.0

Installation:
Clone this repository:
git clone https://github.com/yourusername/RecipeScraper.git
cd RecipeScraper

Create and sync the virtual environment:
uv sync

Activate the environment:
Linux / macOS:
source .venv/bin/activate
Windows:
.venv\Scripts\activate

Or install the package directly with pip:
pip install recipescraper-cli-tool-er==0.1.0

Usage:
Run the program by passing a URL as an argument:
recipescraper https://example.com/recipe-url

Or interactively:
python main.py

This will scrape the recipe and save a .txt file in the current directory.

Example Output File:
Recipe Title: Polenta Fries
Ingredients:
1 cup cornmeal
4 cups water
Salt
Olive oil
Instructions:
Preheat the oven to 425°F.
Bring water to a boil, add salt.
Slowly whisk in cornmeal.
Cook until thickened...
Planned Features:
Support exporting recipes in JSON or Markdown
Improved error handling and validation
Optional web interface for easier scraping
Automatic detection of recipe metadata across more websites

License:

MIT License