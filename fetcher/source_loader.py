import re
from pathlib import Path


SOURCES_PATH = Path(__file__).parent.parent / "SOURCES.md"


def load_sources(path: Path = SOURCES_PATH) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    frequency_map = _parse_frequency(text)
    sources = _parse_sources(text, frequency_map)
    return sources


def _parse_frequency(text: str) -> dict[int, str]:
    freq_map = {}
    in_schedule = False
    for line in text.splitlines():
        if "Fetch Schedule Summary" in line:
            in_schedule = True
            continue
        if in_schedule and line.startswith("|") and "---" not in line and "Frequency" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2:
                freq_label = parts[0].strip().lower()
                ids_str = parts[1].strip()
                for id_str in ids_str.split(","):
                    try:
                        freq_map[int(id_str.strip())] = freq_label
                    except ValueError:
                        pass
        if in_schedule and line.startswith("##") and "Fetch" not in line:
            break
    return freq_map


def _parse_sources(text: str, frequency_map: dict[int, str]) -> list[dict]:
    sources = []
    current_category = ""
    header_pattern = re.compile(r"^##\s+Category\s+\d+\s+[—–-]+\s+(.+?)\s*(\(|$)")
    row_pattern = re.compile(
        r"^\|\s*(\d+)\s*\|"        # number
        r"\s*(.+?)\s*\|"           # name
        r"\s*(.+?)\s*\|"           # url
        r"\s*(RSS|Web|API)\s*\|"       # type
        r"\s*.+?\s*\|"             # cost (ignored)
        r"\s*.+?\s*\|"             # priority (ignored)
        r"\s*(.+?)\s*\|",          # signal
        re.IGNORECASE,
    )

    for line in text.splitlines():
        header_match = header_pattern.match(line)
        if header_match:
            current_category = header_match.group(1).strip()
            continue

        row_match = row_pattern.match(line)
        if row_match:
            num = int(row_match.group(1))
            name = row_match.group(2).strip()
            url = row_match.group(3).strip()
            fetch_type = row_match.group(4).strip().lower()
            signal = row_match.group(5).strip()

            if not url.startswith("http"):
                url = "https://" + url

            sources.append({
                "id": num,
                "name": name,
                "url": url,
                "type": fetch_type,
                "category": current_category,
                "frequency": frequency_map.get(num, "weekly"),
                "signal": signal,
            })

    return sorted(sources, key=lambda s: s["id"])
