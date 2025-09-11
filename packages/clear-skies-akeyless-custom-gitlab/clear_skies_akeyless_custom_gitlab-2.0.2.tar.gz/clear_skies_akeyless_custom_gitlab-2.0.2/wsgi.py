import clearskies

import clearskies_akeyless_custom_gitlab

producer = clearskies_akeyless_custom_gitlab.build_clearskies_akeyless_custom_gitlab_producer()

wsgi = clearskies.contexts.WsgiRef(producer, port=9090)
wsgi()
