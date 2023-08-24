/*# -*- coding: utf-8 -*- */
odoo.define("web_disable_delete", function(require) {
"use strict";

    var core = require("web.core");
    var Sidebar = require("web.Sidebar");
    var session = require("web.session");
    var _t = core._t;

    Sidebar.include({
        _addItems: function (sectionCode, items) {
            var _items = items;
            if (!session.is_superuser && sectionCode === 'other' && items.length && !session.group_hard_delete) {
                _items = _.reject(_items, {label:_t("Delete")});
            }
           
            this._super(sectionCode, _items);
        },
    });
});
