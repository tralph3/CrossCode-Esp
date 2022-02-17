// <https://github.com/CCDirectLink/crosscode-ru/blob/66fcae728384072e7657c214988257071657d86a/src/version-display.ts>

const VERSION_TEXT_STR = `Esp v${modloader.loadedMods.get('CrossCode-Esp').version}`;

function attachVersionTextGui(self) {
  if (self.modVersionGuis == null) {
    self.modVersionGuis = [self.ccloaderVersionGui];
  }
  let prevGui = self.modVersionGuis.last();
  let newGui = new sc.TextGui(VERSION_TEXT_STR, { font: sc.fontsystem.tinyFont });
  newGui.setAlign(prevGui.hook.align.x, prevGui.hook.align.y);
  newGui.setPos(prevGui.hook.pos.x, prevGui.hook.pos.y + prevGui.hook.size.y);
  self.versionGui.addChildGui(newGui);
  self.modVersionGuis.push(newGui);
}

sc.TitleScreenGui.inject({
  init(...args) {
    this.parent(...args);
    attachVersionTextGui(this);
  },
});

sc.PauseScreenGui.inject({
  init(...args) {
    this.parent(...args);
    attachVersionTextGui(this);
  },
});
