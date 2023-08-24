//
//odoo.define("web_disable_archive_exp_type", function(require) {
//"use strict";
//
//    var core = require("web.core");
//    var Sidebar = require("web.Sidebar");
//    var session = require("web.session");
//    var _t = core._t;
//
//    Sidebar.include({
//        _addItems: function (sectionCode, items) {
//            var _items = items;
//            if(this.modelName == "hr.employee"){
//                if (!session.is_superuser && sectionCode === 'other' && items.length && !session.group_employee_archive) {
//                    _items = _.reject(_items, {label:_t("Archive")});
//                }
//                if (!session.is_superuser && sectionCode === 'other' && items.length && !session.group_employee_archive) {
//                    _items = _.reject(_items, {label:_t("Unarchive")});
//                }
//            }
//            this._super(sectionCode, _items);
//        },
//    });
//});
