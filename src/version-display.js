// <https://github.com/CCDirectLink/crosscode-ru/blob/af5403b4fd0be67225a6fe0c3e3bb0b62dfa7c1e/src/version-display.ts>

function attachVersionText(prevVersionGui) {
  let version = modloader.loadedMods.get('CrossCode-Esp').version;
  let newVersionGui = new sc.TextGui(`Esp v${version}`, {
    font: sc.fontsystem.tinyFont,
  });
  newVersionGui.setAlign(prevVersionGui.hook.align.x, prevVersionGui.hook.align.y);
  newVersionGui.setPos(0, prevVersionGui.hook.size.y);
  prevVersionGui.addChildGui(newVersionGui);
  return newVersionGui;
}

sc.TitleScreenGui.inject({
  crosscodeEspVersionGui: null,
  init(...args) {
    this.parent(...args);
    this.crosscodeEspVersionGui = attachVersionText(this.ccloaderVersionGui);
  },
});

sc.PauseScreenGui.inject({
  crosscodeEspVersionGui: null,
  init(...args) {
    this.parent(...args);
    this.crosscodeEspVersionGui = attachVersionText(this.ccloaderVersionGui);
  },
});
