# copyright 2021 Florent Cayré (Villejuif, FRANCE), all rights reserved.
# contact http://www.cubicweb.org/project/cubicweb-i18nfield
# mailto:Florent Cayré <florent.cayre@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime as dt, timedelta as td
import pytz
from cubicweb import ValidationError, Unauthorized
from cubicweb_web.devtools.testlib import WebCWTC
from cubicweb_web.views.autoform import InlinedFormField

from cubicweb_i18nfield.utils import LANGS_BY_CODE, LANGS_BY_EID


class I18nFieldTC(WebCWTC):
    def setup_database(self):
        super().setup_database()
        with self.admin_access.repo_cnx() as cnx:
            self.en = cnx.create_entity("I18nLang", code="en", name="English")
            self.fr = cnx.create_entity("I18nLang", code="fr", name="French")
            self.de = cnx.create_entity("I18nLang", code="de", name="German")
            cnx.transaction_data["i18nfield_lang"] = {"title": "fr"}
            self.card = cnx.create_entity("Card", title="salut", ref_lang=self.fr)
            cnx.commit()

    def create_card(self, cnx, title):
        return cnx.create_entity("Card", title=title, ref_lang=self.fr)

    def test_entity(self):
        # Check translatable printable_value and related adapter's methods
        with self.admin_access.repo_cnx() as cnx:
            card = cnx.find("Card", eid=self.card.eid).one()
            tr_en = cnx.create_entity(
                "Translation",
                value="hello",
                lang=self.en,
                of_field=card.reverse_i18nfield_of[0],
            )
            cnx.commit()
            cnx.transaction_data["i18nfield_target_lang"] = "fr"
            self.assertEqual(card.dc_title(), "salut")
            cnx.transaction_data["i18nfield_target_lang"] = "en"
            self.assertEqual(card.dc_title(), "hello")
            # Check I18nField methods
            field = card.reverse_i18nfield_of[0]
            self.assertEqual(field.translation("en").value, "hello")
            self.assertEqual(field.original_value(), "salut")
            # Check Translation methods
            self._set_field_last_edited(field, dt.now(pytz.utc))
            self.assertTrue(tr_en.is_outdated())
            # Check adapter's translation_infos method
            adapted = card.cw_adapt_to("translatable_entity")
            tr_infos = adapted.translation_infos()
            # - english
            en_infos = tr_infos[0]
            self.assertEqual(en_infos[0].eid, self.en.eid)
            self.assertEqual(len(en_infos[1]), 1)  # one field only
            self.assertEqual(en_infos[1][0][0].eid, tr_en.eid)
            self.assertEqual(en_infos[1][0][1].eid, field.eid)
            # - german
            de_infos = tr_infos[1]
            self.assertEqual(de_infos[0].eid, self.de.eid)
            self.assertEqual(de_infos[1], None)

    def _assert_is_fresh(self, field):
        field.cw_clear_all_caches()
        self.assertLess(dt.now(pytz.utc) - field.last_edited, td(seconds=10))

    def _set_field_last_edited(self, field, date):
        with self.repo.internal_cnx() as cnx:
            cnx.execute(
                "SET X last_edited %(d)s WHERE X eid %(x)s", {"x": field.eid, "d": date}
            )
            cnx.commit()
        field.cw_clear_all_caches()
        self.assertEqual(field.last_edited, date)

    def test_translatable_hooks(self):
        # check creation hook: I18nField creation with supplied lang...
        with self.admin_access.repo_cnx() as cnx:
            card = cnx.find("Card", eid=self.card).one()
            self.assertTrue(card.reverse_i18nfield_of)
            field = card.reverse_i18nfield_of[0]
            # ... and correct last_edited date
            self._assert_is_fresh(field)
            # edition hook: last_edited must be updated
            self._set_field_last_edited(field, dt.now(pytz.utc) - td(days=10))
            card.cw_set(title="bonjour")
            cnx.commit()
            field.cw_clear_all_caches()
            self.assertLess(dt.now(pytz.utc) - field.last_edited, td(seconds=1))
            # deletion hook
            cnx.execute("DELETE Card C WHERE C eid %(c)s", {"c": card.eid})
            cnx.commit()
            self.assertFalse(
                cnx.execute("Any F WHERE F eid %(x)s", {"x": field.eid}).rowcount
            )

    def test_lang_cache_dicts_hooks(self):
        with self.admin_access.repo_cnx() as cnx:
            init_codes = ["de", "en", "fr"]
            init_eids = sorted([self.en.eid, self.fr.eid, self.de.eid])
            self.assertEqual(sorted(LANGS_BY_CODE.keys()), init_codes)
            self.assertEqual(sorted(LANGS_BY_EID.keys()), init_eids)
            # test creation
            sp = cnx.create_entity("I18nLang", code="sp", name="Spanish")
            cnx.commit()
            self.assertEqual(sorted(LANGS_BY_CODE.keys()), init_codes + ["sp"])
            self.assertEqual(sorted(LANGS_BY_EID.keys()), init_eids + [sp.eid])
            # test update
            sp.cw_set(code="sq")
            cnx.commit()
            self.assertEqual(sorted(LANGS_BY_CODE.keys()), init_codes + ["sq"])
            self.assertEqual(sorted(LANGS_BY_EID.keys()), init_eids + [sp.eid])
            # test remove
            cnx.execute('DELETE I18nLang L WHERE L code "sq"')
            cnx.commit()
            self.assertEqual(sorted(LANGS_BY_CODE.keys()), init_codes)
            self.assertEqual(sorted(LANGS_BY_EID.keys()), init_eids)

    def test_constraint(self):
        with self.admin_access.repo_cnx() as cnx:
            card = cnx.find("Card", eid=self.card.eid).one()
            cnx.create_entity(
                "Translation",
                value="salut",
                lang=self.fr.eid,
                of_field=card.reverse_i18nfield_of[0],
            )
            with self.assertRaises(ValidationError):
                cnx.commit()

    def test_permission_admin_cannot_add_i18nfield(self):
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(Unauthorized) as wraperr:
                cnx.create_entity(
                    "I18nField", field_name="synopsis", i18nfield_of=self.card.eid
                )
                self.assertEqual(
                    str(wraperr.exception),
                    (
                        "You are not allowed to perform add operation on "
                        "relation I18nField i18nfield_of Card"
                    ),
                )

    def test_unique_together(self):
        with self.repo.internal_cnx() as cnx:
            with self.assertRaises(ValidationError) as wraperr:
                cnx.create_entity(
                    "I18nField", field_name="title", i18nfield_of=self.card.eid
                )
                self.assertDictEqual(
                    {
                        "i18nfiaeld_of": "i18nfield_of is part of violated unicity constraint",
                        "field_name": "field_name is part of violated unicity constraint",
                        "unicity constraint": "some relations violate a unicity constraint",
                    },
                    wraperr.exception.args[1],
                )

    def _first_inlined_form(self, form):
        return [
            field.view.form
            for field in form.fields
            if isinstance(field, InlinedFormField)
        ][0]

    def _card_form(self, cnx, vid):
        card = cnx.find("Card", eid=self.card.eid).one()
        return cnx.vreg["forms"].select(vid, cnx, rset=card.as_rset())

    def test_formfield(self):
        """translation value field and widget classes must be the same as the
        translated field of the original entity"""
        with self.admin_access.web_request() as req:
            req.form["lang_code"] = "fr"
            # get card translation value field
            tr_card_form = self._card_form(req, "translate_entity")
            title_form = self._first_inlined_form(tr_card_form)
            tr_form = self._first_inlined_form(title_form)
            tr_card_field = tr_form.field_by_name("value", "subject")
            # get card title field
            std_form = self._card_form(req, "edition")
            std_field = std_form.field_by_name("title", "subject")
            # check field and widget classes
            self.assertEqual(type(tr_card_field), type(std_field))
            self.assertEqual(type(tr_card_field.widget), type(std_field.widget))

    def test_adaptable_i18field(self):
        """test  _TranslatableEntityAdapter.i18nfield method"""
        with self.admin_access.repo_cnx() as cnx:
            card = cnx.find("Card", eid=self.card.eid).one()
            adapted = card.cw_adapt_to("translatable_entity")
            self.assertEqual(adapted.i18nfield("title").field_name, "title")

    def test_translatable_entity_udpate(self):
        """test TranslatableEntityUpdateHook"""
        with self.admin_access.repo_cnx() as cnx:
            card1 = self.create_card(cnx, "title")
            card2 = self.create_card(cnx, "card2")
            cnx.commit()
            i18ntitle1 = card1.cw_adapt_to("translatable_entity").i18nfield("title")
            i18ntitle2 = card2.cw_adapt_to("translatable_entity").i18nfield("title")
            initial_date1 = i18ntitle1.last_edited
            initial_date2 = i18ntitle2.last_edited
            # check title i18nfield last_edited date is not changed when
            # another card1 attribute is edited
            card1.cw_set(synopsis="synopsis1")
            cnx.commit()
            i18ntitle1.cw_clear_all_caches()
            self.assertEqual(initial_date1, i18ntitle1.last_edited)
            # check title1 i18nfield last_edited date is changed when card1's
            # title is edited
            initial_date1 = i18ntitle1.last_edited
            card1.cw_set(title="card1")
            cnx.commit()
            i18ntitle1.cw_clear_all_caches()
            self.assertLess(initial_date1, i18ntitle1.last_edited)
            # check card2's title i18nfield last_edited date was never updated
            i18ntitle2.cw_clear_all_caches()
            self.assertEqual(initial_date2, i18ntitle2.last_edited)


if __name__ == "__main__":
    from unittest import main

    main()
