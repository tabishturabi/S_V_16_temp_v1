import pandas as pd
from odoo import _, api, fields, models
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


class SaleDashboard(models.Model):
    _name = "map.operation"
    _description = 'Map Operation'

    def dhms_from_seconds(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return (days, hours, minutes)

    def date_diff_in_seconds(self, dt2, dt1):
        timedelta = dt2 - dt1
        return timedelta.days * 24 * 3600 + timedelta.seconds

    @api.model
    def get_operations_info(self):
        fleet_status = self.env['bsg_branches.bsg_branches'].search([])
        fleet_dict = {}
        tot_trucks_avail = 0
        tot_trucks_final = 0
        tot_trucks_coming = 0
        tot_shipping_cars = 0
        tot_arrived_cars = 0
        tot_maintenance_cars = self.sudo().env['maintenance.request.enhance'].search_count([('vehicle_id', '!=', False),('state', 'not in', ['4','5'])])

        for fleet in fleet_status:
            fleet_dict[str(fleet.branch_no)] = {'trucks_avail': fleet.trucks_available if fleet.trucks_available else 0,
                                                'id': fleet.id,
                                                'trucks_final': fleet.trucks_final_stop if fleet.trucks_final_stop else 0,
                                                'trucks_coming': fleet.trucks_comming if fleet.trucks_comming else 0,
                                                'shipping_cars': fleet.shiping_cars if fleet.shiping_cars else 0,
                                                'arrived_cars': fleet.arrived_cars if fleet.arrived_cars else 0}
            if fleet.branch_no in ['46', '31', '54', '91', '18', '24', '13', '10', '44', '3', '2', '33', '55', '39',
                                   '19', '28', '49', '17',
                                   '15', '52', '59', '16', '5', '14', '21', '20', '23', '12', '11', '22', '58', '9',
                                   '25', '32', '34', '41', '60', '92', '96', '93', '27', '26', '35', '103', '6', '47',
                                   '37', '62', '61', '4', '63', '56', '30', '38', '200']:
                tot_trucks_avail = tot_trucks_avail + fleet.trucks_available
                tot_trucks_final = tot_trucks_final + fleet.trucks_final_stop
                tot_trucks_coming = tot_trucks_coming + fleet.trucks_comming
                tot_shipping_cars = tot_shipping_cars + fleet.shiping_cars
                tot_arrived_cars = tot_arrived_cars + fleet.arrived_cars
        data = {'fleet_data': fleet_dict, 'tot_trucks_avail': tot_trucks_avail, 'tot_trucks_final': tot_trucks_final,
                'tot_trucks_coming': tot_trucks_coming, 'tot_shipping_cars': tot_shipping_cars,
                'tot_arrived_cars': tot_arrived_cars, 'tot_maintenance_cars': tot_maintenance_cars}
        return data

    @api.model
    def arrived_cars_data(self, **kw):
        print(kw)
        if kw['0']:
            branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', kw['0'])])
            last_month = datetime.now() - relativedelta(months=1)
            ship_ids = self.env['bsg_vehicle_cargo_sale_line'].search(
                [('is_package', '=', False), ('create_date', '>=', last_month),
                 ('loc_to.loc_branch_id.id', '=', branch_id.id),
                 ('state', 'in', ['Delivered'])], order="order_date asc")
            return {
                'type': 'ir.actions.act_window',
                'name': 'Arrived Cars',
                'res_model': 'bsg_vehicle_cargo_sale_line',
                'views': [[False, 'list'], [False, 'form']],
                'domain': [('id', 'in', ship_ids.ids)],
            }

    @api.model
    def branch_info(self, **kw):
        print(kw)
        if kw['0']:
            branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', kw['0'])])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Branches',
                'res_id': branch_id.id,
                'res_model': 'bsg_branches.bsg_branches',
                'views': [[self.env.ref('sales_dashboard.bsg_branches_view_form_sales_dashboard').id, 'form']],
            }

    @api.model
    def shiping_cars_data(self, **kw):
        if kw['0']:
            branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', kw['0'])])
            req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', branch_id.id)], limit=1)
            last_month = datetime.now() - relativedelta(months=1)
            ship_ids = self.env['bsg_vehicle_cargo_sale_line'].search(
                [('is_package', '=', False), ('create_date', '>=', last_month),
                 ('cargo_sale_state', 'in', ['done', 'pod']),
                 ('state', 'in', ['draft', 'on_transit']), '|', ('loc_from.id', '=', req_branch.id),
                 ('pickup_loc.id', '=', req_branch.id)], order="order_date asc")
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cars To Ship',
                'res_model': 'bsg_vehicle_cargo_sale_line',
                'views': [[False, 'list'], [False, 'form']],
                'domain': [('id', 'in', ship_ids.ids)],
            }

    @api.model
    def trucks_final_stop_data(self, **kw):
        if kw['0']:
            branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', kw['0'])])
            req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', branch_id.id)], limit=1)

            table_name = "fleet_vehicle as fv"
            self.env.cr.execute(
                "select fv.id as id,fv.current_branch_id as current_branch_id FROM " + table_name + " join bsg_vehicle_type_table as vt on vt.id = fv.vehicle_type where vt.include_in_fleet_status is true and state_id=2 ")
            result = self._cr.fetchall()
            trucks_frame = pd.DataFrame(list(result))
            trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})
            last_month = str(datetime.now() - relativedelta(months=1))
            table_name = "fleet_vehicle_trip"
            self.env.cr.execute(
                "select id,state,vehicle_id,route_id,expected_end_date FROM " + table_name + " where create_date >= '%s' " % last_month)
            trip_result = self._cr.fetchall()
            trip_frame = pd.DataFrame(list(trip_result))
            trip_frame = trip_frame.rename(
                columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet', 3: 'route_id', 4: 'expected_end_date'})

            table_name = "fleet_vehicle_trip_waypoints"
            self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
            waypoints_result = self._cr.fetchall()
            waypoints_frame = pd.DataFrame(list(waypoints_result))
            waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

            waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

            if not (result and trip_result and waypoints_result):
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Trucks Final Stop',
                    'res_model': 'fleet.vehicle',
                    'domain': [('id', 'in', [])],
                    'views': [
                        [self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
                }

            waypoints_frame_last = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="last")

            trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isin(['progress', 'on_transit', 'confirmed']))]

            trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                        right_on='truck_id')

            trip_frame_final_last = pd.merge(trip_frame_final, waypoints_frame_last, how='left', left_on='trip_id',
                                             right_on='way_trip_id')

            trip_frame_final_last = trip_frame_final_last.loc[(trip_frame_final_last['waypoint'] == req_branch.id)]

            trip_frame_final_last = trip_frame_final_last.drop_duplicates(subset='truck_id', keep="first")

            trip_frame_final_last = trip_frame_final_last[trip_frame_final_last.truck_id.notnull()]

            truck_ids = []
            for index, line in trip_frame_final_last.iterrows():
                truck_ids.append(int(line['truck_id']))
                truck_data = self.env['fleet.vehicle'].search([('id', '=', int(line['truck_id']))], limit=1)
                trip_data = self.env['fleet.vehicle.trip'].search([('id', '=', int(line['trip_id']))], limit=1)
                truck_data.trip_id = int(line['trip_id'])
                if line['route_id'] > 0:
                    truck_data.route_id = int(line['route_id'])
                truck_data.expected_end_date = line['expected_end_date']
                truck_data.no_of_cars = str(len(trip_data.stock_picking_id))
                date2 = datetime.now() + relativedelta(hours=5)
                date1 = line['expected_end_date']
                if date2 > date1:
                    truck_data.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(
                        self.date_diff_in_seconds(date2, date1))
                else:
                    truck_data.time_diff = str('0')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Trucks Final Stop',
                'res_model': 'fleet.vehicle',
                'views': [[self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
                'domain': [('id', 'in', truck_ids)],
            }

    @api.model
    def trucks_data(self, **kw):
        if kw['0']:
            branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', kw['0'])])
            truck_ids = self.env['fleet.vehicle'].search(
                [('vehicle_type.include_in_fleet_status', '=', True), ('current_branch_id', '=', branch_id.id),
                 ('state_id', '=', 2)])
            for tr in truck_ids:
                last_month = datetime.now() - relativedelta(months=1)

                trips = self.env['fleet.vehicle.trip'].search(
                    [('create_date', '>=', last_month), ('state', 'not in', ['finished', 'cancelled']),
                     ('vehicle_id.id', '=', tr.id)], order="expected_end_date asc", limit=1)
                if trips:
                    tr.trip_id = trips.id
                    tr.route_id = trips.route_id.id
                    tr.expected_end_date = trips.expected_end_date
                    tr.no_of_cars = str(len(trips.stock_picking_id))
                    date2 = datetime.now() + relativedelta(hours=5)
                    date1 = trips.expected_end_date
                    if date2 > date1:
                        tr.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(
                            self.date_diff_in_seconds(date2, date1))
                    else:
                        tr.time_diff = str('0')

            return {
                'type': 'ir.actions.act_window',
                'name': 'Trucks Available',
                'res_model': 'fleet.vehicle',
                'domain': [('id', 'in', truck_ids.ids)],
                'views': [[self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
            }

    @api.model
    def trucks_coming_data(self, **kw):
        if kw['0']:
            branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', '=', kw['0'])])

            req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', branch_id.id)], limit=1)

            table_name = "fleet_vehicle as fv"
            self.env.cr.execute(
                "select fv.id as id,fv.current_branch_id as current_branch_id FROM " + table_name + " join bsg_vehicle_type_table as vt on vt.id = fv.vehicle_type where vt.include_in_fleet_status is true and state_id=2 ")
            result = self._cr.fetchall()
            trucks_frame = pd.DataFrame(list(result))
            trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})
            last_month = str(datetime.now() - relativedelta(months=1))
            table_name = "fleet_vehicle_trip"
            self.env.cr.execute(
                "select id,state,vehicle_id,route_id,expected_end_date, start_branch FROM " + table_name + " where create_date >= '%s' and state != 'finished' " % last_month)
            trip_result = self._cr.fetchall()
            trip_frame = pd.DataFrame(list(trip_result))
            trip_frame = trip_frame.rename(
                columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet', 3: 'route_id', 4: 'expected_end_date',
                         5: 'start_branch'})

            # table_name = "fleet_trip_arrival"
            # self.env.cr.execute("select id,waypoint_to,trip_id,is_done_survey FROM "+table_name+" ")
            # waypoints_result = self._cr.fetchall()
            # waypoints_frame = pd.DataFrame(list(waypoints_result))
            # waypoints_frame = waypoints_frame.rename(columns={0: 'way_id',1: 'waypoint',2: 'way_trip_id',3: 'is_done_survey'})

            table_name = "fleet_vehicle_trip_waypoints"
            self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
            waypoints_result = self._cr.fetchall()
            waypoints_frame = pd.DataFrame(list(waypoints_result))

            waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

            waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

            if not (result and trip_result and waypoints_result):
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Trucks Comming',
                    'res_model': 'fleet.vehicle',
                    'domain': [('id', 'in', [])],
                    'views': [
                        [self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'list']]
                }
            waypoints_frame_coming = waypoints_frame.loc[(waypoints_frame['waypoint'] == req_branch.id)]
            waypoints_frame_coming = waypoints_frame_coming[waypoints_frame_coming.way_trip_id.notnull()]

            waypoints_frame_coming = waypoints_frame_coming.drop_duplicates(subset='way_trip_id', keep="last")

            trip_frame_final = trip_frame.loc[
                (trip_frame['start_branch'] != req_branch.id) & (trip_frame['trip_state'] != 'draft') & (
                        trip_frame['trip_state'] != 'finished') & (trip_frame['trip_state'] != 'cancelled')]

            trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                        right_on='truck_id')

            trip_frame_final_coming = pd.merge(trip_frame_final, waypoints_frame_coming, how='left', left_on='trip_id',
                                               right_on='way_trip_id')

            trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.way_trip_id.notnull()]
            trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.trip_id.notnull()]
            trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.truck_id.notnull()]

            trip_frame_final_coming = trip_frame_final_coming.drop_duplicates(subset='truck_id', keep="first")

            # trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.truck_id.notnull()]

            truck_ids = []
            for index, line in trip_frame_final_coming.iterrows():
                truck_data = self.env['fleet.vehicle'].search([('id', '=', int(line['truck_id']))], limit=1)
                trip_data = self.env['fleet.vehicle.trip'].search([('id', '=', int(line['trip_id']))], limit=1)
                if truck_data and trip_data and trip_data.start_branch and trip_data.start_branch != req_branch:
                    if len(trip_data.bsg_trip_arrival_ids) > 0 and trip_data.bsg_trip_arrival_ids[
                        -1].waypoint_to.id != req_branch.id:
                        truck_ids.append(int(line['truck_id']))
                        truck_data.trip_id = trip_data.id
                        if line['route_id'] > 0:
                            truck_data.route_id = int(line['route_id'])
                        truck_data.expected_end_date = line['expected_end_date']
                        truck_data.no_of_cars = str(len(trip_data.stock_picking_id))
                        date2 = datetime.now() + relativedelta(hours=5)
                        date1 = line['expected_end_date']
                        if date2 > date1:
                            truck_data.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(
                                self.date_diff_in_seconds(date2, date1))
                        else:
                            truck_data.time_diff = str('0')

            return {
                'type': 'ir.actions.act_window',
                'name': 'Trucks Comming',
                'res_model': 'fleet.vehicle',
                'domain': [('id', 'in', truck_ids)],
                'views': [[self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
            }

    @api.model
    def tot_trucks_final(self):
        branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', 'in',
                                                                   ['46', '31', '54', '91', '18', '24', '13', '10',
                                                                    '44', '3', '2', '33', '55',
                                                                    '39', '19', '28', '49', '17', '15', '52', '59',
                                                                    '16', '5', '14', '21', '20', '23', '12', '11', '22',
                                                                    '58', '9', '25', '32', '34', '41', '60', '92', '96',
                                                                    '93', '27', '26', '35', '103', '6', '47', '37',
                                                                    '62', '61', '4', '63', '56', '30', '38', '200'])])
        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', 'in', branch_id.ids)])

        table_name = "fleet_vehicle as fv"
        self.env.cr.execute(
            "select fv.id as id,fv.current_branch_id as current_branch_id FROM " + table_name + " join bsg_vehicle_type_table as vt on vt.id = fv.vehicle_type where vt.include_in_fleet_status is true and state_id=2 ")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})
        last_month = str(datetime.now() - relativedelta(months=1))
        table_name = "fleet_vehicle_trip"
        self.env.cr.execute(
            "select id,state,vehicle_id,route_id,expected_end_date FROM " + table_name + " where create_date >= '%s' " % last_month)
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(
            columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet', 3: 'route_id', 4: 'expected_end_date'})

        table_name = "fleet_vehicle_trip_waypoints"
        self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
        waypoints_result = self._cr.fetchall()
        waypoints_frame = pd.DataFrame(list(waypoints_result))
        waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

        waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

        if not (result and trip_result and waypoints_result):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Trucks Final Stop',
                'res_model': 'fleet.vehicle',
                'domain': [('id', 'in', [])],
                'views': [[self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
            }

        waypoints_frame_last = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="last")

        trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isin(['progress', 'on_transit', 'confirmed']))]

        trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                    right_on='truck_id')

        trip_frame_final_last = pd.merge(trip_frame_final, waypoints_frame_last, how='left', left_on='trip_id',
                                         right_on='way_trip_id')

        trip_frame_final_last = trip_frame_final_last.loc[(trip_frame_final_last['waypoint'].isin(req_branch.ids))]

        trip_frame_final_last = trip_frame_final_last.drop_duplicates(subset='truck_id', keep="first")

        trip_frame_final_last = trip_frame_final_last[trip_frame_final_last.truck_id.notnull()]

        truck_ids = []
        for index, line in trip_frame_final_last.iterrows():
            truck_ids.append(int(line['truck_id']))
            truck_data = self.env['fleet.vehicle'].search([('id', '=', int(line['truck_id']))], limit=1)
            trip_data = self.env['fleet.vehicle.trip'].search([('id', '=', int(line['trip_id']))], limit=1)
            truck_data.trip_id = int(line['trip_id'])
            if line['route_id'] > 0:
                truck_data.route_id = int(line['route_id'])
            truck_data.expected_end_date = line['expected_end_date']
            truck_data.no_of_cars = str(len(trip_data.stock_picking_id))
            date2 = datetime.now() + relativedelta(hours=5)
            date1 = line['expected_end_date']
            if date2 > date1:
                truck_data.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(
                    self.date_diff_in_seconds(date2, date1))
            else:
                truck_data.time_diff = str('0')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trucks Final Stop',
            'res_model': 'fleet.vehicle',
            'views': [[self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
            'domain': [('id', 'in', truck_ids)],
        }

    @api.model
    def tot_shipping_cars(self):
        branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', 'in',
                                                                   ['46', '31', '54', '91', '18', '24', '13', '10',
                                                                    '44', '3', '2', '33', '55',
                                                                    '39', '19', '28', '49', '17', '15', '52', '59',
                                                                    '16', '5', '14', '21', '20', '23', '12', '11', '22',
                                                                    '58', '9', '25', '32', '34', '41', '60', '92', '96',
                                                                    '93', '27', '26', '35', '103', '6', '47', '37',
                                                                    '62', '61', '4', '63', '56', '30', '38', '200'])])
        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', 'in', branch_id.ids)])
        last_month = datetime.now() - relativedelta(months=1)
        ship_ids = self.env['bsg_vehicle_cargo_sale_line'].search(
            [('is_package', '=', False), ('create_date', '>=', last_month), ('cargo_sale_state', 'in', ['done', 'pod']),
             ('state', 'in', ['draft', 'on_transit']), '|', ('loc_from.id', 'in', req_branch.ids),
             ('pickup_loc.id', 'in', req_branch.ids)], order="order_date asc")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cars To Ship',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [('id', 'in', ship_ids.ids)],
        }

    @api.model
    def tot_trucks_avail(self):
        branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', 'in',
                                                                   ['46', '31', '54', '91', '18', '24', '13', '10',
                                                                    '44', '3', '2', '33', '55',
                                                                    '39', '19', '28', '49', '17', '15', '52', '59',
                                                                    '16', '5', '14', '21', '20', '23', '12', '11', '22',
                                                                    '58', '9', '25', '32', '34', '41', '60', '92', '96',
                                                                    '93', '27', '26', '35', '103', '6', '47', '37',
                                                                    '62', '61', '4', '63', '56', '30', '38', '200'])])
        truck_ids = self.env['fleet.vehicle'].search(
            [('vehicle_type.include_in_fleet_status', '=', True), ('current_branch_id', 'in', branch_id.ids),
             ('state_id', '=', 2)])
        for tr in truck_ids:
            last_month = datetime.now() - relativedelta(months=1)

            trips = self.env['fleet.vehicle.trip'].search(
                [('create_date', '>=', last_month), ('state', 'not in', ['finished', 'cancelled']),
                 ('vehicle_id.id', '=', tr.id)], order="expected_end_date asc", limit=1)
            if trips:
                tr.trip_id = trips.id
                tr.route_id = trips.route_id.id
                tr.expected_end_date = trips.expected_end_date
                tr.no_of_cars = str(len(trips.stock_picking_id))
                date2 = datetime.now() + relativedelta(hours=5)
                date1 = trips.expected_end_date
                if date2 > date1:
                    tr.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(
                        self.date_diff_in_seconds(date2, date1))
                else:
                    tr.time_diff = str('0')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Trucks Available',
            'res_model': 'fleet.vehicle',
            'domain': [('id', 'in', truck_ids.ids)],
            'views': [[self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
        }

    @api.model
    def tot_trucks_coming(self):
        branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', 'in',
                                                                   ['46', '31', '54', '91', '18', '24', '13', '10',
                                                                    '44', '3', '2', '33', '55', '39', '19', '28', '49',
                                                                    '17', '15', '52', '59', '16', '5', '14', '21', '20',
                                                                    '23', '12', '11', '22', '58', '9', '25', '32', '34',
                                                                    '41', '60', '92', '96', '93', '27', '26', '35',
                                                                    '103', '6', '47', '37', '62', '61', '4', '63', '56',
                                                                    '30', '38', '200'])])
        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', 'in', branch_id.ids)])

        table_name = "fleet_vehicle as fv"
        self.env.cr.execute(
            "select fv.id as id,fv.current_branch_id as current_branch_id FROM " + table_name + " join bsg_vehicle_type_table as vt on vt.id = fv.vehicle_type where vt.include_in_fleet_status is true and state_id=2 ")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})
        last_month = str(datetime.now() - relativedelta(months=1))
        table_name = "fleet_vehicle_trip"
        self.env.cr.execute(
            "select id,state,vehicle_id,route_id,expected_end_date, start_branch FROM " + table_name + " where create_date >= '%s' and state != 'finished' " % last_month)
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(
            columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet', 3: 'route_id', 4: 'expected_end_date',
                     5: 'start_branch'})

        # table_name = "fleet_trip_arrival"
        # self.env.cr.execute("select id,waypoint_to,trip_id,is_done_survey FROM "+table_name+" ")
        # waypoints_result = self._cr.fetchall()
        # waypoints_frame = pd.DataFrame(list(waypoints_result))
        # waypoints_frame = waypoints_frame.rename(columns={0: 'way_id',1: 'waypoint',2: 'way_trip_id',3: 'is_done_survey'})

        table_name = "fleet_vehicle_trip_waypoints"
        self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
        waypoints_result = self._cr.fetchall()
        waypoints_frame = pd.DataFrame(list(waypoints_result))

        waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

        waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

        if not (result and trip_result and waypoints_result):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Trucks Comming',
                'res_model': 'fleet.vehicle',
                'domain': [('id', 'in', [])],
                'views': [
                    [self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'list']]
            }
        waypoints_frame_coming = waypoints_frame.loc[(waypoints_frame['waypoint'].isin(req_branch.ids))]
        waypoints_frame_coming = waypoints_frame_coming[waypoints_frame_coming.way_trip_id.notnull()]

        waypoints_frame_coming = waypoints_frame_coming.drop_duplicates(subset='way_trip_id', keep="last")

        trip_frame_final = trip_frame.loc[
            (trip_frame['start_branch'].isin(req_branch.ids)) & (trip_frame['trip_state'] != 'draft') & (
                    trip_frame['trip_state'] != 'finished') & (trip_frame['trip_state'] != 'cancelled')]

        trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                    right_on='truck_id')

        trip_frame_final_coming = pd.merge(trip_frame_final, waypoints_frame_coming, how='left', left_on='trip_id',
                                           right_on='way_trip_id')

        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.way_trip_id.notnull()]
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.trip_id.notnull()]
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.truck_id.notnull()]

        trip_frame_final_coming = trip_frame_final_coming.drop_duplicates(subset='truck_id', keep="first")

        # trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.truck_id.notnull()]

        truck_ids = []
        for index, line in trip_frame_final_coming.iterrows():
            truck_data = self.env['fleet.vehicle'].search([('id', '=', int(line['truck_id']))], limit=1)
            trip_data = self.env['fleet.vehicle.trip'].search([('id', '=', int(line['trip_id']))], limit=1)
            if truck_data and trip_data and trip_data.start_branch:
                truck_ids.append(int(line['truck_id']))
                truck_data.trip_id = trip_data.id
                if line['route_id'] > 0:
                    truck_data.route_id = int(line['route_id'])
                truck_data.expected_end_date = line['expected_end_date']
                truck_data.no_of_cars = str(len(trip_data.stock_picking_id))
                date2 = datetime.now() + relativedelta(hours=5)
                date1 = line['expected_end_date']
                if date2 > date1:
                    truck_data.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(
                        self.date_diff_in_seconds(date2, date1))
                else:
                    truck_data.time_diff = str('0')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Trucks Comming',
            'res_model': 'fleet.vehicle',
            'domain': [('id', 'in', truck_ids)],
            'views': [[self.env.ref('sales_dashboard.fleet_vehicle_trip_tree_list_inherit_truck_in').id, 'list']],
        }

    @api.model
    def tot_arrived_cars(self):
        branch_id = self.env['bsg_branches.bsg_branches'].search([('branch_no', 'in',
                                                                   ['46', '31', '54', '91', '18', '24', '13', '10',
                                                                    '44', '3', '2', '33', '55',
                                                                    '39', '19', '28', '49', '17', '15', '52', '59',
                                                                    '16', '5', '14', '21', '20', '23', '12', '11', '22',
                                                                    '58', '9', '25', '32', '34', '41', '60', '92', '96',
                                                                    '93', '27', '26', '35', '103', '6', '47', '37',
                                                                    '62', '61', '4', '63', '56', '30', '38', '200'])])
        last_month = datetime.now() - relativedelta(months=1)
        ship_ids = self.env['bsg_vehicle_cargo_sale_line'].search(
            [('is_package', '=', False), ('create_date', '>=', last_month),
             ('loc_to.loc_branch_id.id', 'in', branch_id.ids),
             ('state', 'in', ['Delivered'])], order="order_date asc")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Arrived Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [('id', 'in', ship_ids.ids)],
        }

    @api.model
    def tot_maintenance_cars(self):
        maintenance_ids = self.env['maintenance.request.enhance'].search([('vehicle_id', '!=', False),('state', 'not in', ['4','5'])])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Work Order',
            'res_model': 'maintenance.request.enhance',
            'context': {'create': False, 'edit': False, 'delete': False},
            'views': [[self.env.ref('maintenance_enhance.maintenance_req_enh_tree_view').id, 'list'],[self.env.ref('maintenance_enhance.maintenance_req_enh_form_view').id, 'form']],
            'domain': [('id', 'in', maintenance_ids.ids)],
        }
