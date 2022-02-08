import './version-display.js';
import './traders-list.js';
import './level-up.js';
import './tab-buttons.js';
import './quest-dialog.js';
import './quest-hub.js';
import './equipment-menu.js';
import './shop-menu.js';
import './status-menu.js';
import './saves-menu.js';

sc.esp.addLocaleSpecificPatch(() => {
  sc.QuickBorderArrowLevelBox.prototype.renderLevelLabelAsTextBlock = true;
  sc.SocialEntryButton.prototype.renderStatusAsTextBlock = true;
});
