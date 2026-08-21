#!/usr/bin/env python3
"""Convert the SECIHTI perfil.json profile export into Jekyll content.

Reads perfil.json (a local, gitignored file containing sensitive personal
CV data, see CLAUDE.md) and generates:

  - _publications/*.md  from featured ("producto principal") scientific
    publications (journal articles, book chapters, books, conference
    proceedings), each carrying its Google Scholar citation link
    (perfil.json's cita.urlCita) when available. These are collection
    documents with output disabled in _config.yml: they only ever appear
    listed on /publications/, never as their own page.
  - _alumni/*.md         from thesis supervisions where the profile owner
    acted as Director or Co-Director, with the advisee's degree, graduating
    institution, and a link to the thesis repository when the profile has
    one that is actually public (never the private cloud.secihti.mx/
    tlapiakali.conahcyt.mx document storage links). Same as above:
    listing-only, no individual page per advisee.

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
from urllib.parse import urlparse

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

# perfil.json identifies the institution of each tesisDirigidas entry by an
# internal SNP catalog code (claveInstitucionSnp), not by name. The JSON
# itself never spells out what these codes mean, so this mapping was built
# by cross-referencing the codes against perfil.cursosImpartidos (which ties
# code 37 to the "Doctorado en Ciencia de Datos" program) and the profile
# owner's own trajectory, then confirmed manually. Extend this table if a
# future perfil.json export introduces theses directed at a new institution.
INSTITUTION_SNP_CODES = {
    "37": "INFOTEC",
    "138": "Universidad Michoacana de San Nicolás de Hidalgo (UMSNH)",
}

# tesisDirigidas.documento.uri normally points to cloud.secihti.mx or
# tlapiakali.conahcyt.mx: personal document storage tied to the SECIHTI
# account, not a public thesis repository (filenames are things like
# "Claudia.pdf" or an internal advisory letter, not a repository record).
# Only a URL hosted outside these domains is treated as a public repository
# link (e.g. an institutional repository like INFOTEC's); anything on them
# is never exposed, no matter what the filename suggests.
PRIVATE_DOCUMENT_DOMAINS = {"cloud.secihti.mx", "tlapiakali.conahcyt.mx"}

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
    if not isinstance(author, dict):
        return ""
    parts = [author.get("nombre", ""), author.get("primerApellido", ""), author.get("segundoApellido", "")]
    return " ".join(p for p in parts if p).strip()


def build_citation(entry, authors, year):
    names = [author_name(a) for a in (authors or [])]
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


def resolve_doi_url(doi):
    doi = (doi or "").strip()
    if not doi:
        return ""
    if doi.startswith("http://") or doi.startswith("https://"):
        return doi
    # perfil.json is inconsistent: most entries store the full DOI URL, but
    # some store a bare DOI (e.g. "10.1109/MCI.2019.2954668"), which used
    # verbatim as an href resolves as a broken relative link on the site.
    return f"https://doi.org/{doi}"


def collect_publications(profile):
    aportaciones = profile.get("aportaciones") or {}
    if not isinstance(aportaciones, dict):
        print("warning: 'aportaciones' is not an object, skipping all publications", file=sys.stderr)
        aportaciones = {}
    items = []
    for bucket, category in PUBLICATION_BUCKETS.items():
        entries = aportaciones.get(bucket) or []
        if not isinstance(entries, list):
            print(f"warning: '{bucket}' is not a list, skipping", file=sys.stderr)
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                print(f"warning: skipping malformed (non-object) entry in {bucket}", file=sys.stderr)
                continue
            try:
                if not entry.get("productoPrincipal"):
                    continue
                title = entry.get("titulo")
                if not title:
                    print(f"warning: skipping {bucket} entry with no title (id={entry.get('id')})", file=sys.stderr)
                    continue
                year_raw = entry.get("anio") or "1900"
                year_match = re.search(r"\d{4}", str(year_raw))
                year = year_match.group(0) if year_match else "1900"
                authors = entry.get("autores")
                venue = entry.get("nombreRevista") or entry.get("tituloLibro") or ""
                cita = entry.get("cita") or {}
                scholarurl = cita.get("urlCita") if isinstance(cita, dict) else ""
                items.append({
                    "title": title,
                    "category": category,
                    "date": f"{year}-01-01",
                    "year": int(year),
                    "venue": venue,
                    "citation": build_citation(entry, authors, year),
                    "paperurl": resolve_doi_url(entry.get("doi")),
                    "scholarurl": scholarurl or "",
                })
            except Exception as exc:
                print(f"warning: skipping malformed entry in {bucket} (id={entry.get('id')}): {exc}", file=sys.stderr)
    items.sort(key=lambda p: (p["year"], p["title"]))
    return items


def resolve_institution(entry):
    code = entry.get("claveInstitucionSnp")
    if code in INSTITUTION_SNP_CODES:
        return INSTITUTION_SNP_CODES[code]
    institucion = entry.get("institucion")
    if isinstance(institucion, dict) and institucion.get("nombre"):
        return institucion["nombre"]
    return ""


def resolve_repository_url(entry):
    documento = entry.get("documento")
    if not isinstance(documento, dict):
        return ""
    uri = documento.get("uri") or ""
    if not uri:
        return ""
    host = urlparse(uri).netloc
    if not host or host in PRIVATE_DOCUMENT_DOMAINS:
        return ""
    return uri


def collect_alumni(profile):
    perfil = profile.get("perfil") or {}
    if not isinstance(perfil, dict):
        print("warning: 'perfil' is not an object, skipping all alumni", file=sys.stderr)
        perfil = {}
    tesis = perfil.get("tesisDirigidas") or []
    if not isinstance(tesis, list):
        print("warning: 'tesisDirigidas' is not a list, skipping all alumni", file=sys.stderr)
        tesis = []
    items = []
    for entry in tesis:
        if not isinstance(entry, dict):
            print("warning: skipping malformed (non-object) entry in tesisDirigidas", file=sys.stderr)
            continue
        try:
            role_es = (entry.get("rol") or {}).get("nombre", "")
            role_en = ROLE_EN.get(role_es)
            if not role_en:
                continue
            name_parts = [entry.get("nombre", ""), entry.get("primerApellido", ""), entry.get("segundoApellido", "")]
            name = " ".join(p for p in name_parts if p).strip()
            thesis_title = entry.get("titulo")
            if not name or not thesis_title:
                print(f"warning: skipping tesisDirigidas entry with missing name/title (id={entry.get('id')})", file=sys.stderr)
                continue
            degree_es = (entry.get("gradoAcademico") or {}).get("nombre", "")
            degree_en = DEGREE_EN.get(degree_es, degree_es)
            date = str(entry.get("fechaObtencionGrado") or entry.get("fechaAprobacion") or "")
            year_match = re.search(r"\d{4}", date)
            year = int(year_match.group(0)) if year_match else 0
            # Sort by the full graduation date (ISO "YYYY-MM-DD", so a plain
            # string sort is chronological), not just the year: several
            # advisees graduated in the same year and must still order
            # correctly relative to each other.
            sort_date = date if year_match else "0000-00-00"
            institution = resolve_institution(entry)
            if not institution:
                print(f"warning: unknown institution for tesisDirigidas entry (id={entry.get('id')}, "
                      f"claveInstitucionSnp={entry.get('claveInstitucionSnp')}); leaving institution blank",
                      file=sys.stderr)
            items.append({
                "name": name,
                "thesis_title": thesis_title,
                "degree": degree_en,
                "role": role_en,
                "year": year,
                "sort_date": sort_date,
                "institution": institution,
                "repository_url": resolve_repository_url(entry),
            })
        except Exception as exc:
            print(f"warning: skipping malformed tesisDirigidas entry (id={entry.get('id')}): {exc}", file=sys.stderr)
    items.sort(key=lambda a: (a["sort_date"], a["name"]))
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
        if item["scholarurl"]:
            lines.append(f"scholarurl: {yaml_str(item['scholarurl'])}")
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
        if item["institution"]:
            lines.append(f"institution: {yaml_str(item['institution'])}")
        if item["repository_url"]:
            lines.append(f"repository_url: {yaml_str(item['repository_url'])}")
        if item["year"]:
            lines.append(f"year: {item['year']}")
        lines.append("---")
        lines.append("")
        path = out_dir / f"{idx:02d}_alumni.md"
        path.write_text("\n".join(lines), encoding="utf-8")
    return len(items)


def main():
    profile_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "perfil.json"
    if not profile_path.is_file():
        print(f"error: profile file not found: {profile_path}", file=sys.stderr)
        return 1

    try:
        profile = load_profile(profile_path)
    except json.JSONDecodeError as exc:
        print(f"error: {profile_path} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(profile, dict):
        print(f"error: {profile_path} does not contain a JSON object at the top level", file=sys.stderr)
        return 1

    publications = collect_publications(profile)
    n_pub = write_publications(publications, REPO_ROOT / "_publications")

    alumni = collect_alumni(profile)
    n_alumni = write_alumni(alumni, REPO_ROOT / "_alumni")

    print(f"Generated {n_pub} publication(s) in _publications/")
    print(f"Generated {n_alumni} alumni entr{'y' if n_alumni == 1 else 'ies'} in _alumni/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
