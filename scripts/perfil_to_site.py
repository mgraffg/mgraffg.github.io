#!/usr/bin/env python3
"""Convert the SECIHTI perfil.json profile export into Jekyll content.

Reads perfil.json (a local, gitignored file containing sensitive personal
CV data, see CLAUDE.md) and generates:

  - _publications/*.md  from featured ("producto principal") scientific
    publications (journal articles, book chapters, books, conference
    proceedings).
  - _alumni/*.md         from thesis supervisions where the profile owner
    acted as Director or Co-Director.

Usage:
    python3 scripts/perfil_to_site.py [path/to/perfil.json]

The script only writes bibliographic/academic metadata that is meant to be
public (titles, venues, co-author names, advisee names, degrees, years).
It never reads or emits fields such as CURP, photographs, or internal
document-storage links.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEGREE_EN = {
    "Maestría": "Master's",
    "Doctorado": "Ph.D.",
    "Licenciatura": "Bachelor's",
    "Especialidad": "Specialization",
}

ROLE_EN = {
    "Director(a)": "Director",
    "Co-Director (a)": "Co-Director",
}

# Maps a perfil.json "aportaciones" bucket to a publication_category key
# declared in _config.yml.
PUBLICATION_BUCKETS = {
    "articulosCientifica": "manuscripts",
    "capitulosCientifica": "books",
    "librosCientifica": "books",
    "memoriasCongresos": "conferences",
}


def yaml_str(value):
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def load_profile(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def author_name(author):
    parts = [author.get("nombre", ""), author.get("primerApellido", ""), author.get("segundoApellido", "")]
    return " ".join(p for p in parts if p).strip()


def build_citation(entry, authors, year):
    names = [author_name(a) for a in authors]
    names = [n for n in names if n]
    if len(names) > 1:
        authors_str = ", ".join(names[:-1]) + ", and " + names[-1]
    elif names:
        authors_str = names[0]
    else:
        authors_str = "Unknown author"
    venue = entry.get("nombreRevista") or entry.get("tituloLibro") or ""
    title = entry.get("titulo", "").rstrip(".")
    citation = f"{authors_str} ({year}). {title}."
    if venue:
        citation += f" {venue}."
    return citation


def collect_publications(profile):
    aportaciones = profile.get("aportaciones", {})
    items = []
    for bucket, category in PUBLICATION_BUCKETS.items():
        for entry in aportaciones.get(bucket, []):
            if not entry.get("productoPrincipal"):
                continue
            title = entry.get("titulo")
            if not title:
                print(f"warning: skipping {bucket} entry with no title (id={entry.get('id')})", file=sys.stderr)
                continue
            year_raw = entry.get("anio") or "1900"
            year_match = re.search(r"\d{4}", str(year_raw))
            year = year_match.group(0) if year_match else "1900"
            authors = entry.get("autores", [])
            venue = entry.get("nombreRevista") or entry.get("tituloLibro") or ""
            items.append({
                "title": title,
                "category": category,
                "date": f"{year}-01-01",
                "year": int(year),
                "venue": venue,
                "citation": build_citation(entry, authors, year),
                "paperurl": entry.get("doi") or "",
            })
    items.sort(key=lambda p: (p["year"], p["title"]))
    return items


def collect_alumni(profile):
    tesis = profile.get("perfil", {}).get("tesisDirigidas", [])
    items = []
    for entry in tesis:
        role_es = entry.get("rol", {}).get("nombre", "")
        role_en = ROLE_EN.get(role_es)
        if not role_en:
            continue
        name_parts = [entry.get("nombre", ""), entry.get("primerApellido", ""), entry.get("segundoApellido", "")]
        name = " ".join(p for p in name_parts if p).strip()
        thesis_title = entry.get("titulo")
        if not name or not thesis_title:
            print(f"warning: skipping tesisDirigidas entry with missing name/title (id={entry.get('id')})", file=sys.stderr)
            continue
        degree_es = entry.get("gradoAcademico", {}).get("nombre", "")
        degree_en = DEGREE_EN.get(degree_es, degree_es)
        date = entry.get("fechaObtencionGrado") or entry.get("fechaAprobacion") or ""
        year_match = re.search(r"\d{4}", date)
        year = int(year_match.group(0)) if year_match else 0
        items.append({
            "name": name,
            "thesis_title": thesis_title,
            "degree": degree_en,
            "role": role_en,
            "year": year,
        })
    items.sort(key=lambda a: (a["year"], a["name"]))
    return items


def clear_generated(directory, pattern):
    if not directory.exists():
        return
    for path in directory.glob(pattern):
        path.unlink()


def write_publications(items, out_dir):
    out_dir.mkdir(exist_ok=True)
    clear_generated(out_dir, "[0-9][0-9]_publication.md")
    for idx, item in enumerate(items, start=1):
        lines = [
            "---",
            f"title: {yaml_str(item['title'])}",
            "collection: publications",
            f"category: {item['category']}",
            f"date: {item['date']}",
            f"venue: {yaml_str(item['venue'])}",
            f"citation: {yaml_str(item['citation'])}",
        ]
        if item["paperurl"]:
            lines.append(f"paperurl: {yaml_str(item['paperurl'])}")
        lines.append("---")
        lines.append("")
        path = out_dir / f"{idx:02d}_publication.md"
        path.write_text("\n".join(lines), encoding="utf-8")
    return len(items)


def write_alumni(items, out_dir):
    out_dir.mkdir(exist_ok=True)
    clear_generated(out_dir, "[0-9][0-9]_alumni.md")
    for idx, item in enumerate(items, start=1):
        lines = [
            "---",
            f"title: {yaml_str(item['name'])}",
            "collection: alumni",
            f"thesis_title: {yaml_str(item['thesis_title'])}",
            f"degree: {yaml_str(item['degree'])}",
            f"role: {yaml_str(item['role'])}",
        ]
        if item["year"]:
            lines.append(f"year: {item['year']}")
        lines.append("---")
        lines.append("")
        path = out_dir / f"{idx:02d}_alumni.md"
        path.write_text("\n".join(lines), encoding="utf-8")
    return len(items)


def main():
    profile_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "perfil.json"
    if not profile_path.exists():
        print(f"error: profile file not found: {profile_path}", file=sys.stderr)
        return 1

    profile = load_profile(profile_path)

    publications = collect_publications(profile)
    n_pub = write_publications(publications, REPO_ROOT / "_publications")

    alumni = collect_alumni(profile)
    n_alumni = write_alumni(alumni, REPO_ROOT / "_alumni")

    print(f"Generated {n_pub} publication(s) in _publications/")
    print(f"Generated {n_alumni} alumni entr{'y' if n_alumni == 1 else 'ies'} in _alumni/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
