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
//export class SwitchBranchMenu extends Component {
//    setup() {
//        this.companyService = useService("company");
//        this.userService = useService("user");
//        this.orm = useService("orm");
//         onWillStart(async () => {
//            const current_user = this.env.services.user.userId
//            this.data = await this.orm.searchRead("res.users", [["id", "=", current_user]], ["user_branch_id",'user_branch_ids'])
//            this.user_branch_ids = await this.orm.searchRead("bsg_branches.bsg_branches", [["id", "in", this.data[0].user_branch_ids]], ["id","branch_ar_name"])
//            this.currentBranch = this.data[0].user_branch_id[1]
//            this.currentBranchId = this.data[0].user_branch_id[0]
//            console.log("this.user_branch_ids = ")
//            console.log(this.user_branch_ids)
//        });
//        this.currentCompany = this.companyService.currentCompany;
//        this.state = useState({ branchesToToggle: [] });
//    }
//
//    toggleBranch(branch) {
//        this.state.branchesToToggle = symmetricalDifference(this.state.branchesToToggle, [
//            branch.id,
//        ]);
//        console.log("companies toggle before");
//        console.log(this.state.branchesToToggle);
//        browser.clearTimeout(this.toggleTimer);
//        this.toggleTimer = browser.setTimeout(() => {
////            this.companyService.setCompanies("toggle", ...this.state.companiesToToggle);
//            this.setBranches(branch);
//        }, this.constructor.toggleDelay);
//    }
//
//    logIntoBranch(branch) {
//        console.log("log into company");
//        console.log(branch);
//        this.selectedbranch = [branch.id]
//        this.setBranches(branch)
//
////        browser.clearTimeout(this.toggleTimer);
////        this.companyService.setCompanies("loginto", companyId);
////        this.setBranches(companyId)
//    }
//
//    async setBranches(branchId){
//        const userId = this.env.services.user.userId
//        await this.orm.write("res.users", [userId], {
//                user_branch_id: branchId.id,
//            });
////        browser.clearTimeout(this.toggleTimer);
//        browser.location.reload();
//
//    }
//
//    get selectedCompanies() {
//        console.log('this.companyService = ')
//        console.log(this.selectedbranch)
//        return symmetricalDifference(
//            this.companyService.allowedCompanyIds,
//            this.state.branchesToToggle
//        );
//    }
//}
//SwitchBranchMenu.template = "easy_switch_branch.SwitchBranchMenu";
//SwitchBranchMenu.components = { Dropdown, DropdownItem };
//SwitchBranchMenu.toggleDelay = 1000;
//
//export const systrayItem = {
//    Component: SwitchBranchMenu,
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
//registry.category("systray").add("SwitchBranchMenu", systrayItem, { sequence: 1 });
//
////odoo.define('web.SwitchUserbranch', function(require) {
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
////var SwitchUserbranch = Widget.extend({
////    template: 'SwitchUserbranch',
////    events: {
////        'click .dropdown-item[data-menu]': '_onClick',
////        'click #test': '_onTestClick',
////
////    },
////    /**
////     * @override
////     */
////    init: function () {
////        this._super.apply(this, arguments);
////        this.isMobile = config.device.isMobile;
//////        this._onClick = _.debounce(this._onClick, 1500, true);
////        console.log('.............SwitchUserbranch init............')
////    },
////    /**
////     * @override
////     */
////    willStart: function () {
////        return session.user_banch ? this._super() : $.Deferred().reject();
////    },
////    /**
////     * @override
////     */
////    start: function () {
////        var branchList = '';
////        console.log('.............SwitchUserbranch start............')
////        console.log('...............session.user_banch.........')
////        console.log(session.user_banch)
////        if (this.isMobile) {
////            branchList = '<li class="bg-info">' +
////                _t('Tap on the list to change Branch') + '</li>';
////        }
////        else {
////            this.$('.oe_topbar_name').text(session.user_banch[0].current_branch[1]);
////        }
////        _.each(session.user_banch[0].allowed_branch, function(branch) {
////            var a = '';
////            if (branch[0] === session.user_banch[0].current_branch[0]) {
////                a = '<i class="fa fa-check mr8"></i>';
////            } else {
////                a = '<span style="margin-right: 24px;"/>';
////            }
////            branchList += '<a role="menuitem" href="#" class="dropdown-item" data-menu="branch" data-branch-id="' +
////                            branch[0] + '">' + a + branch[1] + '</a>';
////        });
//////        console.log(branchList)
////        this.$('.dropdown-menu').html(branchList);
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
////
////    _onTestClick: function (ev) {
////        confirm("Press a button!\nEither OK or Cancel.");
////    },
////    _onClick: function (ev) {
////        ev.preventDefault();
////        var branchID = $(ev.currentTarget).data('branch-id');
////        this._rpc({
////            model: 'res.users',
////            method: 'write',
////            args: [[session.uid], {'branch-id': branchID}],
////        })
////        .then(function() {
////            location.reload();
////        });
////    },
////});
////
////SystrayMenu.Items.push(SwitchUserbranch);
////
////return SwitchUserbranch;
////
////});
