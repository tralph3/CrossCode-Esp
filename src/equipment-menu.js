sc.esp.addLocaleSpecificPatch(() => {
  sc.EquipLevelOverview.inject({
    init(...args) {
      this.parent(...args);
      const ADDITIONAL_WIDTH = 4;
      this.hook.size.x += ADDITIONAL_WIDTH;
      this.annotation.size.x += ADDITIONAL_WIDTH;
      let lineHook = this.hook.children.find((hook) => hook.gui instanceof ig.ColorGui);
      lineHook.size.x += ADDITIONAL_WIDTH;
    },
  });
});
