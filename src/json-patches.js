ccmod.resources.jsonPatches.add('data/props/cold-dng.json', (data) => {
  if (ig.currentLang !== sc.esp.TRANSLATION_LOCALE) return;
  if (data.DOCTYPE !== 'PROP_SHEET') return;
  for (let prop of data.props) {
    if (prop.name === 'elevatorSign') {
      let sheet = prop.anims.namedSheets.sign;
      if (sheet != null) {
        Object.assign(sheet, {
          src: 'media/map/cold-dng.es_ES.png',
          offX: 0,
          offY: 0,
        });
      }
    }
  }
});
