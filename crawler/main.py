from pathlib import Path
from extract_text import fetch_article
from pypandoc import convert_text
import json
import ast
import re
import validators
from datetime import datetime, timezone
from dateutil.tz import tzutc


def is_json_string(value):
    if isinstance(value, dict):
        return True
    try:
        json.loads(value)
        return True
    except (ValueError, TypeError):
        return False


def parse_repr_datetime(s):
    match = re.search(r"datetime\.datetime\(([\d\s,]+)", s)
    if not match:
        return None
    values = [int(x.strip()) for x in match.group(1).split(',')]
    return datetime(*values, tzinfo=timezone.utc)


base_path = Path(r"E:\prakash\data")
output = base_path / "output"
input = base_path / "Takeout" / "Keep"

output.mkdir(exist_ok=True)

for json_file in input.glob("*.json"):
    with open(json_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            url_text = data.get("annotations", [{}])[0].get(
                "url") or data.get("textContent")
            if validators.url(url_text):
                article = fetch_article(url_text)
            elif url_text is not None:
                article = convert_text(url_text, "md", "html")

            if len(article) > 0:
                op_file = output / f"{json_file.stem}.md"
                with open(op_file, "w", encoding="utf-8") as of:
                    title = data.get("title")
                    of.write(f"# {title}\n")
                    of.write("Reference:\n")
                    of.write(f" - [{url_text}]\n")
                    if not is_json_string(article):
                        of.write(f"{article}\n")
                    elif isinstance(article, dict):
                        authors = article.get("authors")
                        dt_str = article.get("publish_date")
                        md = f"**Authors**: {', '.join(authors)}  \n"
                        if isinstance(dt_str, str):
                            eval_context = {
                                "datetime": datetime, "tzutc": tzutc}
                            dt = eval(
                                dt_str, {"__builtins__": {}}, eval_context)
                        else:
                            dt = dt_str
                        # Format to human-readable
                        if dt is not None:
                            formatted = dt.strftime('%B %d, %Y')
                            md += f"**Publish date**: {formatted}\n"
                        md += article.get("text")
                        of.write(md)

        except json.JSONDecodeError as e:
            print(f"unable to parse json: {e}")
            continue
