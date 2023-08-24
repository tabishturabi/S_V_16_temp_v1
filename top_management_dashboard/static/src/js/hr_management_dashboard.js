odoo.define('hr_management_dashboard.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
//var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');

var _t = core._t;
var QWeb = core.qweb;


var HrManagementDashboard = AbstractAction.extend({
    template: 'HrManagementDashboardMain',
//    cssLibs: [
//        '/web/static/lib/nvd3/nv.d3.css'
//    ],
//    jsLibs: [
//        '/web/static/lib/nvd3/d3.v3.js',
//        '/web/static/lib/nvd3/nv.d3.js',
//        '/web/static/src/js/libs/nvd3.js'
//    ],
    events: {
        'click .get_on_job_employees': 'get_on_job_employees',
        'click .get_on_leave_employees': 'get_on_leave_employees',
        'click .get_on_trial_employees': 'get_on_trial_employees',
        'click .get_confirmed_decisions': 'get_confirmed_decisions',
        'click .get_leaves_request': 'get_leaves_request',
        'click .get_effective_request': 'get_effective_request',
        'click .get_clearances': 'get_clearances',
        "change select[name='filters']": '_onchange_select_timeline',
//        "change select[name='checks']": '_onchange_checks',

    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['HrDashboardDetails'];
    },

    willStart: function() {
        var self = this;
        console.log("............Inside will start of top management dashboard..............")
        return $.when(this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
//            self.update_cp();
            self.render_dashboards();
//            self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');
        });
    },
    _onchange_select_timeline:function(e){
        this.fetch_data_by_timeline();
    },
     on_reverse_breadcrumb: function() {
        var self = this;
        web_client.do_push_state({});
        this.update_cp();
        this.fetch_data_by_timeline().then(function() {
            self.$('.hr_management_dashboard').empty();
            self.render_dashboards();
        });
    },

    update_cp: function() {
        var self = this;
//        this.update_control_panel(
//            {breadcrumbs: self.breadcrumbs}, {clear: true}
//        );
    },
    get_on_job_employees:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Employees On Job"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
            domain: [['id','in', this.employees.on_job_employees_ids]],
            target: 'current'
        },options)
    },
    get_on_leave_employees:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Employees On Leave"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
            domain: [['id','in', this.employees.on_leave_employees_ids]],
            target: 'current'
        },options)
    },
     get_on_trial_employees:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Employees On Trial"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'kanban,tree,form',
            view_type: 'form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
            domain: [['id','in', this.employees.employees_on_trial_ids]],
            target: 'current'
        },options)
    },
    get_confirmed_decisions:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Approved Decisions"),
            type: 'ir.actions.act_window',
            res_model: 'employees.appointment',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.decisions.confirmed_decisions_ids]],
            target: 'current'
        },options)
    },
    get_leaves_request:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Leave Requests"),
            type: 'ir.actions.act_window',
            res_model: 'hr.leave',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.leaves.all_leaves_ids]],
            target: 'current'
        },options)
    },
    get_effective_request:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Effective Date Notice Requests"),
            type: 'ir.actions.act_window',
            res_model: 'effect.request',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.eff_requests.all_eff_requests_ids]],
            target: 'current'
        },options)
    },
    get_clearances:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Clearances"),
            type: 'ir.actions.act_window',
            res_model: 'hr.clearance',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.clearances.all_clearances_ids]],
            target: 'current'
        },options)
    },
    fetch_data: function() {
        var self = this;
//        var def3 = self._rpc({
//            model: "account.payment",
//            method: "get_payment_voucher_by_month",
//        })
//        .then(function (res) {
//            self.payment_voucher = res;
//        });
//        var def5 = self._rpc({
//            model: "bsg_vehicle_cargo_sale_line",
//            method: "get_agreements",
//        })
//        .then(function (agreements) {
//            self.agreements = agreements;
//        });
//        var def6 = self._rpc({
//            model: "fleet.vehicle.trip",
//            method: "get_all_trips_by_month",
//        })
//        .then(function (trip) {
//            self.trips = trip;
//        });
//        var def7 = self._rpc({
//            model: "fleet.vehicle",
//            method: "get_all_vehicles",
//        })
//        .then(function (vehicles) {
//            self.vehicles = vehicles;
//        });
//        var def8 = self._rpc({
//            model: "purchase.req",
//            method: "get_all_purchase_reqs_by_month",
//        })
//        .then(function (purchases) {
//            self.purchases = purchases;
//        });
        var def9 = self._rpc({
            model: "hr.employee",
            method: "get_all_employees",
        })
        .then(function (employees) {
            self.employees = employees;
        });
        var def10 = self._rpc({
            model: "employees.appointment",
            method: "get_all_decisions",
        })
        .then(function (decisions) {
            self.decisions = decisions;
        });
        var def11 = self._rpc({
            model: "hr.leave",
            method: "get_all_leaves",
        })
        .then(function (leaves) {
            self.leaves = leaves;
        });
        var def12 = self._rpc({
            model: "effect.request",
            method: "get_all_effective_requests",
        })
        .then(function (eff_requests) {
            self.eff_requests = eff_requests;
        });
        var def13 = self._rpc({
            model: "hr.clearance",
            method: "get_all_clearances",
        })
        .then(function (clearances) {
            self.clearances = clearances;
        });
        return $.when(def9,def10,def11,def12,def13);
    },
    fetch_data_by_timeline: function() {
        var self = this;
        if (self.$("select[name='filters']").val() === 'today'){
            var def4 = self._rpc({
            model: "account.payment",
            method: "get_payment_voucher_by_day",
            })
            .then(function (res) {
                self.payment_voucher = res;
                self.render_dashboards();
            });
            var def44 = self._rpc({
            model: "fleet.vehicle.trip",
            method: "get_all_trips_by_day",
            })
            .then(function (trip) {
                self.trips = trip;
                self.render_dashboards();
            });
//            var def444 = self._rpc({
//            model: "fleet.vehicle",
//            method: "get_all_vehicles_by_day",
//            })
//            .then(function (vehicles) {
//                self.vehicles = vehicles;
//                self.render_dashboards();
//            });
            var def4444 = self._rpc({
            model: "purchase.req",
            method: "get_all_purchase_reqs_by_day",
            })
            .then(function (purchases) {
                self.purchases = purchases;
                self.render_dashboards();
            });
        }
        else if (self.$("select[name='filters']").val() === 'week'){
            var def4 = self._rpc({
            model: "account.payment",
            method: "get_payment_voucher_by_week",
            })
            .then(function (res) {
                self.payment_voucher = res;
                self.render_dashboards();
            });
            var def44 = self._rpc({
            model: "fleet.vehicle.trip",
            method: "get_all_trips_by_week",
            })
            .then(function (trip) {
                self.trips = trip;
                self.render_dashboards();
            });
//            var def444 = self._rpc({
//            model: "fleet.vehicle",
//            method: "get_all_vehicles_by_week",
//            })
//            .then(function (vehicles) {
//                self.vehicles = vehicles;
//                self.render_dashboards();
//            });
            var def4444 = self._rpc({
            model: "purchase.req",
            method: "get_all_purchase_reqs_by_week",
            })
            .then(function (purchases) {
                self.purchases = purchases;
                self.render_dashboards();
            });
        }
        else if (self.$("select[name='filters']").val() === 'month'){
            var def4 = self._rpc({
            model: "account.payment",
            method: "get_payment_voucher_by_month",
            })
            .then(function (res) {
                self.payment_voucher = res;
                self.render_dashboards();
            });
            var def44 = self._rpc({
            model: "fleet.vehicle.trip",
            method: "get_all_trips_by_month",
            })
            .then(function (trip) {
                self.trips = trip;
                self.render_dashboards();
            });
//            var def444 = self._rpc({
//            model: "fleet.vehicle",
//            method: "get_all_vehicles_by_month",
//            })
//            .then(function (vehicles) {
//                self.vehicles = vehicles;
//                self.render_dashboards();
//            });
            var def4444 = self._rpc({
            model: "purchase.req",
            method: "get_all_purchase_reqs_by_month",
            })
            .then(function (purchases) {
                self.purchases = purchases;
                self.render_dashboards();
            });
        }
        else if (self.$("select[name='filters']").val() === 'year'){
            var def4 = self._rpc({
            model: "account.payment",
            method: "get_payment_voucher_by_year",
            })
            .then(function (res) {
                self.payment_voucher = res;
                self.render_dashboards();
            });
            var def44 = self._rpc({
            model: "fleet.vehicle.trip",
            method: "get_all_trips_by_year",
            })
            .then(function (trip) {
                self.trips = trip;
                self.render_dashboards();
            });
//            var def444 = self._rpc({
//            model: "fleet.vehicle",
//            method: "get_all_vehicles_by_year",
//            })
//            .then(function (vehicles) {
//                self.vehicles = vehicles;
//                self.render_dashboards();
//            });
            var def4444 = self._rpc({
            model: "purchase.req",
            method: "get_all_purchase_reqs_by_year",
            })
            .then(function (purchases) {
                self.purchases = purchases;
                self.render_dashboards();
            });
            }
        else{
            var def4 = self._rpc({
            model: "account.payment",
            method: "get_payment_voucher",
            })
            .then(function (res) {
                self.payment_voucher = res;
                self.render_dashboards();
            });
            var def44 = self._rpc({
            model: "fleet.vehicle.trip",
            method: "get_all_trips",
            })
            .then(function (trip) {
                self.trips = trip;
                self.render_dashboards();
            });
//            var def444 = self._rpc({
//            model: "fleet.vehicle",
//            method: "get_all_vehicles",
//            })
//            .then(function (vehicles) {
//                self.vehicles = vehicles;
//                self.render_dashboards();
//            });
            var def4444 = self._rpc({
            model: "purchase.req",
            method: "get_all_purchase_reqs",
            })
            .then(function (purchases) {
                self.purchases = purchases;
                self.render_dashboards();
            });
        }
        return $.when(def4,def44,def4444);
    },

