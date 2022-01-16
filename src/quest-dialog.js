sc.esp.addLocaleSpecificPatch(() => {
  // TODO: good candidate for inclusion into enhanced-ui
  sc.QuestStartDialogButtonBox.inject({
    init(...args) {
      this.parent(...args);
      let btn1 = this.acceptButton;
      let btn2 = this.declineButton;
      // left border + right border
      let totalBorderWidth = this.hook.size.x - btn1.hook.size.x;
      let prevBtnWidth = btn1.hook.size.x;
      // This will forcibly recompute the width of the buttons
      btn1.setText(btn1.text, false);
      btn2.setText(btn2.text, false);
      let newBtnWidth = Math.max(prevBtnWidth, btn1.hook.size.x, btn2.hook.size.x);
      btn1.setWidth(newBtnWidth);
      btn2.setWidth(newBtnWidth);
      this.hook.size.x = newBtnWidth + totalBorderWidth;
    },
  });
});
