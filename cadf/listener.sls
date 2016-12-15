{%- from "cadf/map.jinja" import config with context %}
{%- from "cadf/map.jinja" import listener with context %}
{%- from "cadf/map.jinja" import pkgs with context %}

{%- if listener.enabled %}

{{ config.config_dir }}/cadf_listener.py:
  file.managed:
    - source: salt://cadf/files/cadf_listener.py
    - template: jinja
    - mode: 644
    - user: {{ config.get('user','root') }}
    - group: {{ config.get('group','root') }}

{%- endif %}
