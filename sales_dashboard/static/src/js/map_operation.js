odoo.define('map_operation.map_operation', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session  = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;

    var MapsDashBoard = AbstractAction.extend({
    	events: {
			'click .arrived_cars_data': '_arrived_cars_data',
			'click .shiping_cars_data': '_shiping_cars_data',
			'click .trucks_final_stop_data': '_trucks_final_stop_data',
			'click .trucks_data': '_trucks_data',
			'click .trucks_coming_data': '_trucks_coming_data',
			'click .branch_info': '_branch_info',
			'click .tot_trucks_final': '_tot_trucks_final',
			'click .tot_shipping_cars': '_tot_shipping_cars',
			'click .tot_trucks_avail': '_tot_trucks_avail',
			'click .tot_trucks_coming': '_tot_trucks_coming',
			'click .tot_arrived_cars': '_tot_arrived_cars',
			'click .tot_maintenance_cars': '_tot_maintenance_cars',

		},
        init: function (parent, action) {
            this._super.apply(this, arguments);
            var self = this;
        },
        start: function(){
            var self = this;
            self._rpc({
                model: 'map.operation',
                method: 'get_operations_info',
            }, []).then(function(result){
                self.map_data = result
            }).then(function(){
                self.fleet_data = self.map_data['fleet_data']
                self.tot_trucks_avail = self.map_data['tot_trucks_avail']
                self.tot_trucks_final = self.map_data['tot_trucks_final']
                self.tot_trucks_coming = self.map_data['tot_trucks_coming']
                self.tot_shipping_cars = self.map_data['tot_shipping_cars']
                self.tot_arrived_cars = self.map_data['tot_arrived_cars']
                self.tot_maintenance_cars = self.map_data['tot_maintenance_cars']
                self.render();
            });
            return this._super();
        },
        render: function() {
            var self = this;
            this.$el.empty();
            var map_dashboard = $(QWeb.render("OperationPage",{widget: self},{'lang':'ar_AA'})).appendTo(this.$el);
            return map_dashboard
        },
        _arrived_cars_data: function (event) {
			var self = this;
			debugger;
			this._rpc({model: "map.operation",method: 'arrived_cars_data',
                        kwargs: [event.target.id]
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _shiping_cars_data: function (event) {
			var self = this;
			this._rpc({model: "map.operation",method: 'shiping_cars_data',
                    kwargs: [event.target.id]
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _trucks_final_stop_data: function (event) {
			var self = this;
			debugger
			this._rpc({model: "map.operation",
			        method: 'trucks_final_stop_data',
                    kwargs: [event.target.id]
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _trucks_data: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'trucks_data',
                    kwargs: [event.target.id]
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _trucks_coming_data: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'trucks_coming_data',
                    kwargs: [event.target.id]
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _branch_info: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'branch_info',
                    kwargs: [event.target.id]
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _tot_trucks_final: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'tot_trucks_final',
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _tot_shipping_cars: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'tot_shipping_cars',
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _tot_trucks_avail: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'tot_trucks_avail',
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _tot_trucks_coming: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'tot_trucks_coming',
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _tot_arrived_cars: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'tot_arrived_cars',
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},
        _tot_maintenance_cars: function (event) {
			var self = this;
			this._rpc({model: "map.operation",
			        method: 'tot_maintenance_cars',
                    })
                    .then(function (res) {
                     self.do_action(res);

                    });
		},

    });
    core.action_registry.add('map_operation.map_operation', MapsDashBoard);
    return MapsDashBoard;
});
