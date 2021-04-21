// Based on <https://github.com/CCDirectLink/crosscode-ru/blob/ab765a9a658a5e08bd9c522542980f9fde125ce7/src/locale.ts>

const ORIGINAL_LOCALE = 'en_US';
const TRANSLATION_LOCALE = 'es_ES';
const LANGUAGE_NAME = {
  en_US: 'Spanish',
  es_ES: 'Español',
};
const LOCALIZE_ME_PACKS_DIR = 'mod://CrossCode-Esp/packs/';
const LOCALIZE_ME_MAPPING_FILE = 'mod://CrossCode-Esp/packs-mapping.json';
const PATCHED_FONT_CHARACTERS = '¡¿ÁÉÍÑÓÚáéíñóú';
const PATCHED_FONT_URLS = [
  `media/font/${TRANSLATION_LOCALE}/hall-fetica-bold.png`,
  `media/font/${TRANSLATION_LOCALE}/hall-fetica-small.png`,
  `media/font/${TRANSLATION_LOCALE}/tiny.png`,
];
const DEBUG_MISSING_TRANSLATIONS = false;

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
  language: LANGUAGE_NAME,
  flag: `media/font/${TRANSLATION_LOCALE}/flag.png`,

  missing_cb: (langLabelOrString, dictPath) => {
    let original;
    let translated;
    if (typeof langLabelOrString === 'string') {
      original = langLabelOrString;
      translated = null;
    } else {
      original = langLabelOrString[ORIGINAL_LOCALE];
      translated = langLabelOrString[TRANSLATION_LOCALE];
    }

    if (translated != null && translated.length > 0) return translated;
    if (original === ORIGINAL_LOCALE) return TRANSLATION_LOCALE;

    if (!DEBUG_MISSING_TRANSLATIONS) return original;

    if (IGNORED_LABELS.has(original.trim())) {
      return original;
    }

    if (/^credits\/[^/]+\.json\/entries\/[^/]+\/names\/[^/]+$/.test(dictPath)) {
      return original;
    }

    return `--${original}`;
  },

  pre_patch_font: async (context) => {
    let url = PATCHED_FONT_URLS[context.size_index];
    if (url != null) {
      context.spanishFont = await sc.ui2.waitForLoadable(new ig.Font(url, context.char_height));
    }
  },

  patch_base_font: (canvas, context) => {
    let { spanishFont } = context;
    if (spanishFont != null) {
      let ctx2d = canvas.getContext('2d');
      for (let i = 0; i < PATCHED_FONT_CHARACTERS.length; i++) {
        let char = PATCHED_FONT_CHARACTERS[i];
        let width = spanishFont.widthMap[i] + 1;
        let rect = context.reserve_char(canvas, width);
        context.set_char_pos(char, rect);
        let srcX = spanishFont.indicesX[i];
        let srcY = spanishFont.indicesY[i];
        ctx2d.drawImage(
          spanishFont.data,
          srcX,
          srcY,
          width,
          spanishFont.charHeight,
          rect.x,
          rect.y,
          rect.width,
          rect.height,
        );
      }
    }
    return canvas;
  },
});
