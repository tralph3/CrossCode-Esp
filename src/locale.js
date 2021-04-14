// Based on <https://github.com/CCDirectLink/crosscode-ru/blob/ab765a9a658a5e08bd9c522542980f9fde125ce7/src/locale.ts>

const ORIGINAL_LOCALE = 'en_US';
const TRANSLATION_LOCALE = 'es_ES';

const LOCALIZE_ME_PACKS_DIR = 'mod://CrossCode-Esp/packs/';
const LOCALIZE_ME_MAPPING_FILE = 'mod://CrossCode-Esp/packs-mapping.json';

const IGNORED_LABELS = new Set([
  '',
  'en_US',
  'LOL, DO NOT TRANSLATE THIS!',
  'LOL, DO NOT TRANSLATE THIS! (hologram)',
  '\\c[1][DO NOT TRANSLATE THE FOLLOWING]\\c[0]',
  '\\c[1][DO NOT TRANSLATE FOLLOWING TEXTS]\\c[0]',
]);

localizeMe.add_locale(TRANSLATION_LOCALE, {
  from_locale: ORIGINAL_LOCALE,
  map_file: LOCALIZE_ME_MAPPING_FILE,
  url_prefix: LOCALIZE_ME_PACKS_DIR,
  language: {
    en_US: 'Spanish',
    es_ES: 'Español',
  },
  flag: `media/font/${TRANSLATION_LOCALE}/flag.png`,

  missing_cb: (langLabelOrString, dictPath) => {
    if (typeof langLabelOrString === 'string') {
      langLabelOrString = { [ORIGINAL_LOCALE]: langLabelOrString };
    }
    let original = langLabelOrString[ORIGINAL_LOCALE];
    let translated = langLabelOrString[TRANSLATION_LOCALE];

    if (translated) return translated;
    if (original === ORIGINAL_LOCALE) return TRANSLATION_LOCALE;

    if (IGNORED_LABELS.has(original.trim())) {
      return original;
    }

    if (/^credits\/[^/]+\.json\/entries\/[^/]+\/names\/[^/]+$/.test(dictPath)) {
      return original;
    }

    // return `--${original}`; // debug mode
    return original;
  },
});
