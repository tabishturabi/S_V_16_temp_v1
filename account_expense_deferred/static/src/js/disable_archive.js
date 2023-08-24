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
//            if(this.modelName == "account.asset.category"){
//                if (!session.is_superuser && sectionCode === 'other' && items.length && !session.group_deferred_exp_type_archive) {
//                    _items = _.reject(_items, {label:_t("Archive")});
//                }
//                if (!session.is_superuser && sectionCode === 'other' && items.length && !session.group_deferred_exp_type_archive) {
//                    _items = _.reject(_items, {label:_t("Unarchive")});
//                }
//            }
//            this._super(sectionCode, _items);
//        },
//    });
//});
//
//odoo.define("web_disable_archive_exp", function(require) {
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
//            if(this.modelName == "account.asset.asset"){
//                if (!session.is_superuser && sectionCode === 'other' && items.length && !session.group_deferred_exp_archive) {
//                    _items = _.reject(_items, {label:_t("Archive")});
//                }
//                if (!session.is_superuser && sectionCode === 'other' && items.length && !session.group_deferred_exp_archive) {
//                    _items = _.reject(_items, {label:_t("Unarchive")});
//                }
//            }
//            this._super(sectionCode, _items);
//        },
//    });
//});