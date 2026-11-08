# mgraffg.github.io

## Desarrollo local

El sitio Jekyll se desarrolla con el Ruby 3.4 instalado localmente mediante Homebrew.

1. Instala Ruby 3.4: `brew install ruby@3.4`.
2. Pon `/usr/local/opt/ruby@3.4/bin` al inicio del `PATH`. El Ruby del sistema o el Ruby 4.0 predeterminado no funcionan con las gemas de este sitio.
3. Instala las dependencias:

   ```
   PATH="/usr/local/opt/ruby@3.4/bin:$PATH" bundle install
   ```

4. Levanta el sitio con:

   ```
   PATH="/usr/local/opt/ruby@3.4/bin:$PATH" LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bundle exec jekyll serve -l -H localhost
   ```

5. Abre [http://localhost:4000](http://localhost:4000) en el navegador.

Para solo construir el sitio (sin servirlo):

```
PATH="/usr/local/opt/ruby@3.4/bin:$PATH" LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 bundle exec jekyll build
```

## Generar Publications y Alumni desde el perfil único de SECIHTI

El script [`scripts/perfil_to_site.py`](scripts/perfil_to_site.py) lee `perfil.json` (el JSON del perfil único, descargado manualmente desde rizoma.conahcyt.mx → "Compartir Mi Perfil Único") y genera automáticamente el contenido de dos colecciones:

- `_publications/`: una entrada por cada publicación científica marcada como "producto principal" (destacada) en el perfil único.
- `_alumni/`: una entrada por cada tesis dirigida en la que el rol fue Director(a) o Co-Director(a).

**Entradas:** `perfil.json` en la raíz del repositorio (no se versiona; ver `.gitignore` — nunca debe subirse a git porque contiene datos personales sensibles como CURP y fotografía).

**Salidas:** archivos Markdown en `_publications/` y `_alumni/`, con el front matter que Jekyll/academicpages espera (`title`, `collection`, `category`, `date`, `venue`, `citation`, `paperurl`, `scholarurl` para publicaciones; `title`, `collection`, `thesis_title`, `degree`, `role`, `institution`, `repository_url`, `year` para alumni). Ambas colecciones tienen `output: false` en `_config.yml`: no generan una página por cada publicación/alumno, solo se listan en `/publications/` y `/alumni/` (agrupadas por grado académico y numeradas de forma descendente por fecha completa, en el caso de Alumni). El script solo extrae metadatos bibliográficos/académicos pensados para ser públicos; nunca lee ni escribe campos sensibles (CURP, fotografía, enlaces internos a documentos como `cloud.secihti.mx`/`tlapiakali.conahcyt.mx` — `repository_url` solo se llena si la liga de la tesis apunta a un dominio distinto de esos).

**Dependencias:** solo Python 3 (biblioteca estándar), sin paquetes adicionales.

**Ejecución:** desde la raíz del repositorio,

```
python3 scripts/perfil_to_site.py
```

Cada ejecución regenera por completo el contenido de `_publications/` y `_alumni/` a partir del `perfil.json` actual (borra las entradas generadas previamente antes de escribir las nuevas), por lo que no requiere intervención manual adicional. Vuelve a correrlo cada vez que se actualice `perfil.json`.

Para el detalle de la estructura de `perfil.json`, qué campos se usan y a qué sección corresponden (y sugerencias de otras secciones a evaluar), ver [`scripts/PERFIL_JSON.md`](scripts/PERFIL_JSON.md).