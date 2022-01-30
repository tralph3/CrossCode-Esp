sc.esp.addLocaleSpecificPatch(() => {
  sc.QuestHubListEntry.inject({
    init(...args) {
      this.parent(...args);
      this.area.tickerHook.maxWidth =
        this.areaContent.hook.size.x - this.area.hook.pos.x - this.level.hook.pos.x;
    },
  });
});
