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