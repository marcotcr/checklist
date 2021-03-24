import re

def replace_race(editor, text, meta=False):
    # document: only replace if there is a single instance
    races = ['white', 'Asian', 'black', 'Hispanic']
    found = re.findall(r'\b(%s)\b' % '|'.join(races), text,  flags=re.I)
    if len(found) != 1:
        return None
    found = found[0].lower()
    b = re.sub(r'\b(%s)\b' % '|'.join(races), '{race}', text,  flags=re.I)
    b = re.sub(r'\ban? {race}', '{a:race}', b)
    nraces = [x for x in races if x.lower() != found.lower()]
    t = [x for x in editor.template(b, race=nraces).data if x != text]
    if not t:
        return None
    if found.lower() not in ['asian', 'hispanic']:
        if not editor.suggest_replace(text, found, candidates=['Hispanic', 'Asian'], threshold=6):
            return None
    return t
