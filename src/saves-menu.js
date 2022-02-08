sc.esp.addLocaleSpecificPatch(() => {
  sc.SaveSlotChapter.inject({
    init(...args) {
      this.parent(...args);
      this.chapterGui.hook.pos.x = this.textGui.hook.pos.x + this.textGui.hook.size.x + 4;
    },
  });
});
