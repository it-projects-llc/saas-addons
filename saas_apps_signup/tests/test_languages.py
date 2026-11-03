# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from unittest.mock import patch

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDatabaseLanguages(TransactionCase):
    def test_selection_includes_english_and_preferred(self):
        languages = self.env["saas.db"]._get_signup_languages(
            ["fr_FR", "de_DE", "fr_FR"], "ru_RU"
        )
        self.assertEqual(set(languages.mapped("code")), {"en_US", "fr_FR", "de_DE", "ru_RU"})

    def test_invalid_selection_is_rejected(self):
        for codes in (["not-a-language"], [123], {"code": "fr_FR"}):
            with self.subTest(codes=codes), self.assertRaises(ValidationError):
                self.env["saas.db"]._get_signup_languages(codes)
        for preferred in ("not-a-language", 123):
            with self.subTest(preferred=preferred), self.assertRaises(ValidationError):
                self.env["saas.db"]._get_signup_languages([], preferred)

    def _build(self):
        languages = self.env["saas.db"]._get_signup_languages(["fr_FR", "de_DE"])
        return self.env["saas.db"].new({
            "name": "language-test", "database_language_ids": [Command.set(languages.ids)],
        })

    def test_remote_install_uses_remote_language_ids(self):
        build = self._build()
        remote = [
            {"id": 8001, "code": "en_US", "active": True},
            {"id": 8002, "code": "fr_FR", "active": False},
            {"id": 8003, "code": "de_DE", "active": False},
        ]
        with patch.object(type(build), "execute_kw", side_effect=[remote, 42, {}]) as rpc:
            build._install_database_languages()
        self.assertEqual(rpc.call_args_list[1].args, (
            "base.language.install", "create",
            {"lang_ids": [Command.set([8002, 8003])], "overwrite": False},
        ))
        self.assertEqual(rpc.call_args_list[2].args, ("base.language.install", "lang_install", 42))

    def test_installed_languages_are_not_installed_again(self):
        build = self._build()
        remote = [{"id": i, "code": code, "active": True}
                  for i, code in enumerate(("en_US", "fr_FR", "de_DE"), 1)]
        with patch.object(type(build), "execute_kw", return_value=remote) as rpc:
            build._install_database_languages()
        self.assertEqual(rpc.call_count, 1)

    def test_missing_remote_language_is_reported(self):
        build = self._build()
        with patch.object(type(build), "execute_kw", return_value=[]), self.assertRaises(UserError):
            build._install_database_languages()
