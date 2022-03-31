// Based on <https://github.com/CCDirectLink/crosscode-ru/blob/ab765a9a658a5e08bd9c522542980f9fde125ce7/src/locale.ts>

sc.esp.ORIGINAL_LOCALE = 'en_US';
sc.esp.TRANSLATION_LOCALE = 'es_ES';
sc.esp.LANGUAGE_NAME = {
  en_US: 'Spanish',
  es_ES: 'Español',
};
sc.esp.LOCALIZE_ME_PACKS_DIR = 'mod://CrossCode-Esp/packs/';
sc.esp.LOCALIZE_ME_MAPPING_FILE = 'mod://CrossCode-Esp/packs-mapping.json';
sc.esp.PATCHED_FONT_CHARACTERS = '¡¿ÁÉÍÑÓÚáéíñóú';
sc.esp.PATCHED_FONT_URLS = [
  `media/font/${sc.esp.TRANSLATION_LOCALE}/hall-fetica-bold.png`,
  `media/font/${sc.esp.TRANSLATION_LOCALE}/hall-fetica-small.png`,
  `media/font/${sc.esp.TRANSLATION_LOCALE}/tiny.png`,
];
sc.esp.DEBUG_MISSING_TRANSLATIONS = false;

sc.esp.IGNORED_LABELS = new Set([
  '',
  'en_US',
  'LOL, DO NOT TRANSLATE THIS!',
  'LOL, DO NOT TRANSLATE THIS! (hologram)',
  '\\c[1][DO NOT TRANSLATE THE FOLLOWING]\\c[0]',
  '\\c[1][DO NOT TRANSLATE FOLLOWING TEXTS]\\c[0]',
]);

localizeMe.add_locale(sc.esp.TRANSLATION_LOCALE, {
  from_locale: sc.esp.ORIGINAL_LOCALE,
  map_file: sc.esp.LOCALIZE_ME_MAPPING_FILE,
  url_prefix: sc.esp.LOCALIZE_ME_PACKS_DIR,
  language: sc.esp.LANGUAGE_NAME,
  flag: `media/font/${sc.esp.TRANSLATION_LOCALE}/flag.png`,

  missing_cb: (langLabelOrString, dictPath) => {
    let original;
    let translated;
    if (typeof langLabelOrString === 'string') {
      original = langLabelOrString;
      translated = null;
    } else {
      original = langLabelOrString[sc.esp.ORIGINAL_LOCALE];
      translated = langLabelOrString[sc.esp.TRANSLATION_LOCALE];
    }

    if (translated != null && translated.length > 0) return translated;
    if (original === sc.esp.ORIGINAL_LOCALE) return sc.esp.TRANSLATION_LOCALE;

    if (!sc.esp.DEBUG_MISSING_TRANSLATIONS) return original;

    if (sc.esp.IGNORED_LABELS.has(original.trim())) {
      return original;
    }

    if (/^credits\/[^/]+\.json\/entries\/[^/]+\/names\/[^/]+$/.test(dictPath)) {
      return original;
    }

    return `--${original}`;
  },

  pre_patch_font: async (context) => {
    if (context.patchedFonts == null) context.patchedFonts = {};
    let url = sc.esp.PATCHED_FONT_URLS[context.size_index];
    if (url != null) {
      context.patchedFonts[sc.esp.TRANSLATION_LOCALE] = await sc.ui2.waitForLoadable(
        new ig.Font(url, context.char_height),
      );
    }
  },

  patch_base_font: (canvas, context) => {
    let patchedFont = context.patchedFonts[sc.esp.TRANSLATION_LOCALE];
    if (patchedFont != null) {
      let ctx2d = canvas.getContext('2d');
      for (let i = 0; i < sc.esp.PATCHED_FONT_CHARACTERS.length; i++) {
        let char = sc.esp.PATCHED_FONT_CHARACTERS[i];
        let width = patchedFont.widthMap[i] + 1;
        let rect = context.reserve_char(canvas, width);
        context.set_char_pos(char, rect);
        let srcX = patchedFont.indicesX[i];
        let srcY = patchedFont.indicesY[i];
        ctx2d.drawImage(
          patchedFont.data,
          srcX,
          srcY,
          width,
          patchedFont.charHeight,
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
