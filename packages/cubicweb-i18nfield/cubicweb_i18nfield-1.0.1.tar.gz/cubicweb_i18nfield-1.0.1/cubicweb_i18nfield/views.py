# copyright 2011 Florent Cayré (Villejuif, FRANCE), all rights reserved.
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

"""cubicweb-i18nfield views/forms/actions/components for web ui"""

from six import text_type as unicode
from logilab.mtconverter import xml_escape
from logilab.common.decorators import iclassmethod

from cubicweb import tags
from cubicweb.predicates import (
    adaptable,
    has_permission,
    is_instance,
    match_form_params,
    one_line_rset,
    match_kwargs,
    specified_etype_implements,
)
from cubicweb_web.views import uicfg
from cubicweb_web.action import Action
from cubicweb_web.form import FieldNotFound
from cubicweb_web.formfields import guess_field
from cubicweb_web.formwidgets import HiddenInput
from cubicweb_web.views.editforms import EditionFormView
from cubicweb_web.views.autoform import (
    AutomaticEntityForm as AutoForm,
    InlineEntityEditionFormView,
    InlineEntityCreationFormView,
)
from cubicweb_web.views.formrenderers import EntityInlinedFormRenderer


from cubicweb_web.views import tableview as cw_tableview
from cubicweb.uilib import sgml_attributes
from cubicweb.utils import UStringIO

from cubicweb_i18nfield.utils import LANGS_BY_EID

from cubicweb_web.view import StartupView
from cubicweb_web.httpcache import NoHTTPCacheManager
from cubicweb_web.views.urlrewrite import SimpleReqRewriter, rgx

_ = unicode  # make pylint happier

_AFF = uicfg.autoform_field
_AFF_KWARGS = uicfg.autoform_field_kwargs
_AFS = uicfg.autoform_section
_AFFK = uicfg.autoform_field_kwargs


def lang_from_code(req, code=None):
    code = code or req.form.get("lang_code", req.lang)
    if code is None:
        return None
    rql = "Any L,N WHERE L is I18nLang, L name N, L code %(l)s"
    try:
        return req.execute(rql, {"l": code}).get_entity(0, 0)
    except IndexError:
        raise ValueError(req._('unknown language code "%s"') % code)


class TranslateEntityAction(Action):
    __regid__ = "translate_entity"
    __select__ = (
        adaptable("translatable_entity") & has_permission("update") & one_line_rset()
    )

    submenu = _("translations")
    category = "mainactions"

    def actual_actions(self):
        entity = self.cw_rset.get_entity(0, 0)
        _infos = entity.cw_adapt_to("translatable_entity").translation_infos()
        for lang, infos in _infos:
            url = entity.absolute_url(vid="translate_entity", lang_code=lang.code)
            if infos is None:
                action = self._cw._("creation")
            else:
                # add translation state in action text (outdated, incomplete)
                action = []
                if len([1 for t, _f in infos if t.is_outdated()]):
                    action.append(self._cw._("outdated"))
                if len(infos) < len(entity.i18nfields):
                    action.append(self._cw._("incomplete"))
                action = ", ".join(action) or self._cw._("edition")
            title = f"{self._cw._(lang.name)} ({action})"
            yield self.build_action(title, url)
        yield self.build_action(
            self._cw._("manage translations"), self._cw.build_url("i18n")
        )

    def fill_menu(self, box, menu):
        menu.append_anyway = True
        super().fill_menu(box, menu)


class ManageTranslationsView(StartupView):
    __regid__ = "i18nfield.manage_translations"
    http_cache_manager = NoHTTPCacheManager

    def select_rql(self):
        return (
            "Any X,GROUP_CONCAT(C) GROUPBY X ORDERBY MD DESC "
            "WHERE X modification_date MD, NOT X ref_lang L, L name C, "
        )

    def incomplete_rql(self):
        return (
            self.select_rql()
            + "EXISTS(F i18nfield_of X, NOT EXISTS(T of_field F, T lang L))"
        )

    def outdated_rql(self):
        return (
            self.select_rql()
            + "EXISTS(F i18nfield_of X, F last_edited FD, T of_field F,"
            " T modification_date < FD, T lang L)"
        )

    def lang_html(self, entity, lang_eids):
        html = []
        for eid in lang_eids.split(","):
            infos = LANGS_BY_EID[int(eid)]
            href = entity.absolute_url(vid="translate_entity", lang_code=infos["code"])
            html.append(
                f"{xml_escape(infos['name'])} ({tags.a(self._cw._('edit'), href=href)})"
            )
        return ", ".join(html)

    def call(self, *args, **kwargs):
        sections = (
            ("incomplete translations", self.incomplete_rql),
            ("outdated translations", self.outdated_rql),
        )
        for title, rql_method in sections:
            rset = self._cw.execute(rql_method())
            if rset.rowcount:
                self.w(
                    f'<div class="section translations"><h2>{self._cw._(title)}</h2>'
                )
                self.wview("table.translations", rset)
                self.w("</div>")


