{%- from "cadf/map.jinja" import config with context %}
{%- if pillar.cadf is defined %}

include:
- cadf.dispatcher
- cadf.listener

{%- if pillar.cadf.dispatcher.enabled or pillar.cadf.listener.enabled  %}

cadf_packages:
  pkg.installed:
    - names: {{ config.pkgs }}

{{ config.config_dir }}:
  file.directory:
    - mode: 755
    - user: {{ config.get('user','root') }}
    - group: {{ config.get('group','root') }}

/var/log/cadf:
  file.directory:
    - mode: 755
    - user: {{ config.get('user','root') }}
    - group: {{ config.get('group','root') }}

{%- endif %}

{%- endif %}

