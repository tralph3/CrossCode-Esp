// <https://github.com/CCDirectLink/crosscode-ru/blob/5cab767ad7bc6ba75efd541ba6839f6801f04dce/src/level-up.ts>
sc.esp.addLocaleSpecificPatch(() => {
  sc.LevelUpContentGui.inject({
    patchedGfx: new ig.Image('media/gui/status-gui.es_ES.png'),

    updateDrawables(renderer) {
      renderer.addGfx(this.patchedGfx, 9, 0, 0, 0, 97, 20);
      renderer.addTransform().setTranslate(-7, 0);
      let oldAddGfx = renderer.addGfx;
      try {
        // skip the first call to addGfx
        renderer.addGfx = (_gfx, _posX, _posY, _srcX, _srcY, _sizeX, _sizeY) => {
          renderer.addGfx = oldAddGfx;
        };
        this.parent(renderer);
      } finally {
        renderer.addGfx = oldAddGfx;
      }
      renderer.undoTransform();
    },
  });
});
