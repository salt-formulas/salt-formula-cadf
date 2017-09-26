{%- from "cadf/map.jinja" import config with context %}
{%- from "cadf/map.jinja" import dispatcher with context %}
{%- from "cadf/map.jinja" import listener with context %}
{%- if dispatcher.enabled or listener.enabled  %}

/etc/logrotate.d/cadf:
  file.managed:
    - source: salt://cadf/files/logrotate
    - template: jinja
    - user: {{ config.get('user','root') }}
    - group: {{ config.get('group','root') }}
    - mode: 644

{%- endif %}
