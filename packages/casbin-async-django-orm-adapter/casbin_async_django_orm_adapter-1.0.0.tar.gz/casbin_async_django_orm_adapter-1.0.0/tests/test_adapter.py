import os
from casbin import AsyncEnforcer
import simpleeval

from django.test import TestCase
from async_casbin_adapter.models import CasbinRule
from async_casbin_adapter.adapter import AsyncAdapter


def get_fixture(path):
    dir_path = os.path.split(os.path.realpath(__file__))[0] + "/"
    return os.path.abspath(dir_path + path)


async def get_async_enforcer():
    adapter = AsyncAdapter()

    await CasbinRule.objects.abulk_create(
        [
            CasbinRule(ptype="p", v0="alice", v1="data1", v2="read"),
            CasbinRule(ptype="p", v0="bob", v1="data2", v2="write"),
            CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="read"),
            CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="write"),
            CasbinRule(ptype="g", v0="alice", v1="data2_admin"),
        ]
    )

    enforcer = AsyncEnforcer(get_fixture("rbac_model.conf"), adapter)
    await enforcer.load_policy()
    return enforcer


class TestAsyncAdapter(TestCase):
    async def test_enforcer_basic(self):
        e = await get_async_enforcer()
        self.assertTrue(e.enforce("alice", "data1", "read"))
        self.assertFalse(e.enforce("bob", "data1", "read"))
        self.assertTrue(e.enforce("bob", "data2", "write"))
        self.assertTrue(e.enforce("alice", "data2", "read"))
        self.assertTrue(e.enforce("alice", "data2", "write"))

    async def test_add_policy(self):
        adapter = AsyncAdapter()
        e = AsyncEnforcer(get_fixture("rbac_model.conf"), adapter)

        try:
            self.assertFalse(e.enforce("alice", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data1", "read"))
            self.assertFalse(e.enforce("bob", "data2", "write"))
            self.assertFalse(e.enforce("alice", "data2", "read"))
            self.assertFalse(e.enforce("alice", "data2", "write"))
        except simpleeval.NameNotDefined:
            pass

        await adapter.add_policy(sec="p", ptype="p", rule=["alice", "data1", "read"])
        await adapter.add_policy(sec="p", ptype="p", rule=["bob", "data2", "write"])
        await adapter.add_policy(sec="p", ptype="p", rule=["data2_admin", "data2", "read"])
        await adapter.add_policy(sec="p", ptype="p", rule=["data2_admin", "data2", "write"])
        await adapter.add_policy(sec="g", ptype="g", rule=["alice", "data2_admin"])

        await e.load_policy()

        self.assertTrue(e.enforce("alice", "data1", "read"))
        self.assertFalse(e.enforce("bob", "data1", "read"))
        self.assertTrue(e.enforce("bob", "data2", "write"))
        self.assertTrue(e.enforce("alice", "data2", "read"))
        self.assertTrue(e.enforce("alice", "data2", "write"))
        self.assertFalse(e.enforce("bogus", "data2", "write"))

    async def test_save_policy(self):
        enforcer_for_model = AsyncEnforcer(get_fixture("rbac_model.conf"), get_fixture("rbac_policy.csv"))
        await enforcer_for_model.load_policy()
        model = enforcer_for_model.model

        adapter = AsyncAdapter()
        await adapter.save_policy(model)
        e = AsyncEnforcer(get_fixture("rbac_model.conf"), adapter)
        await e.load_policy()

        self.assertTrue(e.enforce("alice", "data1", "read"))
        self.assertFalse(e.enforce("bob", "data1", "read"))
        self.assertTrue(e.enforce("bob", "data2", "write"))
        self.assertTrue(e.enforce("alice", "data2", "read"))
        self.assertTrue(e.enforce("alice", "data2", "write"))

    async def test_autosave_off_doesnt_persist_to_db(self):
        adapter = AsyncAdapter()
        e = AsyncEnforcer(get_fixture("rbac_model.conf"), adapter)

        e.enable_auto_save(False)
        await e.add_policy("alice", "data1", "write")
        await e.load_policy()
        policies = e.get_policy()

        self.assertListEqual(policies, [])

    async def test_autosave_on_persists_to_db(self):
        adapter = AsyncAdapter()
        e = AsyncEnforcer(get_fixture("rbac_model.conf"), adapter)

        e.enable_auto_save(True)
        await e.add_policy("alice", "data1", "write")
        await e.load_policy()
        policies = e.get_policy()
        self.assertListEqual(policies, [["alice", "data1", "write"]])

    async def test_autosave_on_persists_remove_action_to_db(self):
        adapter = AsyncAdapter()
        e = AsyncEnforcer(get_fixture("rbac_model.conf"), adapter)
        await e.add_policy("alice", "data1", "write")
        await e.load_policy()
        self.assertListEqual(e.get_policy(), [["alice", "data1", "write"]])

        e.enable_auto_save(True)
        await e.remove_policy("alice", "data1", "write")
        await e.load_policy()
        self.assertListEqual(e.get_policy(), [])

    async def test_remove_filtered_policy(self):
        e = await get_async_enforcer()

        await e.remove_filtered_policy(0, "data2_admin")
        await e.load_policy()
        self.assertListEqual(e.get_policy(), [["alice", "data1", "read"], ["bob", "data2", "write"]])

    def test_str(self):
        rule = CasbinRule(ptype="p", v0="alice", v1="data1", v2="read")
        self.assertEqual(str(rule), "p, alice, data1, read")

    async def test_repr(self):
        rule = CasbinRule(ptype="p", v0="alice", v1="data1", v2="read")
        self.assertEqual(repr(rule), '<CasbinRule None: "p, alice, data1, read">')

        await rule.asave()
        self.assertRegex(repr(rule), r'<CasbinRule \d+: "p, alice, data1, read">')
