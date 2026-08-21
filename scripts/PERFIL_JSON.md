# Estructura de `perfil.json` y su mapeo al sitio

`perfil.json` es la exportación JSON del perfil único de SECIHTI (antes CONACYT),
descargada manualmente desde rizoma.conahcyt.mx → "Compartir Mi Perfil Único".
Vive en la raíz del repositorio, **nunca se versiona** (ver `.gitignore` y
CLAUDE.md) porque contiene datos personales sensibles, y solo se usa como
entrada local para [`scripts/perfil_to_site.py`](perfil_to_site.py).

Este documento describe, a alto nivel, las partes del JSON que el script
consume y a qué sección del sitio corresponde cada una, según lo acordado en
el issue #6 (y el mapa de secciones del issue #4/#9).

## Estructura de alto nivel

```
{
  "perfil": {
    "id", "cvu", "nivelAcademico", "titulo",
    "principal": { "nombre", "primerApellido", "segundoApellido", "curp", "fotografia", ... },
    "tesisDirigidas": [ {...}, ... ],
    "cursosImpartidos": [ {...}, ... ],
    "trayectoriaAcademica": [ {...}, ... ],
    "trayectoriaProfesional": [ {...}, ... ],
    "logros": [ {...}, ... ],
    "divulgacion": [ {...}, ... ],
    "idiomaLengua": { "idiomas": [...] },
    "estancias": [ {...}, ... ],
    "formacionContinua": { "cursos": [...] },
    "evaluacionesOtorgadas": [ {...}, ... ],
    ...
  },
  "aportaciones": {
    "articulosCientifica": [ {...}, ... ],
    "capitulosCientifica": [ {...}, ... ],
    "librosCientifica": [ {...}, ... ],
    "memoriasCongresos": [ {...}, ... ],
    "desarrolloTecnologicoInnovacion": [ {...}, ... ],
    "transferenciaTecnologica": [ {...}, ... ],
    ...
  },
  "filtro": "...",
  "nombreInstitucionReceptora": "..."
}
```

`perfil.principal` y varios campos de nivel superior contienen datos que
**nunca deben usarse ni exponerse**: `curp` (identificador oficial mexicano),
`fotografia` (imagen codificada), y cualquier `documento.uri` que apunte a
almacenamiento interno (`cloud.secihti.mx`, `tlapiakali.conahcyt.mx`) — esos
enlaces están ligados a la cuenta y no son para consumo público.

## Campos usados actualmente y su sección destino

### Publications ← `aportaciones.{articulosCientifica, capitulosCientifica, librosCientifica, memoriasCongresos}`

