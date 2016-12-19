cadf:
  config:
    user: root
    group: root
    config_dir:
      /tmp
  dispatcher:
    enabled: true
    #cron:
    #  hour: '*'
    #  minute: '*/1'
    messaging:
      host: 127.0.0.1
      port: 5672
      user: test
      password: password
      vhost: /openstack
      queue: notifications.info
      topic: notifications
    http_server:
      url: 192.168.1.24:33333
  listener:
    enabled: true
