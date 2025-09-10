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

from casbin import persist
from casbin.persist.adapters.asyncio import AsyncAdapter
from django.db.utils import OperationalError, ProgrammingError

from .models import CasbinRule

logger = logging.getLogger(__name__)


class AsyncAdapter(AsyncAdapter):
    """the interface for Casbin async adapters."""

    def __init__(self, db_alias="default"):
        self.db_alias = db_alias

    async def load_policy(self, model):
        """loads all policy rules from the storage."""
        try:
            lines = CasbinRule.objects.using(self.db_alias).all()

            async for line in lines:
                persist.load_policy_line(str(line), model)
        except (OperationalError, ProgrammingError) as error:
            logger.warning("Could not load policy from database: {}".format(error))

    def _create_policy_line(self, ptype, rule):
        line = CasbinRule(ptype=ptype)
        if len(rule) > 0:
            line.v0 = rule[0]
        if len(rule) > 1:
            line.v1 = rule[1]
        if len(rule) > 2:
            line.v2 = rule[2]
        if len(rule) > 3:
            line.v3 = rule[3]
        if len(rule) > 4:
            line.v4 = rule[4]
        if len(rule) > 5:
            line.v5 = rule[5]
        return line

    async def save_policy(self, model):
        """saves all policy rules to the storage."""
        # this will delete all rules
        await CasbinRule.objects.using(self.db_alias).all().adelete()

        lines = []
        for sec in ["p", "g"]:
            if sec not in model.model.keys():
                continue
            for ptype, ast in model.model[sec].items():
                for rule in ast.policy:
                    lines.append(self._create_policy_line(ptype, rule))

        db_alias = self.db_alias if self.db_alias else "default"
        rows_created = await CasbinRule.objects.using(db_alias).abulk_create(lines)
        return len(rows_created) > 0

    async def add_policy(self, sec, ptype, rule):
        """adds a policy rule to the storage."""
        line = self._create_policy_line(ptype, rule)
        await line.asave()

    async def remove_policy(self, sec, ptype, rule):
        """removes a policy rule from the storage."""
        query_params = {"ptype": ptype}
        for i, v in enumerate(rule):
            query_params["v{}".format(i)] = v

        rows_deleted, _ = await CasbinRule.objects.using(self.db_alias).filter(**query_params).adelete()
        return rows_deleted > 0

    async def remove_filtered_policy(self, sec, ptype, field_index, *field_values):
        """removes policy rules that match the filter from the storage."""
        query_params = {"ptype": ptype}
        if not (0 <= field_index <= 5):
            return False
        if not (1 <= field_index + len(field_values) <= 6):
            return False
        for i, v in enumerate(field_values):
            query_params["v{}".format(i + field_index)] = v

        rows_deleted, _ = await CasbinRule.objects.using(self.db_alias).filter(**query_params).adelete()
        return rows_deleted > 0
