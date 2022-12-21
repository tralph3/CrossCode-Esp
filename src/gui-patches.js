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
      renderer.addTransform().setTranslate(-7, 0);
      let { addGfx } = renderer;
      try {
        renderer.addGfx = (gfx, posX, posY, srcX, srcY, sizeX, sizeY, flipX, flipY) => {
          if (gfx === this.gfx && srcX === 0 && srcY === 192 && sizeX === 112 && sizeY === 20) {
            return addGfx.call(renderer, this.patchedGfx, 16, 0, 0, 0, 97, 20);
          }
          return addGfx.call(renderer, gfx, posX, posY, srcX, srcY, sizeX, sizeY, flipX, flipY);
        };
        this.parent(renderer);
      } finally {
        renderer.addGfx = addGfx;
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

  sc.QuestDetailsView.inject({
    init(...args) {
      this.parent(...args);
      this.locationArea.tickerHook.maxWidth =
        this.lines[0].hook.pos.x + this.lines[0].hook.size.x - this.locationArea.hook.pos.x;
      this.locationMap.tickerHook.maxWidth =
        this.lines[0].hook.pos.x + this.lines[0].hook.size.x - this.locationMap.hook.pos.x;
    },
  });

  sc.CircuitInfoBox.inject({
    init(...args) {
      this.parent(...args);
      this.special.setPos(this.header.hook.pos.x, this.header.hook.pos.y);
      this.special.setAlign(ig.GUI_ALIGN.X_LEFT, ig.GUI_ALIGN.Y_BOTTOM);
    },
  });
});
