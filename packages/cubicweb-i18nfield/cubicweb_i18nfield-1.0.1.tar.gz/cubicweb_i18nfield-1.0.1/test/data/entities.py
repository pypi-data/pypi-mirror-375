from logilab.common.registry import yes
from cubicweb.predicates import is_instance

from cubicweb_card.entities import Card as OrigCard
from cubicweb_i18nfield.entities import (
    TranslatableEntityMixin,
    _TranslatableEntityAdapter,
)


class Card(TranslatableEntityMixin, OrigCard):
    __select__ = OrigCard.__select__ & yes()
    i18nfields = ("title",)

    def dc_title(self):
        return self.printable_value("title", format="text/plain")


class MyTranslatableEntityAdapter(_TranslatableEntityAdapter):
    __select__ = _TranslatableEntityAdapter.__select__ & is_instance("Card")
