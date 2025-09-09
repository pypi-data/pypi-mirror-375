Summary
-------

This cube provides a way to manage and display entity field (attribute)
translations, stored in the application database.

To achieve this for your particular entity type, you have to:

* add an 'i18nfield_of' relation definition, linking from the 'I18nField'
  entity type to your translatable entity type(s)

* add a 'ref_lang' relation definition, linking from your entity types
  to the 'I18nLang' entity type

* make your business entity type inherit the 'TranslatableEntityMixin' and
  list its translatable fields in its 'i18nfields' attribute

* create a simple adapter that inherits '_TranslatableEntityAdapter' and is
  selectable for your translatable entity types

That's all for the code part. Just add at least one I18nLang instance in your
database and link your translatable entities to their reference language.

The default web UI will then display a new 'translations' action menu to
users who can modify translatable entities, and display your translatable
entities in the web request language by default.

Example
-------

If you want to translate all fields of the Card entity type (from the 'card'
cube), you will need in your schema.py file::

 from yams.buildobjs import RelationDefinition


 class i18nfield_of(RelationDefinition):
     subject = 'I18nField'
     object = 'Card'
     cardinality = '1*'
     composite = 'object'


 class ref_lang(RelationDefinition):
     subject = 'Card'
     object = 'I18nLang'
     cardinality = '1*'
     inlined = True


And in the entities.py file::

   from cubicweb.predicates import is_instance

   from cubicweb_card.entities import Card as OrigCard
   from cubicweb_i18nfield.entities import (TranslatableEntityMixin,
                                         _TranslatableEntityAdapter)


   class Card(TranslatableEntityMixin, OrigCard):
       i18nfields = (u'title', u'synopsis', u'content')

       def dc_title(self):
           return self.printable_value('title', format='text/plain')


   class MyTranslatableEntityAdapter(_TranslatableEntityAdapter):
       __select__ = _TranslatableEntityAdapter.__select__ & is_instance('Card')

Run tests
---------

In a virtualenv:

```
python2 -m tox
```
