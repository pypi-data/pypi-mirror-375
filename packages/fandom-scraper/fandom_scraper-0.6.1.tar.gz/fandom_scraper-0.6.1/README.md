# Fandom Scraper
A simple AI (span marker) powered fandom scraper.

> [!NOTE]  
> This package is a part of the [Cirilla project](https://github.com/AnthonyP57/Cirilla---a-LLM-made-on-a-budget)

> [!IMPORTANT]  
> In order to use the package an nvidia gpu is required.
## Installation
```bash
# (recommended)
uv add fandom-scraper

# or
pip install fandom-scraper
```
## Usage
The usage is very simple, the function requires path with so-called seeds to start scraping e.g. `examples/witcher_json/witcher_1.json`
```json
[
    "Geralt of Rivia", "Triss Merigold", "Vesemir", "Leo", "Lambert", 
    "Eskel", "Alvin", "Shani", "Zoltan Chivay", "Dandelion (Jaskier)", 
    "King Foltest", "Adda the White",

    "Jacques de Aldersberg", "Azar Javed", "Professor (leader of Salamandra)", 
    ...
]
```
and later uses sugesions provided by an Named Entity Recognition (NER) model. The script saves the scraped pages and instructions into respective folders.
```python
from fandom_scraper import scrape_fandom
in_path = Path("./examples/witcher_json")
out_path = Path("./examples/async_fandom")
instruct_path = Path("./examples/async_fandom_instruct")

scrape_fandom(in_path, out_path, instruct_path)
```
See `examples/async_fandom/` and `examples/async_fandom_instruct/` for more examples.