import collections
from iso639 import languages
def get_language_code(language):
    to_try = [languages.name, languages.inverted, languages.part1]
    l_to_try = [language.capitalize(), language.lower()]
    for l in l_to_try:
        for t in to_try:
            if l in t:
                if not t[l].part1:
                    continue
                return t[l].part1
    raise Exception('Language %s not recognized. Try the iso-639 code.' % language)

def multilingual_params(language, **kwargs):
    language_code = get_language_code(language)
    lang_model = collections.defaultdict(lambda: 'xlm-roberta-large')
    lang_model['fr'] = 'flaubert/flaubert_base_cased'
    lang_model['en'] = 'roberta-base'
    lang_model['de'] = 'bert-base-german-cased'
    prefixes = {
        'af': 'Hierdie teks is in Afrikaans geskryf. ',
        'sq': 'Ky tekst është shkruar në shqip. ',
        'am': 'ይህ ጽሑፍ በአማርኛ ተጽ writtenል ፡፡ ',
        'ar': 'هذا النص مكتوب بالعربية. ',
        'hy': 'Այս տեքստը գրված է հայերեն: ',
        'az': 'Bu mətn Azərbaycan dilində yazılmışdır. ',
        'eu': 'Testu hau euskaraz idatzita dago. ',
        'be': 'Гэты тэкст напісаны па-беларуску. ',
        'bn': 'এই লেখাটি বাংলা ভাষায় রচিত;। ',
        'bs': 'Ovaj tekst je napisan na bosanskom jeziku. ',
        'br': 'Ce texte est écrit en breton. ',
        'bg': 'Този текст е написан на български език. ',
        'my': 'ဒီစာသားကိုဗမာလိုရေးထားတယ်။ ',
        'ca': 'Aquest text està escrit en català ;. ',
        'zh': '这段文字是用中文写的。',
        'hr': 'Ovaj tekst je napisan na hrvatskom jeziku. ',
        'cs': 'Tento text je psán česky. ',
        'da': 'Denne tekst er skrevet på dansk. ',
        'nl': 'Deze tekst is geschreven in het Nederlands ;. ',
        'eo': 'This text is written in Esperanto. ',
        'et': 'See tekst on kirjutatud eesti keeles. ',
        'fi': 'Tämä teksti on kirjoitettu suomeksi. ',
        'gl': 'Este texto está escrito en galego. ',
        'ka': 'ეს ტექსტი ქართულად არის დაწერილი. ',
        'el': 'Αυτό το κείμενο είναι γραμμένο στα Ελληνικά. ',
        'gu': 'આ લખાણ ગુજરાતીમાં લખાયેલ છે. ',
        'ha': 'An rubuta wannan rubutun cikin harshen Hausa. ',
        'he': 'טקסט זה כתוב בעברית. ',
        'hi': 'यह पाठ हिंदी में लिखा गया है। ',
        'hu': 'Ez a szöveg magyarul készült. ',
        'is': 'Þessi texti er skrifaður á íslensku. ',
        'id': 'Teks ini ditulis dalam bahasa Indonesia. ',
        'ga': 'Tá an téacs seo scríofa i nGaeilge. ',
        'it': 'Questo testo è scritto in italiano. ',
        'ja': 'このテキストは日本語で書かれています。 ',
        'jv': 'Naskah iki ditulis nganggo basa jawa. ',
        'kn': 'ಈ ಪಠ್ಯವನ್ನು ಕನ್ನಡದಲ್ಲಿ ಬರೆಯಲಾಗಿದೆ. ',
        'kk': 'Бұл мәтін қазақ тілінде жазылған. ',
        'km': 'អត្ថបទនេះត្រូវបានសរសេរនៅកណ្តាល។ ',
        'ko': '이 텍스트는 한국어로 작성되었습니다. ',
        'ku': 'Bu metin Kürtçe yazılmıştır. ',
        'ky': 'Бул текст кыргыз тилинде жазылган;. ',
        'lo': 'ບົດຂຽນນີ້ຂຽນເປັນພາສາລາວ. ',
        'la': 'Questo testo è scritto in latino. ',
        'lv': 'Šis teksts ir uzrakstīts latviešu valodā. ',
        'lt': 'Šis tekstas parašytas lietuvių kalba. ',
        'mk': 'Овој текст е напишан на македонски јазик. ',
        'mg': 'Ity soratra ity dia voasoratra amin\'ny teny malagasy. ',
        'ms': 'Teks ini ditulis dalam bahasa Melayu. ',
        'ml': 'ഈ വാചകം മലയാളത്തിലാണ് എഴുതിയിരിക്കുന്നത്. ',
        'mr': 'हा मजकूर मराठीत लिहिला आहे;. ',
        'mn': 'Энэ текстийг монгол хэлээр бичсэн болно. ',
        'ne': 'यो लेख नेपालीमा लेखिएको छ। ',
        'no': 'Denne teksten er skrevet på norsk. ',
        'ps': 'دا متن په پښتو ژبه لیکل شوی.. ',
        'fa': 'این متن به زبان فارسی نوشته شده است ؛. ',
        'pl': 'Ten tekst jest napisany w języku polskim. ',
        'pt': 'Este texto está escrito em português. ',
        'pa': 'ਇਹ ਪਾਠ ਪੰਜਾਬ ਵਿਚ ਲਿਖਿਆ ਗਿਆ ਹੈ;. ',
        'ro': 'Acest text este scris în limba română ;. ',
        'ru': 'Этот текст написан на русском языке. ',
        'gd': 'Tha an teacsa seo sgrìobhte ann an Gàidhlig ;. ',
        'sr': 'Овај текст је написан на српском. ',
        'sd': 'اهو متن سنڌي ۾ لکيو وڃي ٿو. ',
        'si': 'මෙම පා text ය සිංහල භාෂාවෙන් ලියා ඇත. ',
        'sk': 'Tento text je v slovenskom jazyku. ',
        'sl': 'To besedilo je napisano v slovenščini;. ',
        'so': 'Qoraalkan wuxuu ku qoran yahay Afsoomaali. ',
        'es': 'Este texto está escrito en español. ',
        'su': 'Téks ieu ditulis dina basa Sunda. ',
        'sw': 'Maandishi haya yameandikwa kwa kiswahili. ',
        'sv': 'Denna text är skriven på svenska. ',
        'ta': 'இந்த உரை தமிழில் எழுதப்பட்டுள்ளது. ',
        'te': 'ఈ వచనం తెలుగులో వ్రాయబడింది. ',
        'th': 'ข้อความนี้เขียนเป็นภาษาไทย ',
        'tr': 'Bu metin Türkçe yazılmıştır. ',
        'uk': 'Цей текст написаний українською мовою. ',
        'ur': 'یہ عبارت اردو میں لکھی گئی ہے۔ ',
        'ug': 'This text is written in Uighur;. ',
        'uz': 'Ushbu matn o\'zbek tilida yozilgan. ',
        'vi': 'Văn bản này được viết bằng tiếng Việt. ',
        'cy': 'Mae\'r testun hwn wedi\'i ysgrifennu yn Gymraeg. ',
        'xh': 'Lo mbhalo ubhalwe ngesiXhosa. ',
        'yi': 'דער טעקסט איז געשריבן אויף ייִדיש. ',
    }
    params = {
        'model_name': lang_model[language_code],
        'prefix_sentence': prefixes.get(language_code, ''),
        'allow_word_pieces': True if language_code in ['zh', 'ja', 'ko'] else False
    }
    if language_code not in prefixes and language_code not in ['fr', 'en', 'de']:
        raise Exception('Language %s not supported yet. Sorry!' % language)
    params.update(**kwargs)
    return params
