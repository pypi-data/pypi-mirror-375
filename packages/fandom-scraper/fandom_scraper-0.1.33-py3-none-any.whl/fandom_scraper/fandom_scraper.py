import asyncio
import json
import os
import re
from pathlib import Path
import fandom
from span_marker import SpanMarkerModel
from typing import List  # NEW

span_model_name = "tomaarsen/span-marker-bert-base-fewnerd-fine-super"
sm_model = SpanMarkerModel.from_pretrained(span_model_name).cuda()

def clean_text(text: str) -> str:
    """Clean text until the first unwanted section appears, then stop."""
    cleaned_lines = []
    unwanted_sections = {"Footnotes", "References", "Videos", "Gallery", "External links", "See also", "Other"}

    for line in text.split("\n"):
        line = line.strip()

        # hard stop if line starts with any unwanted section
        if any(line.startswith(sec) for sec in unwanted_sections):
            break

        # remove JSON-LD / schema.org lines
        if line.startswith("{\"@context\":") or line.startswith("{ \"@context\":"):
            continue

        # remove footnotes like ↑ 6.0 6.1 Time of Contempt
        if re.match(r"^↑\s?\d+(\.\d+)*.*", line):
            continue

        # remove empty lines
        if not line:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# NEW: helper to split long texts safely
def chunk_text_by_chars(text: str, max_chars: int = 1000) -> List[str]:
    """Split text into chunks not longer than max_chars, preserving line boundaries."""
    if not text:
        return []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    chunks: List[str] = []
    cur = []
    cur_len = 0
    for ln in lines:
        ln_len = len(ln) + 1
        if cur_len + ln_len > max_chars and cur:
            chunks.append("\n".join(cur))
            cur = [ln]
            cur_len = ln_len
        else:
            cur.append(ln)
            cur_len += ln_len
    if cur:
        chunks.append("\n".join(cur))
    return chunks


# CHANGED: classify_entities now defensive + batching
def classify_entities(text: str):
    if text is None:
        return set()

    if not isinstance(text, (str, list)):
        print(f"[DEBUG] classify_entities received non-string: {type(text)}; coercing to str.")
        text = str(text)

    if isinstance(text, list):
        text_list: List[str] = [str(x) for x in text if x is not None]
    else:
        text_list = chunk_text_by_chars(text, max_chars=800)

    if not text_list:
        return set()

    batch_size = 8
    all_ents = []
    for i in range(0, len(text_list), batch_size):
        batch = text_list[i : i + batch_size]
        try:
            preds = sm_model.predict(batch)
            if isinstance(preds, list) and preds and isinstance(preds[0], list):
                for p in preds:
                    all_ents.extend(p)
            else:
                all_ents.extend(preds)
        except Exception as ex:
            preview = batch[0][:200] if batch else "<empty>"
            print(f"[ERROR] span-marker.predict failed for batch preview: {preview!r}. Exception: {ex}")
            continue

    suggestions = set()
    for e in all_ents:
        if not isinstance(e, dict):
            continue
        if e.get("score", 0.0) >= 0.9 and e.get("span"):
            suggestions.add(e["span"].strip())
    return suggestions


def extract_instructions(text: str):
    """Extract instructions from a text and remove them from the main text."""
    lines = text.split('\n')
    capture = False
    extracted_lines = []
    remaining_lines = []

    for i, line in enumerate(lines):
        if i > 0 and lines[i-1].startswith('Quick Answers'):
            capture = True
        elif line.startswith('{'):
            capture = False

        if capture:
            extracted_lines.append(line)
        else:
            remaining_lines.append(line)

    # parse questions/answers
    questions, answers = [], []
    capture = False
    for l in extracted_lines:
        if l.startswith('						Provided by:'):
            capture = False
        if capture:
            answers[-1].append(l)
        if l.endswith('?'):
            questions.append(l)
            answers.append([])
            capture = True

    ans_clean = []
    for a in answers:
        a = ''.join(a)
        a = a.replace('\n', ' ').replace('\t', '').replace("'", '')
        ans_clean.append(a)

    q_a_dict = {q: a for q, a in zip(questions, ans_clean)}
    if len(questions) > 0:
        return q_a_dict, '\n'.join(remaining_lines)
    else:
        return None, text


