import os
from django.test import TestCase
from async_casbin_adapter.enforcer import get_enforcer
from async_casbin_adapter.models import CasbinRule


def get_fixture(path):
    dir_path = os.path.split(os.path.realpath(__file__))[0] + "/"
    return os.path.abspath(dir_path + path)


async def db_setup():
    await CasbinRule.objects.abulk_create(
        [
            CasbinRule(ptype="p", v0="alice", v1="data1", v2="read"),
            CasbinRule(ptype="p", v0="bob", v1="data2", v2="write"),
            CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="read"),
            CasbinRule(ptype="p", v0="data2_admin", v1="data2", v2="write"),
            CasbinRule(ptype="g", v0="alice", v1="data2_admin"),
        ]
    )


class TestEnforcer(TestCase):
    async def test_get_enforcer_basic(self):
        enforcer = await get_enforcer()
        await enforcer.add_policy("alice", "data1", "read")
        self.assertEqual(enforcer.get_policy(), [["alice", "data1", "read"]])
        self.assertTrue(enforcer.enforce("alice", "data1", "read"))

    async def test_get_enforcer(self):
        await db_setup()
        enforcer = await get_enforcer()

        self.assertEqual(
            enforcer.get_policy(),
            [
                ["alice", "data1", "read"],
                ["bob", "data2", "write"],
                ["data2_admin", "data2", "read"],
                ["data2_admin", "data2", "write"],
            ],
        )
        self.assertTrue(enforcer.enforce("alice", "data1", "read"))
        self.assertFalse(enforcer.enforce("bob", "data1", "read"))
        self.assertTrue(enforcer.enforce("bob", "data2", "write"))
        self.assertTrue(enforcer.enforce("alice", "data2", "read"))
        self.assertTrue(enforcer.enforce("alice", "data2", "write"))
        self.assertFalse(enforcer.enforce("bogus", "data2", "write"))
