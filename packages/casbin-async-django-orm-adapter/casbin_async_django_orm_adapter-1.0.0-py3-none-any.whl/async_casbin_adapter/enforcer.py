# Copyright 2025 The casbin Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from django.conf import settings
from django.db import connections
from asgiref.sync import sync_to_async

from casbin import AsyncEnforcer

from .utils import import_class


logger = logging.getLogger(__name__)


def _perform_sync_db_check(db_alias):
    logger.info(f"Performing synchronous DB check for migration on alias '{db_alias}'...")
    connection = connections[db_alias]
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT app, name FROM django_migrations
                WHERE app = 'async_casbin_adapter' AND name = '0001_initial';
                """
            )
            row = cursor.fetchone()

        if not row:
            raise RuntimeError("Async Casbin Adapter initial migration not applied. ")
        logger.info("Synchronous DB check passed.")
        return True
    except Exception as e:
        logger.error(f"Synchronous DB check failed: {e}")
        raise


async def get_enforcer(db_alias=None):
    """
    An asynchronous factory function for creating and initializing Casbin AsyncEnforcer
    """
    if db_alias is None:
        db_alias = getattr(settings, "CASBIN_DB_ALIAS", "default")

    async_db_check = sync_to_async(_perform_sync_db_check, thread_sensitive=True)
    await async_db_check(db_alias)

    model = getattr(settings, "CASBIN_MODEL")
    adapter_loc = getattr(settings, "ASYNC_CASBIN_ADAPTER", "async_casbin_adapter.adapter.AsyncAdapter")
    adapter_args = getattr(settings, "CASBIN_ADAPTER_ARGS", tuple())
    Adapter = import_class(adapter_loc)
    adapter = Adapter(db_alias, *adapter_args)

    enforcer = AsyncEnforcer(model, adapter)

    watcher_loc = getattr(settings, "CASBIN_WATCHER", None)
    if watcher_loc:
        Watcher = import_class(watcher_loc)
        enforcer.set_watcher(Watcher())

    role_manager_loc = getattr(settings, "CASBIN_ROLE_MANAGER", None)
    if role_manager_loc:
        RoleManager = import_class(role_manager_loc)
        enforcer.set_role_manager(RoleManager())

    await enforcer.load_policy()

    logger.info("Casbin AsyncEnforcer initialized successfully.")
    return enforcer