async def fetch_page(title: str, out_path: Path, instruct_path: Path, search_counter: dict, q: asyncio.Queue, queued: set, visited: set):
    """Download all pages returned by search for a title."""
    try:
        results = await asyncio.to_thread(fandom.search, title)
        search_counter["count"] += 1
        search_counter["queue_size"] = q.qsize()
        print(f"[SEARCH #{search_counter['count']}] {title} -> queue size: {search_counter['queue_size']}")

        if not results:
            print(f"[MISS] {title}")
            return None

        for (page_title, _) in results:
            if page_title in visited:
                continue
            try:
                page = await asyncio.to_thread(fandom.page, page_title)
                text = getattr(page, "plain_text", "")
                if not text:
                    continue

                instructions, cleaned_text = extract_instructions(text)
                cleaned_text = clean_text(cleaned_text)

                fname = page_title.replace("/", "_") + ".txt"
                fpath = out_path / fname
                if not fpath.exists():
                    await asyncio.to_thread(fpath.write_text, cleaned_text, encoding="utf-8")

                if instructions:
                    instruct_file = instruct_path / f"{page_title}.json"
                    def write_json():
                        if not instruct_file.exists():
                            with open(instruct_file, "w", encoding="utf-8") as f:
                                json.dump(instructions, f, ensure_ascii=False, indent=2)
                    await asyncio.to_thread(write_json)
                    print(f"[INSTRUCT] {len(instructions)} instructions saved for {page_title}")

                print(f"[FETCH] {page_title}")
                visited.add(page_title)

            except Exception as inner_e:
                print(f"[ERROR] Failed page {page_title}: {inner_e}")

        return True

    except Exception as e:
        print(f"[ERROR] {title}: {e}")
        return None


# CHANGED: don’t add True into visited
async def fetch_worker(q: asyncio.Queue, out_path: Path, instruct_path: Path, visited: set, search_counter: dict, queued: set):
    while True:
        title = await q.get()
        queued.discard(title)
        if title in visited:
            q.task_done()
            continue
        res = await fetch_page(title, out_path, instruct_path, search_counter, q, queued, visited)
        # fetch_page already updates visited if successful
        q.task_done()


async def classify_worker(out_path: Path, visited: set, q: asyncio.Queue, done: set, queued: set):
    while True:
        for fname in os.listdir(out_path):
            if not fname.endswith(".txt") or fname in done:
                continue
            fpath = out_path / fname
            text = fpath.read_text(encoding="utf-8")
            suggestions = classify_entities(text)
            print(f"[NER] {fname}: {len(suggestions)} suggestions")
            for s in suggestions:
                if s not in visited and s not in queued:
                    queued.add(s)
                    await q.put(s)
                    print(f"[QUEUE] Added '{s}' -> queue size: {q.qsize()}")
            done.add(fname)
        await asyncio.sleep(5)


async def _main(in_path: Path, out_path: Path, instruct_path: Path, n_workers: int = 50):

    for p in [in_path, out_path, instruct_path]:
        if not isinstance(p, Path):
            p = Path(p)

    out_path.mkdir(parents=True, exist_ok=True)
    instruct_path.mkdir(parents=True, exist_ok=True)

    seeds = []
    for file in os.listdir(in_path):
        if not file.endswith(".json"):
            continue
        with open(in_path / file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                seeds.extend([str(x) for x in data])
    print(f"[SEEDS] {len(seeds)}")

    q = asyncio.Queue()
    visited, done = set(), set()
    queued = set()

    for s in seeds:
        if s not in visited and s not in queued:
            queued.add(s)
            await q.put(s)

    search_counter = {'count': 0, 'queue_size': 0}
    fetchers = [asyncio.create_task(fetch_worker(q, out_path, instruct_path, visited, search_counter, queued)) for _ in range(n_workers)]
    classifier = asyncio.create_task(classify_worker(out_path, visited, q, done, queued))

    await asyncio.gather(*fetchers, classifier)


def scrape_fandom(in_path: Path,
                  out_path: Path,
                  instruct_path: Path,
                  n_workers: int = 50,
                  wiki: str = "Witcher",
                  lang: str = "en"):

    fandom.set_wiki(wiki)
    fandom.set_lang(lang)

    asyncio.run(_main(in_path, out_path, instruct_path, n_workers))
