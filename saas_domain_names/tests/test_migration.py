# License AGPL-3.0 or later.
import tempfile
from pathlib import Path
from unittest.mock import patch, PropertyMock
from odoo.tests import TransactionCase, tagged
from odoo.addons.host2db.override import Host2DBConfig, host2db_config, db_filter


@tagged("post_install", "-at_install")
class TestDomainMigration(TransactionCase):
    def test_create_reassign_delete_and_cross_worker_reload(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(Host2DBConfig, "config_filename", new_callable=PropertyMock, return_value=str(Path(directory) / "host2db.ini")):
            env = self.env(context={**self.env.context, "queue_job__no_delay": True})
            operator = env.ref("saas.local_operator")
            first, second = env["saas.domain.name"].create([
                {"name": "first.audit.test", "operator_id": operator.id},
                {"name": "second.audit.test", "operator_id": operator.id},
            ])
            build = env["saas.db"].create({"name": "audit-domain-create", "operator_id": operator.id, "domain_name_id": first.id})
            self.assertEqual(host2db_config.get_db_by_host(first.name), build.name)
            self.assertEqual(db_filter([build.name], host=first.name), [build.name])
            self.assertEqual(db_filter(["another-database"], host=first.name), [])
            build.domain_name_id = second
            self.assertFalse(host2db_config.get_db_by_host(first.name))
            self.assertEqual(host2db_config.get_db_by_host(second.name), build.name)
            other_worker = Host2DBConfig()
            other_worker.assign_host_to_db(second.name, "new-audit-database")
            self.assertEqual(host2db_config.get_db_by_host(second.name), "new-audit-database")
            second.unlink()
            self.assertFalse(host2db_config.get_db_by_host("second.audit.test"))