class ManageTranslationTableView(cw_tableview.RsetTableView):
    __regid__ = "table.translations"
    layout_id = "table.table-layout"
    headers = (_("entities"), _("languages"))
    layout_args = {"display_filter": "top", "hide_filter": False}


class TableLayout(cw_tableview.TableLayout):
    __regid__ = "table.table-layout"
    cssclass = "table table-default listing"
    page_size = 20

    def render_table(self, w, actions, paginate):
        view = self.view
        divid = view.domid
        if divid is not None:
            w(f'<div id="{divid}">')
        else:
            assert not (actions or paginate)
        nav_html = UStringIO()
        if paginate:
            #  customization :  add page_size=self.page_size
            view.paginate(
                w=nav_html.write,
                page_size=self.page_size,
                show_all_option=self.show_all_option,
            )
        w(nav_html.getvalue())
        if actions and self.display_actions == "top":
            self.render_actions(w, actions)
        colrenderers = view.build_column_renderers()
        attrs = self.table_attributes()
        w(f"<table {sgml_attributes(attrs)}>")
        if self.view.has_headers:
            self.render_table_headers(w, colrenderers)
        self.render_table_body(w, colrenderers)
        w("</table>")
        if actions and self.display_actions == "bottom":
            self.render_actions(w, actions)
        if divid is not None:
            w("</div>")


class TranslateEntityView(EditionFormView):
    __regid__ = "translate_entity"
    __select__ = (
        EditionFormView.__select__
        & adaptable("translatable_entity")
        & match_form_params("lang_code")
    )
    form_id = "translate_entity"

    @property
    def title(self):
        lang = lang_from_code(self._cw)
        return self._cw._("%s translation") % self._cw._(lang.name)


class TranslateEntityForm(AutoForm):
    __regid__ = "translate_entity"
    __select__ = AutoForm.__select__ & adaptable("translatable_entity")

    def editable_attributes(self):
        return []

    def inlined_relations(self):
        rschema = self._cw.vreg.schema["i18nfield_of"]
        ttype = self._cw.vreg.schema["I18nField"]
        return [(rschema, (ttype,), "object")]

    def inline_edition_form_view(self, rschema, ttype, role):
        """overloaded method to force uneditable I18nField instance forms to
        be displayed, so that underlying Translation entities can be created
        or edited.
        """
        assert str(rschema) == "i18nfield_of"
        entity = self.edited_entity
        rset = entity.has_eid() and entity.related(rschema, role)
        if rset:
            fields = entity.i18nfields
            related = sorted(rset.entities(), key=lambda f: fields.index(f.field_name))
            vvreg = self._cw.vreg["views"]
            for relentity in related:
                yield vvreg.select(
                    "inline-edition",
                    self._cw,
                    rset=relentity.as_rset(),
                    row=0,
                    col=0,
                    etype=ttype,
                    rtype=rschema,
                    role=role,
                    peid=entity.eid,
                    pform=self,
                )


class I18nFieldInlineEditionView(InlineEntityEditionFormView):
    __select__ = (
        InlineEntityEditionFormView.__select__
        & is_instance("I18nField")
        & match_form_params("lang_code")
    )

    def form_title(self, entity, i18nctx):
        return entity.field_name

    def _get_removejs(self):
        return None


