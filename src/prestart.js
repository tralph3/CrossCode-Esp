import './version-display.js';
import './traders-list.js';
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

  sc.ArenaCupList.prototype.UI2_INCREASE_TAB_BUTTON_WIDTH = 135;
  sc.BotanicsListBox.prototype.UI2_INCREASE_TAB_BUTTON_WIDTH = 160;
  sc.OptionsTabBox.prototype.UI2_INCREASE_TAB_BUTTON_WIDTH = 105;
  sc.QuestHubList.prototype.UI2_INCREASE_TAB_BUTTON_WIDTH = 105;
  sc.QuestListBox.prototype.UI2_INCREASE_TAB_BUTTON_WIDTH = 100;
  sc.SocialList.prototype.UI2_INCREASE_TAB_BUTTON_WIDTH = 95;
  sc.TradersListBox.prototype.UI2_INCREASE_TAB_BUTTON_WIDTH = 200;
});
