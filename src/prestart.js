import './version-display.js';
import './traders-list.js';
import './level-up.js';
import './tab-buttons.js';
import './quest-hub.js';
import './equipment-menu.js';
import './shop-menu.js';
import './status-menu.js';
import './saves-menu.js';
import './hud.js';

sc.esp.addLocaleSpecificPatch(() => {
  sc.QuickBorderArrowLevelBox.prototype.UI2_DRAW_LEVEL_LABEL_AS_TEXT_BLOCK = true;
  sc.SocialEntryButton.prototype.UI2_DRAW_STATUS_AS_TEXT_BLOCK = true;
});
