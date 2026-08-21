# mgraffg.github.io

## Desarrollo local con Dev Container

Este repositorio incluye una configuración de [Dev Container](https://containers.dev/) para desarrollar el sitio Jekyll sin instalar Ruby ni sus dependencias en la máquina host.

1. Instala la extensión [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) en VS Code.
2. Abre el repositorio en VS Code y ejecuta **"Dev Containers: Reopen in Container"**.
3. Al crear el contenedor se ejecuta automáticamente `bundle install`.
4. Levanta el sitio con:

   ```
   bundle exec jekyll serve
   ```

5. Abre [http://localhost:4000](http://localhost:4000) en el navegador (el puerto 4000 se reenvía automáticamente).

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