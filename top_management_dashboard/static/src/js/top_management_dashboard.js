odoo.define('top_management_dashboard.Dashboard', function (require) {
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


var TopManagementDashboard = AbstractAction.extend({
    template: 'TopManagementDashboardMain',
//    cssLibs: [
//        '/web/static/lib/nvd3/nv.d3.css'
//    ],
//    jsLibs: [
//        '/web/static/lib/nvd3/d3.v3.js',
//        '/web/static/lib/nvd3/nv.d3.js',
//        '/web/static/src/js/libs/nvd3.js'
//    ],
    events: {
        'click .get_receipt_vouchers': 'receipt_vouchers',
        'click .get_portal_receipt_vouchers': 'portal_receipt_vouchers',
        'click .get_app_receipt_vouchers': 'app_receipt_vouchers',
        'click .get_payment_vouchers': 'payment_vouchers',
        'click .get_fuel_vouchers': 'get_fuel_vouchers',
        'click .get_transit_trips': 'get_transit_trips',
        'click .get_confirmed_trips': 'get_confirmed_trips',
        'click .get_operations_trips': 'get_operations_trips',
        'click .get_finished_trips': 'get_finished_trips',
        'click .get_linked_vehicles': 'get_linked_vehicles',
        'click .get_vehicles_in_maintenance': 'get_vehicles_in_maintenance',
        'click .get_unlinked_vehicles': 'get_unlinked_vehicles',
        'click .get_purchase_requests': 'get_purchase_requests',
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
        this.dashboards_templates = ['AccountPaymentDetails'];
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
            self.$('.payments_dashboard').empty();
            self.render_dashboards();
        });
    },

    update_cp: function() {
        var self = this;
//        this.update_control_panel(
//            {breadcrumbs: self.breadcrumbs}, {clear: true}
//        );
    },
    receipt_vouchers:function(e){
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Receit Vouchers"),
            type: 'ir.actions.act_window',
            res_model: 'account.payment',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.payment_voucher.receipt_vouchers_ids]],
            target: 'current'
        }, options)
    },
    portal_receipt_vouchers:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Portal Receit Vouchers"),
            type: 'ir.actions.act_window',
            res_model: 'account.payment',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.payment_voucher.portal_receipt_vouchers_ids]],
            target: 'current'
        },options)
    },
    app_receipt_vouchers:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("App Receit Vouchers"),
            type: 'ir.actions.act_window',
            res_model: 'account.payment',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.payment_voucher.app_receipt_vouchers_ids]],
            target: 'current'
        },options)
    },
    payment_vouchers:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Payment Vouchers"),
            type: 'ir.actions.act_window',
            res_model: 'account.payment',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.payment_voucher.payment_vouchers_ids]],
            target: 'current'
        },options)
    },
    get_fuel_vouchers:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Payment Vouchers"),
            type: 'ir.actions.act_window',
            res_model: 'account.payment',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.payment_voucher.fuel_vouchers_ids]],
            target: 'current'
        },options)
    },
    get_transit_trips:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Transit Trips"),
            type: 'ir.actions.act_window',
            res_model: 'fleet.vehicle.trip',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.trips.transit_trips_ids]],
            target: 'current'
        },options)
    },
    get_confirmed_trips:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Confirmed Trips"),
            type: 'ir.actions.act_window',
            res_model: 'fleet.vehicle.trip',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.trips.confirmed_trips_ids]],
            target: 'current'
        },options)
    },
    get_operations_trips:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        console.log('..........operations_trips_ids.........',this.trips.operations_trips_ids)
        this.do_action({
            name: _t("Operations Trips"),
            type: 'ir.actions.act_window',
            res_model: 'fleet.vehicle.trip',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.trips.operations_trips_ids]],
            target: 'current'
        },options)
    },
    get_finished_trips:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Finished Trips"),
            type: 'ir.actions.act_window',
            res_model: 'fleet.vehicle.trip',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.trips.finished_trips_ids]],
            target: 'current'
        },options)
    },
    get_linked_vehicles:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Linked Vehicles"),
            type: 'ir.actions.act_window',
            res_model: 'fleet.vehicle',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.vehicles.vehicles_in_service_ids]],
            target: 'current'
        },options)
    },
    get_vehicles_in_maintenance:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Vehicles In Maintenance"),
            type: 'ir.actions.act_window',
            res_model: 'fleet.vehicle',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.vehicles.vehicles_in_maintenance_ids]],
            target: 'current'
        },options)
    },
    get_unlinked_vehicles:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Unlinked Vehicles"),
            type: 'ir.actions.act_window',
            res_model: 'fleet.vehicle',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.vehicles.vehicles_unlinked_ids]],
            target: 'current'
        },options)
    },
    get_purchase_requests:function(e){
        var self = this;
//        e.stopPropagation();
//        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Purchase Requests"),
            type: 'ir.actions.act_window',
            res_model: 'purchase.req',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['id','in', this.purchases.purchase_requests_ids]],
            target: 'current'
        },options)
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
        var def3 = self._rpc({
            model: "account.payment",
            method: "get_payment_voucher_by_month",
        })
        .then(function (res) {
            self.payment_voucher = res;
        });
//        var def5 = self._rpc({
//            model: "bsg_vehicle_cargo_sale_line",
//            method: "get_agreements",
//        })
//        .then(function (agreements) {
//            self.agreements = agreements;
//        });
        var def6 = self._rpc({
            model: "fleet.vehicle.trip",
            method: "get_all_trips_by_month",
        })
        .then(function (trip) {
            self.trips = trip;
        });
        var def7 = self._rpc({
            model: "fleet.vehicle",
            method: "get_all_vehicles",
        })
        .then(function (vehicles) {
            self.vehicles = vehicles;
        });
        var def8 = self._rpc({
            model: "purchase.req",
            method: "get_all_purchase_reqs_by_month",
        })
        .then(function (purchases) {
            self.purchases = purchases;
        });
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
        return $.when(def3,def6,def7,def8,def9,def10,def11,def12,def13);
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
        if (this.payment_voucher){
            var templates = ['AccountPaymentDetails']
            _.each(templates, function(template) {
                self.$('.payments_dashboard').empty();
                self.$('.payments_dashboard').append(QWeb.render(template, {widget: self}));
            });
        }
        else{
                self.$('.o_hr_dashboard').empty();
                self.$('.o_hr_dashboard').append(QWeb.render('PaymentWarning', {widget: self}));
            }
    },
});


//core.action_registry.add('top_management_dashboard.top_management_dashboard', TopManagementDashboard);
core.action_registry.add('top_management_dashboard', TopManagementDashboard);

return TopManagementDashboard;

});
