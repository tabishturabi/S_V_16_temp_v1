odoo.define('sales_dashboard.sales_dashboard', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    
    var _t = core._t;
    var QWeb = core.qweb;

    var SalesDashBoard = AbstractAction.extend({
        events: {
            'change select#branch_selected_id': '_onChangeBranch',
        },
        init: function (parent, action) {
            this._super.apply(this, arguments);
            var self = this;
            self.has_admin_access = false
        },
        willStart: function () {
        var self = this;
        return this.getSession().user_has_group('base.group_system').then(function(has_group)
         {if(has_group) {self.has_admin_access = true;}
         else {self.has_admin_access = false;}});
    },
        start: function(){
            var self = this;
            var input = ''
            if (self.has_admin_access == true){input='all_branches'}
            else{input='your_branches'}
//                self._rpc({
//                model: 'sale.dashboard',
//                method: 'get_sales_info',
//                kwargs: [input,self.has_admin_access],
//            }, []).then(function(result){
//                self.sale_data = result
//            }).done(function(){
//                self.branch = self.sale_data['branches']
//                self.fleet_data = self.sale_data['fleet_data']
//                self.render();
//                self.bar_chart();
//                self.show_map();
//            });
            self._rpc({
                model: 'sale.dashboard',
                method: 'get_sales_info',
                kwargs: [input,self.has_admin_access],
            }, []).then(function(result){
                self.sale_data = result
                 self.branch = self.sale_data['branches']
                self.fleet_data = self.sale_data['fleet_data']
                self.render();
                self.bar_chart();
                self.show_map();
            });
            return this._super();
        },
        _load_data: function(){
            var self = this;
            self.render();
            self.bar_chart();
         },
        render: function() {
            var self = this;
            this.$el.empty();
            var branch_dashboard = $(QWeb.render("DashboardPage",{widget: self})).appendTo(this.$el);
            return branch_dashboard
        },
        _onChangeBranch: function(ev){
            var self = this;
            var $input = $(ev.target);
            var branch_id = $input.val()
//            var branch_dashboard_data = self._rpc({
//                model: 'sale.dashboard',
//                method: 'get_sales_info',
//                kwargs: [branch_id,self.has_admin_access],
//            }).then(function (res){
//               self.selected_branch =  branch_id;
//               self.sale_data = res
//
//            }).done(function(){
//                self.render();
//                self.bar_chart();
//                $("#branch_selected_id").children('option[value='+ self.selected_branch +']').prop('selected',true);
//
//            });
               var branch_dashboard_data = self._rpc({
                model: 'sale.dashboard',
                method: 'get_sales_info',
                kwargs: [branch_id,self.has_admin_access],
            }).then(function (res){
               self.selected_branch =  branch_id;
               self.sale_data = res
               self.render();
               self.bar_chart();
               $("#branch_selected_id").children('option[value='+ self.selected_branch +']').prop('selected',true);

            });
        },
        bar_chart: function(){
            var self = this;
            var data = self.sale_data['d1'];
            var layout = {barmode: 'stack'};
            Plotly.newPlot('myDiv', data, layout);

        },
        show_map: function(){
            var self = this;
            var data = [{
                type: 'scattergeo',
                mode: 'markers+text',
                text: [
                    'Jeddah', 'Khamis', 'Harmah', 'Unayzah', 'Taif',
                    'Sakaka', 'Arar', 'Yanbu', 'Hail', 'Riyadh'
                ],
                lon: [
                    39.172779, 42.759365, 45.318161, 43.973454, 40.512714,
                    40.197044, 41.016666, 38.026428, 41.696632, 46.738586
                ],
                lat: [
                    21.543333, 18.329384, 25.994478, 26.094088, 21.437273, 29.953894,
                    30.983334, 24.186848, 27.523647, 24.774265
                ],
                marker: {
                    size: 18,
                    color: [
                        '#bebada', '#fdb462', '#fb8072', '#d9d9d9', '#bc80bd',
                        '#b3de69', '#8dd3c7', '#80b1d3', '#fccde5', '#ffffb3'
                    ],
                    line: {
                        width: 1
                    }
                },
                name: 'Saudi Arab',
                textposition: [
                    'top right', 'top left', 'top center', 'bottom right', 'top right',
                    'top left', 'bottom right', 'bottom left', 'top right', 'top right'
                ],
            }];
            var layout = {
                title: 'Saudi Arab',
                width:1110,
                height:1000,
                font: {
                    family: 'Droid Serif, serif',
                    size: 13
                },
                titlefont: {
                    size: 16
                },
                geo: {
                    scope: 'asia',
                    resolution: 50,
                    lonaxis: {
                        'range': [30, 55]
                    },
                    lataxis: {
                        'range': [15, 35]
                    },
                    showrivers: true,
                    rivercolor: '#fff',
                    showlakes: true,
                    lakecolor: '#fff',
                    showland: true,
                    landcolor: "rgb(229, 229, 229)",
                    countrycolor: '#d3d3d3',
                    countrywidth: 1.5,
                    subunitcolor: '#d3d3d3'
                }
            };
            Plotly.newPlot('myDiv4', data, layout);
        },
    });
    core.action_registry.add('sales_dashboard.sales_dashboard', SalesDashBoard);
    return SalesDashBoard;
});
