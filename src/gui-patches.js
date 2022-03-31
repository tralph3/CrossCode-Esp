localizeMe.register_locale_chosen(() => {
  if (ig.currentLang !== sc.esp.TRANSLATION_LOCALE) return;

  sc.QuickBorderArrowLevelBox.prototype.UI2_DRAW_LEVEL_LABEL_AS_TEXT_BLOCK = true;
  sc.SocialEntryButton.prototype.UI2_DRAW_STATUS_AS_TEXT_BLOCK = true;

  function tabBtnsCfg(clazz, opts = {}) {
    clazz.prototype.UI2_TAB_BTN_AUTO_WIDTH = true;
    let { min = 0, padding = 16 } = opts;
    clazz.prototype.UI2_TAB_BTN_AUTO_WIDTH_MIN = min;
    clazz.prototype.UI2_TAB_BTN_AUTO_WIDTH_PADDING = padding;
  }

  // tabBtnsCfg(sc.ItemTabbedBox);
  tabBtnsCfg(sc.OptionsTabBox);
  tabBtnsCfg(sc.QuestListBox);
  tabBtnsCfg(sc.QuestHubList);
  tabBtnsCfg(sc.EnemyListBox);
  tabBtnsCfg(sc.LoreListBoxNew, { padding: 22 });
  tabBtnsCfg(sc.StatsListBox);
  tabBtnsCfg(sc.TrophyList);
  tabBtnsCfg(sc.SocialList);
  tabBtnsCfg(sc.TradersListBox);
  tabBtnsCfg(sc.BotanicsListBox);
  // tabBtnsCfg(sc.ArenaRoundList);
  tabBtnsCfg(sc.ArenaCupList);

  sc.TradeButtonBox.prototype.UI2_SPLIT_LOCATION_INTO_TWO_LINES = true;
  sc.TradersListBox.prototype.UI2_ADDITIONAL_WIDTH = 64;

  // <https://github.com/CCDirectLink/crosscode-ru/blob/5cab767ad7bc6ba75efd541ba6839f6801f04dce/src/level-up.ts>
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

  sc.QuestHubListEntry.inject({
    init(...args) {
      this.parent(...args);
      this.area.tickerHook.maxWidth =
        this.areaContent.hook.size.x - this.area.hook.pos.x - this.level.hook.pos.x;
    },
  });

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

  sc.ShopMenu.inject({
    init(...args) {
      this.parent(...args);
      const ADDITIONAL_WIDTH = 20;
      this.pageView.hook.size.x += ADDITIONAL_WIDTH;
      this.pageView.hook.pos.x -= ADDITIONAL_WIDTH / 2;
    },
  });

  sc.ShopCart.inject({
    init(...args) {
      this.parent(...args);
      this.checkout.setWidth(this.hook.size.x - this.checkout.hook.pos.x * 2 - 1);
    },
  });

  sc.StatusMenu.inject({
    init(...args) {
      this.parent(...args);
      const ADDITIONAL_WIDTH = 10;
      this.pager.hook.size.x += ADDITIONAL_WIDTH;
    },
  });

  sc.SaveSlotChapter.inject({
    init(...args) {
      this.parent(...args);
      this.chapterGui.hook.pos.x = this.textGui.hook.pos.x + this.textGui.hook.size.x + 4;
    },
  });

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
