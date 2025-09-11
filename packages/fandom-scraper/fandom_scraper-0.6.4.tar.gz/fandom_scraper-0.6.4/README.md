# Fandom Scraper
A simple AI (span marker) powered fandom scraper.

> [!NOTE]  
> This package is a part of the [Cirilla project](https://github.com/AnthonyP57/Cirilla---a-LLM-made-on-a-budget)

> [!IMPORTANT]  
> In order to use the package an nvidia gpu is required.
> 
> Considering how *fragile* huggingface's span marker can be, the requirements are fixed, so I advise to create a separate project in order to only scrape the data.
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
in_path = "./examples/witcher_json"
out_path = "./examples/async_fandom"
instruct_path = "./examples/async_fandom_instruct"

wiki = "Witcher"
lang = "en"

scrape_fandom(in_path=in_path,
              out_path=out_path,
              instruct_path=instruct_path,
              n_workers=50, # n async page "fetchers"
              wiki=wiki,
              lang=lang)
```
See `examples/async_fandom/` and `examples/async_fandom_instruct/` for more examples.

In order to turn the scraped instructions into a `.jsonl` file that can be used by [Cirilla](https://github.com/AnthonyP57/Cirilla---a-LLM-made-on-a-budget) models use:
```python
from fandom_scraper import instructions_into_conv

instructions_into_conv('./examples/async_fandom_instruct', './examples/fandom_instruct.jsonl')
```

The resulting file will look like:
```json
{"subject": "Shani", "text": [{"role": "user", "content": "What role did Shani play in the Battle of Brenna?"}, {"role": "assistant", "content": "Shani played a vital role in the Battle of Brenna in March 1268, serving in a field hospital under Milo Rusty Vanderbeck. Despite her youth, she effectively managed the demanding and gruesome conditions, providing essential medical aid to the wounded, contributing to the victory of the Northern Kingdoms."}], "data type": "conv", "source": "fandom"}
{"subject": "Shani", "text": [{"role": "user", "content": "How did Shani become the Dean of the Department of Medicine at Oxenfurt Academy?"}, {"role": "assistant", "content": "Shani, initially a medical student at Oxenfurt Academy, demonstrated her medical proficiency at a young age. She served in Milo Rusty Vanderbecks field hospital at the Battle of Brenna. Her exceptional skills and commitment to the field led to her appointment as the Dean of the Department of Medicine at Oxenfurt Academy."}], "data type": "conv", "source": "fandom"}
...
```
## Effectiveness
For the Witcher fandom, the scraper managed to gather 7506 pages, 1494 instructions. All in all around 40MiB of pure text in around 4 hours.