class I18nFieldEditionForm(AutoForm):
    __select__ = (
        AutoForm.__select__ & is_instance("I18nField") & match_form_params("lang_code")
    )

    def inlined_relations(self):
        rschema = self._cw.vreg.schema["of_field"]
        ttype = self._cw.vreg.schema["Translation"]
        return [(rschema, (ttype,), "object")]

    def inline_edition_form_view(self, rschema, ttype, role):
        assert str(rschema) == "of_field"
        translation = self.edited_entity.translation(self._cw.form["lang_code"])
        vvreg = self._cw.vreg["views"]
        if translation:
            yield vvreg.select(
                "inline-edition",
                self._cw,
                rset=translation.as_rset(),
                row=0,
                col=0,
                etype=ttype,
                rtype=rschema,
                role=role,
                peid=self.edited_entity.eid,
                pform=self,
            )
        else:
            yield vvreg.select(
                "inline-creation",
                self._cw,
                etype=ttype,
                rtype=rschema,
                role=role,
                petype=self.edited_entity.e_schema,
                peid=self.edited_entity.eid,
                pform=self,
            )

    def should_display_inline_creation_form(self, rschema, existant, card):
        return not existant

    def should_display_add_new_relation_link(self, rschema, existant, card):
        return False


class I18nTranslationInlineViewMixin:
    def form_title(self, entity, i18nctx):
        title = super().form_title(entity, i18nctx)
        if entity.has_eid() and entity.is_outdated():
            title += f" ({self._cw._('outdated')})"
        return title


class I18nTranslationInlinedFormRenderer(EntityInlinedFormRenderer):
    __select__ = EntityInlinedFormRenderer.__select__ & is_instance("Translation")

    def render_title(self, w, form, values):
        return


class I18nFieldInlinedFormRenderer(EntityInlinedFormRenderer):
    __select__ = EntityInlinedFormRenderer.__select__ & is_instance("I18nField")
    title_template = """\
    <div class="{css_value}">{orig_val}</div>
    <div class="{css_lang}">{label} : {orig_lang}</div>
    """

    def render_title(self, w, form, values):
        ent = form.edited_entity
        template_parameters = {
            "orig_val": xml_escape(ent.original_value() or ""),
            "orig_lang": self._cw._(ent.i18nfield_of[0].ref_lang[0].name),
            "label": self._cw._("Original version"),
            "css_lang": "cw_i18nfield_orig_lang",
            "css_value": "cw_i18nfield_orig_value",
        }
        w(self.title_template.format(**template_parameters))


class I18nTranslationInlineEditionView(
    I18nTranslationInlineViewMixin, InlineEntityEditionFormView
):
    __select__ = InlineEntityEditionFormView.__select__ & is_instance("Translation")


class I18nTranslationInlineCreationView(
    I18nTranslationInlineViewMixin, InlineEntityCreationFormView
):
    __select__ = InlineEntityCreationFormView.__select__ & specified_etype_implements(
        "Translation"
    )


class TranslationEditionForm(AutoForm):
    __select__ = (
        AutoForm.__select__ & is_instance("Translation") & match_kwargs("pform")
    )

    @iclassmethod
    def field_by_name(cls_or_self, name, role=None, eschema=None):
        """make the field used for translation value the same than the one
        used for the field in the translated entity itself"""
        if (name, role) == ("value", "subject"):
            try:
                return super().field_by_name(name, role)
            except FieldNotFound:
                if eschema is None:
                    raise
            i18nfield = cls_or_self.parent_form.edited_entity
            orig_eschema = i18nfield.i18nfield_of[0].e_schema
            rschema = orig_eschema.schema.relation_schema_for(i18nfield.field_name)
            tschemas = rschema.targets(orig_eschema, role)
            fieldcls = _AFF.etype_get(orig_eschema, rschema, role, tschemas[0])
            kwargs = _AFF_KWARGS.etype_get(orig_eschema, rschema, role, tschemas[0])
            if kwargs is None:
                kwargs = {}
            if fieldcls:
                if not isinstance(fieldcls, type):
                    return fieldcls  # already and instance
                return fieldcls(name=name, role=role, eidparam=True, **kwargs)
            field = guess_field(orig_eschema, rschema, role, eidparam=True, **kwargs)
            if field is None:
                raise
            field.name = name
            if getattr(field, "get_format_field", None):
                field.get_format_field = lambda form: None
            return field
        else:
            return super().field_by_name(name, role, eschema)


def translation_form_lang(form, field):
    lang = lang_from_code(form._cw)
    return lang is not None and lang.eid or None


_AFS.tag_object_of(("Translation", "of_field", "I18nField"), "main", "inlined")

_AFFK.tag_subject_of(
    ("Translation", "lang", "I18nLang"),
    {"widget": HiddenInput, "value": translation_form_lang},
)


class i18nfieldReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx("/i18n"), dict(vid="i18nfield.manage_translations")),
    ]
