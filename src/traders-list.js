// <https://github.com/CCDirectLink/crosscode-ru/blob/5cab767ad7bc6ba75efd541ba6839f6801f04dce/src/traders-list.ts>

sc.esp.addLocaleSpecificPatch(() => {
  function patchTraderLocation(location) {
    location.textBlock.linePadding = -3;
  }

  function setTraderLocationText(location, traderId) {
    let foundTrader = sc.trade.getFoundTrader(traderId);
    location.setText(`${foundTrader.area || '???'}\n> ${foundTrader.map || '???'}`);
  }

  sc.TradeButtonBox.inject({
    init(trader, ...args) {
      this.parent(trader, ...args);
      patchTraderLocation(this.location);
      setTraderLocationText(this.location, trader);
    },
  });

  sc.TradeDetailsView.inject({
    init(...args) {
      this.parent(...args);
      patchTraderLocation(this.location);
    },

    setTraderData(trader, ...args) {
      let shouldUpdateLocation = this._trader !== trader;
      this.parent(trader, ...args);
      if (shouldUpdateLocation) setTraderLocationText(this.location, trader);
    },
  });
});
