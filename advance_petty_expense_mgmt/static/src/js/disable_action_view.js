
odoo.define("disable_action_view", function(require) {
"use strict";

    var core = require("web.core");
    var Sidebar = require("web.Sidebar");
    var session = require("web.session");
    var _t = core._t;

    Sidebar.include({
        _addItems: function (sectionCode, items) {
            var _items = items;
            if (!session.is_superuser && sectionCode === 'other' && items.length && !session.petty_cash_auditor) {
                _items = _.reject(_items, {label:_t("Validate All Line")});
            }
            if (!session.is_superuser && sectionCode === 'other' && items.length && !session.petty_cash_auditor) {
                _items = _.reject(_items, {label:_t("Validate Posted Line")});
            }
            this._super(sectionCode, _items);
        },
    });
});
