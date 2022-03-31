import './version-display.js';
import './level-up.js';
import './quest-hub.js';
import './equipment-menu.js';
import './shop-menu.js';
import './status-menu.js';
import './saves-menu.js';
import './hud.js';

sc.esp.addLocaleSpecificPatch(() => {
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
});
