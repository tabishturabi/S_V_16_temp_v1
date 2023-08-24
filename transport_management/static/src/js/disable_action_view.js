
odoo.define("disable_driver_action_view", function(require) {
"use strict";

    var cores = require("web.core");
    var Sidebars = require("web.Sidebar");
    var sessions = require("web.session");
    var _t = cores._t;

    Sidebars.include({
        _addItems: function (sectionCodes, itemss) {
            var _itemss = itemss;
            if (!sessions.is_superuser && sectionCodes === 'other' && itemss.length && !sessions.group_get_driver_back) {
                _itemss = _.reject(_itemss, {label:_t("Retrieve Drivers")});
                console.log('===========111',_itemss,sessions.is_superuser,sectionCodes,itemss.length,sessions.group_get_driver_back)
            }
            this._super(sectionCodes, _itemss);
        },
    });
});
