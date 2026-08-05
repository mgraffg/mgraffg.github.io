---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
---

{% include base_path %}

La información de educación, experiencia, distinciones y proyectos financiados de esta
sección se generará automáticamente a partir del perfil único de la SECIHTI (ver
[issue #6](https://github.com/mgraffg/mgraffg.github.io/issues/6)) y aún no ha sido
incorporada.

Publications
======
  <ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>

Talks
======
  <ul>{% for post in site.talks reversed %}
    {% include archive-single-talk-cv.html %}
  {% endfor %}</ul>

Teaching
======
  <ul>{% for post in site.teaching reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
