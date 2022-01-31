sc.esp.addLocaleSpecificPatch(() => {
  sc.ShopMenu.inject({
    init(...args) {
      this.parent(...args);
      const ADDITIONAL_WIDTH = 20;
      this.pageView.hook.size.x += ADDITIONAL_WIDTH;
      this.pageView.hook.pos.x -= ADDITIONAL_WIDTH / 2;
    },
  });
});