//    _onchange_checks:function(){
//        var self = this;
//        if (self.$("select[name='checks']").val() === 'trips'){
//            $('.transit_trips')[0].parentElement.style.display = '';
//            $('.confirmed_trips')[0].parentElement.style.display = '';
//            $('.operations_trips')[0].parentElement.style.display = '';
//            $('.finished_trips')[0].parentElement.style.display = '';
//            $('.linked_vehicles')[0].parentElement.style.display = 'none';
//            $('.vehicles_in_maintenance')[0].parentElement.style.display = 'none';
//            $('.unlinked_vehicles')[0].parentElement.style.display = 'none';
//            $('.purchase_requests')[0].parentElement.style.display = 'none';
//        }
//        else if (self.$("select[name='checks']").val() === 'Vehicles'){
//            $('.linked_vehicles')[0].parentElement.style.display = '';
//            $('.vehicles_in_maintenance')[0].parentElement.style.display = '';
//            $('.unlinked_vehicles')[0].parentElement.style.display = '';
//             $('.transit_trips')[0].parentElement.style.display = 'none';
//            $('.confirmed_trips')[0].parentElement.style.display = 'none';
//            $('.operations_trips')[0].parentElement.style.display = 'none';
//            $('.finished_trips')[0].parentElement.style.display = 'none';
//            $('.purchase_requests')[0].parentElement.style.display = 'none';
//        }
//        else if (self.$("select[name='checks']").val() === 'Purchases'){
//            $('.purchase_requests')[0].parentElement.style.display = '';
//             $('.linked_vehicles')[0].parentElement.style.display = 'none';
//            $('.vehicles_in_maintenance')[0].parentElement.style.display = 'none';
//            $('.unlinked_vehicles')[0].parentElement.style.display = 'none';
//             $('.transit_trips')[0].parentElement.style.display = 'none';
//            $('.confirmed_trips')[0].parentElement.style.display = 'none';
//            $('.operations_trips')[0].parentElement.style.display = 'none';
//            $('.finished_trips')[0].parentElement.style.display = 'none';
//        }
//        else{
//            $('.transit_trips')[0].parentElement.style.display = 'none';
//            $('.confirmed_trips')[0].parentElement.style.display = 'none';
//            $('.operations_trips')[0].parentElement.style.display = 'none';
//            $('.finished_trips')[0].parentElement.style.display = 'none';
//            $('.linked_vehicles')[0].parentElement.style.display = 'none';
//            $('.vehicles_in_maintenance')[0].parentElement.style.display = 'none';
//            $('.unlinked_vehicles')[0].parentElement.style.display = 'none';
//            $('.purchase_requests')[0].parentElement.style.display = 'none';
//        }
//    },

    render_dashboards: function() {
        var self = this;
        if (this.employees){
            var templates = ['HrDashboardDetails']
            _.each(templates, function(template) {
                self.$('.hr_management_dashboard').empty();
                self.$('.hr_management_dashboard').append(QWeb.render(template, {widget: self}));
            });
        }
        else{
                self.$('.o_hr_dashboard').empty();
                self.$('.o_hr_dashboard').append(QWeb.render('HrManagementDashboardWarning', {widget: self}));
            }
    },
});


core.action_registry.add('top_management_dashboard.hr_management_dashboard', HrManagementDashboard);

return HrManagementDashboard;

});
