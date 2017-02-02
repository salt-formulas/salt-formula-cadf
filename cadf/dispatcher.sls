{%- from "cadf/map.jinja" import config with context %}
{%- from "cadf/map.jinja" import dispatcher with context %}
{%- if dispatcher.enabled %}


{{ config.config_dir }}/cadf_dispatcher.py:
  file.managed:
    - source: salt://cadf/files/cadf_dispatcher.py
    - template: jinja
    - mode: 644
    - user: {{ config.get('user','root') }}
    - group: {{ config.get('group','root') }}
    - require:
        - file: {{ config.config_dir }}

{{ config.config_dir }}/cadf_dispatcher.conf:
  file.managed:
    - source: salt://cadf/files/cadf_dispatcher.conf
    - template: jinja
    - mode: 644
    - user: {{ config.get('user','root') }}
    - group: {{ config.get('group','root') }}
    - require:
        - file: {{ config.config_dir }}


dispatcher_cron:
  cron.present:
    - name: "python {{ config.config_dir }}/cadf_dispatcher.py {{ config.config_dir }}/cadf_dispatcher.conf"
    - identifier: cadf_dispatcher
    - hour: "{{ dispatcher.cron.hour  }}"
    - minute: "{{ dispatcher.cron.minute  }}"
    - user: "{{ config.get('user','root') }}"
    - require:
      - file: {{ config.config_dir }}/cadf_dispatcher.py
      - pkg: cadf_packages

cron_path:
  cron.env_present:
    - name: PATH
    - value: "/bin:/sbin:/usr/bin:/usr/sbin"
    - require:
      - pkg: cadf_packages

{%- else %}

distpatcher_cron:
  cron.absent:
    - identifier: cadf_dispatcher
    - user: "{{ config.get('user','root') }}"
    - require:
      - pkg: cadf_packages

{% endif %}

