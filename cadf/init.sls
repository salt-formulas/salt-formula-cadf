{%- from "cadf/map.jinja" import config with context %}
{%- if pillar.cadf is defined %}

include:
{%- if pillar.cadf.dispatcher.enabled  %}
- cadf.dispatcher
{%- endif %}
{%- if pillar.cadf.dispatcher.enabled  %}
- cadf.listener
{%- endif %}



{%- if pillar.cadf.dispatcher.enabled or pillar.cadf.listener.enabled  %}
cadf_packages:
  pkg.installed:
    - names: {{ config.pkgs }}

{{ config.config_dir }}:
  file.directory:
    - mode: 777
    - user: {{ config.get('user','root') }}
    - group: {{ config.get('group','root') }}
{%- endif %}

{%- endif %}
