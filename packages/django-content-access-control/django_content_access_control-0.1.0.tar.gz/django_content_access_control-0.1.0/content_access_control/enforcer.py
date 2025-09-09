import logging
from django.conf import settings

from casbin import Enforcer

from .utils import import_class

logger = logging.getLogger(__name__)


class ProxyEnforcer(Enforcer):
    _initialized = False
    db_alias = "default"

    def __init__(self, *args, **kwargs):
        if self._initialized:
            super().__init__(*args, **kwargs)
        else:
            logger.info(
                "Deferring casbin enforcer initialisation until django is ready"
            )

    def _load(self):
        if self._initialized is False:
            logger.info("Performing deferred casbin enforcer initialisation")
            self._initialized = True
            model = getattr(settings, "CASBIN_MODEL")
            adapter_loc = getattr(
                settings, "CASBIN_ADAPTER", "content_access_control.adapter.Adapter"
            )
            adapter_args = getattr(settings, "CASBIN_ADAPTER_ARGS", tuple())
            self.db_alias = getattr(settings, "CASBIN_DB_ALIAS", "default")
            Adapter = import_class(adapter_loc)
            adapter = Adapter(self.db_alias, *adapter_args)

            super().__init__(model, adapter)
            logger.debug("Casbin enforcer initialised")

            watcher = getattr(settings, "CASBIN_WATCHER", None)
            if watcher:
                self.set_watcher(watcher)

            role_manager = getattr(settings, "CASBIN_ROLE_MANAGER", None)
            if role_manager:
                self.set_role_manager(role_manager)

    def __getattribute__(self, name):
        safe_methods = ["__init__", "_load", "_initialized", "db_alias"]
        if not super().__getattribute__("_initialized") and name not in safe_methods:
            self._load()

        return super().__getattribute__(name)
