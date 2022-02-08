sc.esp.addLocaleSpecificPatch(() => {
  sc.HpHudGui.inject({
    patchedGfx: new ig.Image('media/gui/status-gui.es_ES.png'),
    updateDrawables(renderer) {
      this.parent(renderer);
      renderer.addGfx(this.patchedGfx, 7, 0, 1, 20, 12, 7);
    },
  });

  sc.SpHudGui.inject({
    patchedGfx: new ig.Image('media/gui/status-gui.es_ES.png'),
    updateDrawables(renderer) {
      this.parent(renderer);
      renderer.addGfx(this.patchedGfx, 7, 0, 1, 28, 12, 7);
    },
  });
});
