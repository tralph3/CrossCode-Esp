// <https://github.com/CCDirectLink/crosscode-ru/blob/5cab767ad7bc6ba75efd541ba6839f6801f04dce/src/tab-button.ts>

sc.esp.addLocaleSpecificPatch(() => {
  function createPatch(getConstructor, minLargeWidth, methodName = 'onTabButtonCreation') {
    getConstructor().inject({
      [methodName](...args) {
        let btn = this.parent(...args);
        btn._largeWidth = Math.max(btn._largeWidth, minLargeWidth);
        return btn;
      },
    });
  }

  sc.esp.addLocaleSpecificPatch(() => {
    createPatch(() => sc.ArenaCupList, 135);
    createPatch(() => sc.BotanicsListBox, 160);
    createPatch(() => sc.OptionsTabBox, 105, '_createTabButton');
    createPatch(() => sc.QuestHubList, 105);
    createPatch(() => sc.QuestListBox, 100, '_createTabButton');
    createPatch(() => sc.SocialList, 95);
    createPatch(() => sc.TradersListBox, 200);
  });
});
