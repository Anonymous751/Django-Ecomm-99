import polib
from deep_translator import GoogleTranslator

languages = ['fr', 'hi', 'pa']

for lang in languages:
    po_path = f'locale/{lang}/LC_MESSAGES/django.po'
    po = polib.pofile(po_path)
    print(f"\n🔤 Translating {lang.upper()} file...")

    for entry in po.untranslated_entries():
        try:
            translation = GoogleTranslator(source='en', target=lang).translate(entry.msgid)
            entry.msgstr = translation
            print(f"✅ {entry.msgid} → {entry.msgstr}")
        except Exception as e:
            print(f"⚠️ Error on {entry.msgid}: {e}")

    po.save(po_path)
    print(f"💾 Saved translations to {po_path}")