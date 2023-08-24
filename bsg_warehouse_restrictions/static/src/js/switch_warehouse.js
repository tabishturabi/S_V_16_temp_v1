///** @odoo-module **/
//
//import { Dropdown } from "@web/core/dropdown/dropdown";
//import { DropdownItem } from "@web/core/dropdown/dropdown_item";
//import { useService } from "@web/core/utils/hooks";
//import { registry } from "@web/core/registry";
//import { browser } from "@web/core/browser/browser";
//import { symmetricalDifference } from "@web/core/utils/arrays";
//
//import { Component, useState,onWillStart } from "@odoo/owl";
//
//export class SwitchUserWarehouse extends Component {
//    setup() {
//        this.companyService = useService("company");
//        this.userService = useService("user");
//        this.orm = useService("orm");
//         onWillStart(async () => {
//            const current_wh_user = this.env.services.user.userId
//            this.data = await this.orm.searchRead("res.users", [["id", "=", current_wh_user]], ["stock_warehouse_id",'stock_warehouse_ids'])
//            this.user_wh_ids = await this.orm.searchRead("stock.warehouse", [["id", "in", this.data[0].stock_warehouse_ids]], ["id","name"])
//            this.currentWarehouse = this.data[0].stock_warehouse_id[1]
//            this.currentWarehouseId = this.data[0].stock_warehouse_id[0]
//            console.log("this.user_branch_ids = ")
//            console.log(this.user_wh_ids)
//        });
//        this.currentCompany = this.companyService.currentCompany;
//        this.state = useState({ wareHouseToToggle: [] });
//    }
//
//    toggleWarehouse(warehouse) {
//        this.state.wareHouseToToggle = symmetricalDifference(this.state.wareHouseToToggle, [
//            warehouse.id,
//        ]);
//        console.log("companies toggle before");
//        console.log(this.state.branchesToToggle);
//        browser.clearTimeout(this.toggleTimer);
//        this.toggleTimer = browser.setTimeout(() => {
////            this.companyService.setCompanies("toggle", ...this.state.companiesToToggle);
//            this.setWarehouses(warehouse);
//        }, this.constructor.toggleDelay);
//    }
//
//    logIntoWarehouse(warehouse) {
//        console.log("log into company");
//        console.log(branch);
//        this.setWarehouses(warehouse)
//
////        browser.clearTimeout(this.toggleTimer);
////        this.companyService.setCompanies("loginto", companyId);
////        this.setBranches(companyId)
//    }
//
//    async setWarehouses(wareHouseId){
//        const userId = this.env.services.user.userId
//        await this.orm.write("res.users", [userId], {
//                stock_warehouse_id: wareHouseId.id,
//            });
////        browser.clearTimeout(this.toggleTimer);
//        browser.location.reload();
//
//    }
//
//    get selectedWarehouses() {
//        console.log('this.companyService = ')
//        console.log(this.selectedbranch)
//        return symmetricalDifference(
//            this.companyService.allowedCompanyIds,
//            this.state.wareHouseToToggle
//        );
//    }
//}
//SwitchUserWarehouse.template = "bsg_warehouse_restrictions.SwitchUserWarehouse";
//SwitchUserWarehouse.components = { Dropdown, DropdownItem };
//SwitchUserWarehouse.toggleDelay = 1000;
//
//export const systrayItem = {
//    Component: SwitchUserWarehouse,
//    async isDisplayed(env) {
//        const current_user = env.services.user.userId
//        console.log('env.services.company')
//        console.log(env.services.company)
//        const { availableCompanies } = env.services.company;
////        const { availableCompanies } = await env.services.orm.searchRead("res.users", [["id", "=", current_user]], ["user_branch_ids"]);
////        console.log('availableCompanies are ')
////        console.log(availableCompanies)
////        const { availableCompanies } = env.services.company;
//
////        env.services.orm.searchRead("res.users", [["id", "=", current_user]], ["user_branch_ids"]).then((obj)=>{
////            env.services.orm.searchRead("bsg_branches.bsg_branches", [["id", "in", obj[0].user_branch_ids]], ["branch_ar_name"]).then((branch_obj)=>{
////                const {user_branch_ids} = branch_obj
////                console.log("search user_branch_ids are = ")
////                console.log(user_branch_ids)
////
////        });
////            const {user_branch_ids} = this.getUserBranchIds(obj)
////            console.log("search user_branch_ids are = ")
////            console.log(obj)
////            return Object.keys(obj[0]).length > 1;
//
////        });
////        env.services.orm.search("res.users", [["id", "=", current_user]]).then((obj)=>{
////            console.log("search user obj are = ")
////            console.log(obj)
////
////        });
////        console.log('user_branch_ids are')
////        console.log(user_branch_ids)
////        console.log(env.services.user.user_branch_ids)
//        return Object.keys(availableCompanies).length > 1;
//    },
//};
//
//registry.category("systray").add("SwitchUserWarehouse", systrayItem, { sequence: 1 });
//
////odoo.define('web.SwitchUserWarehouse', function(require) {
////"use strict";
////
/////**
//// # -*- coding: utf-8 -*-
//// */
////
////var config = require('web.config');
////var core = require('web.core');
////var session = require('web.session');
////var SystrayMenu = require('web.SystrayMenu');
////var Widget = require('web.Widget');
////
////var _t = core._t;
////
////var SwitchUserWarehouse = Widget.extend({
////    template: 'SwitchUserWarehouse',
////    events: {
////        'click .dropdown-item[data-menu]': '_onClick',
////    },
////    /**
////     * @override
////     */
////    init: function () {
////        this._super.apply(this, arguments);
////        this.isMobile = config.device.isMobile;
////        this._onClick = _.debounce(this._onClick, 1500, true);
////    },
////    /**
////     * @override
////     */
////    willStart: function () {
////        return session.user_warehouse ? this._super() : $.Deferred().reject();
////    },
////    /**
////     * @override
////     */
////    start: function () {
////        var warehouseList = '';
////        if (this.isMobile) {
////            warehouseList = '<li class="bg-info">' +
////                _t('Tap on the list to change Warehouse') + '</li>';
////        }
////        else {
////            this.$('.oe_topbar_name').text(session.user_warehouse[0].current_warehouse[1]);
////        }
////        _.each(session.user_warehouse[0].allowed_warehouse, function(warehouse) {
////            var a = '';
////            if (warehouse[0] === session.user_warehouse[0].current_warehouse[0]) {
////                a = '<i class="fa fa-check mr8"></i>';
////            } else {
////                a = '<span style="margin-right: 24px;"/>';
////            }
////            warehouseList += '<a role="menuitem" href="#" class="dropdown-item" data-menu="warehouse" data-warehouse-id="' +
////            warehouse[0] + '">' + a + warehouse[1] + '</a>';
////        });
////        this.$('.dropdown-menu').html(warehouseList);
////        return this._super();
////    },
////
////    //--------------------------------------------------------------------------
////    // Handlers
////    //--------------------------------------------------------------------------
////
////    /**
////     * @private
////     * @param {MouseEvent} ev
////     */
////    _onClick: function (ev) {
////        ev.preventDefault();
////        var warehouseID = $(ev.currentTarget).data('warehouse-id');
////        this._rpc({
////            model: 'res.users',
////            method: 'write',
////            args: [[session.uid], {'warehouse-id': warehouseID}],
////        })
////        .then(function() {
////            location.reload();
////        });
////    },
////});
////
////SystrayMenu.Items.push(SwitchUserWarehouse);
////
////return SwitchUserWarehouse;
////
////});