Solo se incluyen las entradas con `productoPrincipal: true` (el criterio de
"destacada" del issue #6). Campos leídos por entrada:

| Campo JSON | Uso |
|---|---|
| `titulo` | Título de la publicación (se conserva verbatim, incluso si está en español — es el título real de la obra citada) |
| `nombreRevista` / `tituloLibro` | `venue` |
| `anio` | Año → `date` (se usa `YYYY-01-01`, el JSON no trae mes/día) |
| `autores[].{nombre, primerApellido, segundoApellido}` | Lista de autores para construir `citation` |
| `doi` | `paperurl` (se omite si no existe; nunca se usa `documento.uri`) |
| `cita.urlCita` | `scholarurl`, enlace a la cita específica en Google Scholar (se omite si no existe) |

La colección `publications` tiene `output: false` en `_config.yml`: cada
entrada es solo un registro de datos, no genera su propia página. `/publications/`
las lista todas juntas, dejando claro que son las publicaciones **destacadas**
del perfil único (no un listado exhaustivo).

Mapeo de bucket a `category` (coincide con `publication_category` en `_config.yml`):

| Bucket JSON | `category` |
|---|---|
| `articulosCientifica` | `manuscripts` |
| `capitulosCientifica`, `librosCientifica` | `books` |
| `memoriasCongresos` | `conferences` |

### Alumni ← `perfil.tesisDirigidas`

Solo se incluyen entradas cuyo `rol.nombre` sea `Director(a)` o
`Co-Director (a)` (se excluye explícitamente `Revisor(a)`, que no es dirección
de tesis).

| Campo JSON | Uso |
|---|---|
| `nombre`, `primerApellido`, `segundoApellido` | Nombre completo del alumno → `title` |
| `titulo` | Título de la tesis → `thesis_title` (verbatim) |
| `gradoAcademico.nombre` | Grado → `degree` (traducido: Maestría → Master's, Doctorado → Ph.D.) |
| `rol.nombre` | `role` (Director/Co-Director, traducido a inglés) |
| `fechaObtencionGrado` (o `fechaAprobacion` si falta) | Año → `year`; la fecha completa (`YYYY-MM-DD`) se usa además como clave de orden (ver abajo) |
| `claveInstitucionSnp` | `institution`, resuelto mediante una tabla fija en el script (ver abajo) |
| `documento.uri` | `repository_url`, solo si el dominio no es de almacenamiento privado (ver abajo) |

El orden de despliegue (y por lo tanto la numeración descendente en
`/alumni/`) usa la **fecha completa** de graduación, no solo el año: dos
personas pueden haberse titulado el mismo año pero en fechas distintas
(p. ej. Jose Ortiz Bejar, 2020-06-23, se tituló antes que Claudia Nayelli
Sánchez Gómez, 2020-08-04), y deben ordenarse por esa fecha exacta.

**Sobre `repository_url`:** `documento.uri` en `tesisDirigidas` casi siempre
apunta a `cloud.secihti.mx` (o `tlapiakali.conahcyt.mx`): almacenamiento
personal ligado a la cuenta, no un repositorio institucional público (los
nombres de archivo son cosas como `Claudia.pdf` o el oficio interno de
asesorías, no un registro de repositorio). El script solo usa esa URL como
liga a la tesis cuando su dominio **no** es uno de esos dos; si el único
enlace disponible es privado, `repository_url` se deja vacío. Al día de hoy
las 23 tesis dirigidas/co-dirigidas solo tienen el enlace privado, así que
ninguna entrada generada trae `repository_url`.

**Sobre `institution`:** `perfil.json` identifica la institución de cada tesis
con un código interno del catálogo SNP (`claveInstitucionSnp`), no con un
nombre. El JSON no trae ningún catálogo código→nombre, así que
`perfil_to_site.py` usa una tabla fija (`INSTITUTION_SNP_CODES`) con los
únicos dos códigos que aparecen en tesis dirigidas o co-dirigidas: `37` →
INFOTEC y `138` → Universidad Michoacana de San Nicolás de Hidalgo (UMSNH),
confirmados manualmente. Si un futuro `perfil.json` trae un código nuevo, el
script lo deja sin resolver (advertencia en stderr, campo `institution`
vacío) hasta que se agregue a la tabla.

Igual que en Publications, la colección `alumni` tiene `output: false`: no
hay una página por alumno. `/alumni/` los agrupa por grado académico
(Ph.D. primero, luego Master's).

## Otras secciones del JSON — sugerencias para analizar (no implementadas)

El issue #6 pide sugerir, para su análisis, qué otra información del perfil
único podría dar bien en el sitio. Con base en lo que contiene `perfil.json`
hoy, estos son los candidatos más claros — ninguno se implementó, quedan
pendientes de una decisión explícita antes de tocarlos:

- **`aportaciones.desarrolloTecnologicoInnovacion`** (4 entradas, todas
  destacadas): son exactamente los proyectos que ya existen, curados a mano,
  en `_software/` (CompStats, EvoMSA, microTC, más un "Índice de Movilidad"
  que no tiene entrada de software todavía). Podría usarse para *enriquecer*
  las descripciones existentes o para detectar software del perfil único que
  aún no está en `_software/`, pero no debe generarlas automáticamente sin
  revisión: el texto en el JSON está en español y el estilo/curación actual
  de `_software/` es manual.
- **`perfil.divulgacion`** (23 entradas): actividades de divulgación
  científica. Podrían complementar `_talks/`, que ya incluye pláticas de
  divulgación curadas a mano (issue #17); antes de generarlas automáticamente
  habría que decidir cómo evitar duplicar charlas que ya están cargadas.
- **`perfil.logros`** (10 entradas) y **`perfil.trayectoriaAcademica`** /
  **`trayectoriaProfesional`**: distinciones y trayectoria — información que
  cabría en la sección "Mario Graff" (`about.md`), pero requeriría redactar
  texto narrativo en inglés, no una simple conversión de campos.
- **`perfil.cursosImpartidos`** (98 entradas): historial de cursos impartidos.
  Es un volumen alto y granular; `_teaching`/Course Textbooks ya está
  simplificado a dos libros de texto (issue #16), así que probablemente no
  aplica tal cual.

## Robustez

El script tolera y omite (con una advertencia en stderr, sin detener la
ejecución) casos como: JSON inválido, `perfil.json` sin las llaves
esperadas, valores `null` donde se esperaba una lista/objeto, entradas que no
son objetos, y entradas de publicación/tesis sin título o sin nombre. Nunca
falla de forma silenciosa: cada entrada omitida se reporta.
