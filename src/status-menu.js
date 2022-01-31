sc.esp.addLocaleSpecificPatch(() => {
  sc.StatusMenu.inject({
    init(...args) {
      this.parent(...args);
      const ADDITIONAL_WIDTH = 10;
      this.pager.hook.size.x += ADDITIONAL_WIDTH;
    },
  });
});
