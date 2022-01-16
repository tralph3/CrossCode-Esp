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

  const TRADERS_LIST_ADDITIONAL_WIDTH = 64;
  sc.TradersListBox.inject({
    init(...args) {
      let setSizeOld = this.setSize;
      let setPivotOld = this.setPivot;
      let setPanelSizeOld = this.setPanelSize;
      try {
        this.setSize = (w, h) => setSizeOld.call(this, w + TRADERS_LIST_ADDITIONAL_WIDTH, h);
        this.setPivot = (x, y) => setPivotOld.call(this, x + TRADERS_LIST_ADDITIONAL_WIDTH, y);
        this.setPanelSize = (w, h) =>
          setPanelSizeOld.call(this, w + TRADERS_LIST_ADDITIONAL_WIDTH, h);

        this.parent(...args);
      } finally {
        this.setSize = setSizeOld;
        this.setPivot = setPivotOld;
        this.setPanelSize = setPanelSizeOld;
      }
    },

    onCreateListEntries(list, ...args) {
      let listSetSizeOld = list.setSize;
      try {
        list.setSize = (w, h) => listSetSizeOld.call(list, w + TRADERS_LIST_ADDITIONAL_WIDTH, h);

        this.parent(list, ...args);
      } finally {
        list.setSize = listSetSizeOld;
      }

      for (let hook of list.contentPane.hook.children) {
        hook.pos.x += TRADERS_LIST_ADDITIONAL_WIDTH;
      }
      for (let hook of list.traderInfoGui.hook.children) {
        hook.size.x += TRADERS_LIST_ADDITIONAL_WIDTH;
      }
    },
  });

  sc.TradeDetailsView.inject({
    init(...args) {
      this.parent(...args);
      this.hook.pos.x -= TRADERS_LIST_ADDITIONAL_WIDTH / 2;
      patchTraderLocation(this.location);
    },

    setTraderData(trader, ...args) {
      let shouldUpdateLocation = this._trader !== trader;
      this.parent(trader, ...args);
      if (shouldUpdateLocation) setTraderLocationText(this.location, trader);
    },
  });
});
