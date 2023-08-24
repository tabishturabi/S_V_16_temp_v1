# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.http import request
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta


class BsgVehicleType(models.Model):
    _inherit = 'bsg.vehicle.type.table'

    include_in_fleet_status = fields.Boolean()


class FleetStatusModel(models.Model):
    _name = 'fleet.status.model'
    _inherit = ['mail.thread']
    _description = "Fleet Status"

    name = fields.Char(string='Name', default="Fleet Status")
    fleet_line_ids = fields.One2many(
        'fleet.status.line',
        'fleet_status_id',
        string='Branches',
    )


class FleetStatusLine(models.Model):
    _name = 'fleet.status.line'
    _inherit = ['mail.thread']
    _description = "Fleet Status Line"
    _order = "branch_no desc"

    fleet_status_id = fields.Many2one(
        'fleet.status.model',
        string='Fleet Status ID',
    )
    branch_id = fields.Many2one(
        'bsg_branches.bsg_branches',
        string='Branch',
    )
    branch_no = fields.Char(related="branch_id.branch_no", string='Branch #')
    trucks_available = fields.Integer(related="branch_id.trucks_available", string='Trucks Available')
    trucks_comming = fields.Integer(related="branch_id.trucks_comming", string='Trucks Comming')
    trucks_final_stop = fields.Integer(related="branch_id.trucks_final_stop", string='Trucks Final Stop')
    shiping_cars = fields.Integer(related='branch_id.shiping_cars', string='Cars to Ship')
    arrived_cars = fields.Integer(related='branch_id.arrived_cars', string='Arrived Cars')


    def trucks_data(self):
        truck_ids = self.env['fleet.vehicle'].search(
            [('vehicle_type.include_in_fleet_status', '=', True), ('current_branch_id', '=', self.branch_id.id),
             ('state_id', '=', 2)])
        for tr in truck_ids:
            last_month = datetime.now() - relativedelta(months=1)

            trips = tr.trip_id
            if trips:
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
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', truck_ids.ids)],
            'views': [(self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_in').id, 'tree')],
        }


    def trucks_coming_data(self):
        # trips = self.env['fleet.vehicle.trip'].search([('state','in',['progress','on_transit'])])
        # truck_ids = []
        # for tr in trips:
        # 	for line in tr.bsg_trip_arrival_ids:
        # 		if(self.branch_id.id ==line.waypoint_to.loc_branch_id.id):
        # 			if line.is_done_survey:
        # 				if tr.vehicle_id.id in truck_ids:
        # 					truck_ids.remove(tr.vehicle_id.id)
        # 				# truck_count -= 1
        # 			else:
        # 				if tr.vehicle_id:
        # 					if tr.vehicle_id.id not in truck_ids:
        # 						tr.vehicle_id.trip_id = tr.id
        # 						tr.vehicle_id.route_id = tr.route_id.id
        # 						tr.vehicle_id.expected_end_date = tr.expected_end_date
        # 						tr.vehicle_id.no_of_cars = str(len(tr.stock_picking_id))
        # 						date2 = datetime.now() + relativedelta(hours=5)
        # 						date1 = tr.expected_end_date
        # 						if date2 > date1:
        # 							tr.vehicle_id.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(self.date_diff_in_seconds(date2, date1))
        # 						else:
        # 							tr.vehicle_id.time_diff = str('0')

        # 						truck_ids.append(tr.vehicle_id.id)

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.branch_id.id)], limit=1)

        table_name = "fleet_vehicle as fv"
        self.env.cr.execute(
            "select fv.id as id,fv.current_branch_id as current_branch_id FROM " + table_name + " join bsg_vehicle_type_table as vt on vt.id = fv.vehicle_type where vt.include_in_fleet_status is true and state_id=2 ")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})
        last_month = str(datetime.now() - relativedelta(months=1))
        table_name = "fleet_vehicle_trip"
        self.env.cr.execute(
            "select id,state,vehicle_id,route_id,expected_end_date, start_branch FROM " + table_name + " where create_date >= '%s' " % last_month)
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
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', [])],
                'views': [
                    (self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
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
                if len(trip_data.bsg_trip_arrival_ids) > 0 and trip_data.bsg_trip_arrival_ids[-1].waypoint_to.id != req_branch.id:
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
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', truck_ids)],
            'views': [(self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
        }


    def trucks_final_stop_data(self):
        # trips = self.env['fleet.vehicle.trip'].search([('state','in',['progress','on_transit'])])
        # truck_ids = []
        # for tr in trips:
        # 	waypoints = self.env['fleet.vehicle.trip.waypoints'].search([('bsg_fleet_trip_id.id','=',tr.id)])
        # 	if waypoints:
        # 		last_branch = waypoints[-1]
        # 		if last_branch.waypoint.loc_branch_id.id == self.branch_id.id:
        # 			if tr.vehicle_id:
        # 				tr.vehicle_id.trip_id = tr.id
        # 				tr.vehicle_id.route_id = tr.route_id.id
        # 				tr.vehicle_id.expected_end_date = tr.expected_end_date
        # 				tr.vehicle_id.no_of_cars = str(len(tr.stock_picking_id))
        # 				date2 = datetime.now() + relativedelta(hours=5)
        # 				date1 = tr.expected_end_date
        # 				if date2 > date1:
        # 					tr.vehicle_id.time_diff = "\n%d days, %d hours, %d minutes" % self.dhms_from_seconds(self.date_diff_in_seconds(date2, date1))
        # 				else:
        # 					tr.vehicle_id.time_diff = str('0')
        # 				truck_ids.append(tr.vehicle_id.id)

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.branch_id.id)], limit=1)

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
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', [])],
                'views': [
                    (self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
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
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', truck_ids)],
            'views': [(self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
        }

    def date_diff_in_seconds(self, dt2, dt1):
        timedelta = dt2 - dt1
        return timedelta.days * 24 * 3600 + timedelta.seconds

    def dhms_from_seconds(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return (days, hours, minutes)


    def shiping_cars_data(self):
        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.branch_id.id)], limit=1)
        last_month = datetime.now() - relativedelta(months=1)
        ship_ids = self.env['bsg_vehicle_cargo_sale_line'].search(
            [('is_package', '=',False),('create_date', '>=', last_month), ('cargo_sale_state', 'in', ['done', 'pod']),
             ('state', 'in', ['confirm', 'on_transit']), '|', ('loc_from.id', '=', req_branch.id),
             ('pickup_loc.id', '=', req_branch.id)], order="order_date desc")

        # ship_ids = []
        # car_count_1 = self.env['bsg_vehicle_cargo_sale_line'].search([('loc_from_branch_id','=',self.branch_id.id),('cargo_sale_state','in',['done','pod']),('state','in',['draft']),('added_to_trip','=',False),('fleet_trip_id','=',False)])
        # for x in car_count_1:
        # 	ship_ids.append(x.id)
        # car_count_2 = self.env['bsg_vehicle_cargo_sale_line'].search([('loc_to.loc_branch_id.id','=',self.branch_id.id),('cargo_sale_state','in',['done','pod']),('state','in',['on_transit']),('added_to_trip','=',False),('fleet_trip_id','=',False)])
        # for y in car_count_2:
        # 	ship_ids.append(y.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cars To Ship',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ship_ids.ids)],
        }


    def arrived_cars_data(self):
        last_month = datetime.now() - relativedelta(months=1)
        ship_ids = self.env['bsg_vehicle_cargo_sale_line'].search(
            [('is_package', '=',False),('create_date', '>=', last_month), ('loc_to.loc_branch_id.id', '=', self.branch_id.id),
             ('state', 'in', ['Delivered'])], order="order_date desc")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Arrived Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ship_ids.ids)],
        }


class BsgBranches(models.Model):
    _inherit = 'bsg_branches.bsg_branches'

    trucks_available = fields.Integer(string='Trucks Available')
    trucks_comming = fields.Integer(string='Trucks Comming', )
    trucks_final_stop = fields.Integer(string='Trucks Final Stop', )
    shiping_cars = fields.Integer(string='Cars to Ship', )
    arrived_cars = fields.Integer(string='Arrived Cars', )

    @api.model
    def get_branches(self):
        print('................')
        # commented due to odoo.sh mail
        fleet_model = self.env['fleet.status.model'].search([], limit=1)
        fleet_model.fleet_line_ids = False
        branch_ids = self.env['bsg_route_waypoints'].search(
            [('loc_branch_id', '!=', False), ('location_type', '=', 'albassami_loc'),
             ('is_close_location', '!=', True)]).mapped('loc_branch_id')
        for br in branch_ids:
            if br.branch_name and br.branch_no and br.branch_type:
                fleet_model.fleet_line_ids |= \
                    fleet_model.fleet_line_ids.new({'branch_id': br.id})
                br.trucks_comming = self._get_trucks_comming(br)
                br.trucks_final_stop = self._get_trucks_final_stop(br)
                self.get_car_details(br)

    def _get_trucks_comming(self, branch_id):

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
            "select id,state,vehicle_id, start_branch  FROM " + table_name + " where create_date >= '%s' and state != 'finished' " % last_month)
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet', 3: 'start_branch'})

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

        waypoints_frame_coming = waypoints_frame.loc[(waypoints_frame['waypoint'] == req_branch.id)]

        waypoints_frame_coming = waypoints_frame_coming.drop_duplicates(subset='way_trip_id', keep="last")
        # trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isnotin(['draft','finished','cancelled']))]
        if not (result and trip_result and waypoints_result):
            return 0
        trip_frame_final = trip_frame.loc[
            (trip_frame['start_branch'] != False) & (trip_frame['start_branch'] != req_branch.id) & (
                        trip_frame['trip_state'] != 'draft') & (trip_frame['trip_state'] != 'finished') & (
                        trip_frame['trip_state'] != 'cancelled')]

        trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                    right_on='truck_id')

        trip_frame_final_coming = pd.merge(trip_frame_final, waypoints_frame_coming, how='left', left_on='trip_id',
                                           right_on='way_trip_id')

        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.way_trip_id.notnull()]

        trip_frame_final_coming = trip_frame_final_coming.drop_duplicates(subset='truck_id', keep="first")
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.truck_id.notnull()]
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.trip_id.notnull()]
        truck_ids = []
        for index, line in trip_frame_final_coming.iterrows():
            truck_data = self.env['fleet.vehicle'].search([('id', '=', int(line['truck_id']))], limit=1)
            trip_data = self.env['fleet.vehicle.trip'].search([('id', '=', int(line['trip_id']))], limit=1)
            if truck_data and trip_data and trip_data.start_branch and trip_data.start_branch != req_branch:
                if len(trip_data.bsg_trip_arrival_ids) > 0 and trip_data.bsg_trip_arrival_ids[-1].waypoint_to.id != req_branch.id:
                    truck_ids.append(int(line['truck_id']))

        return int(len(truck_ids))

    # trips = self.env['fleet.vehicle.trip'].search([('state','in',['progress','on_transit'])])
    # truck_count_ids = []
    # for tr in trips:
    # 	for line in tr.bsg_trip_arrival_ids:
    # 		if(branch_id.id ==line.waypoint_to.loc_branch_id.id):
    # 			if line.is_done_survey:
    # 				if tr.vehicle_id.id in truck_count_ids:
    # 					truck_count_ids.remove(tr.vehicle_id.id)
    # 			else:
    # 				if tr.vehicle_id:
    # 					if tr.vehicle_id.id not in truck_count_ids:
    # 						truck_count_ids.append(tr.vehicle_id.id)

    # print (branch_id)
    # print (len(truck_count_ids))
    # print ("99999999999999999999999999")

    # return len(truck_count_ids)

    def _get_trucks_final_stop(self, branch_id):

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
            "select id,state,vehicle_id FROM " + table_name + " where create_date >= '%s' " % last_month)
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet'})

        table_name = "fleet_vehicle_trip_waypoints"
        self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
        waypoints_result = self._cr.fetchall()
        waypoints_frame = pd.DataFrame(list(waypoints_result))
        waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

        waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

        if not (result and trip_result and waypoints_result): return 0

        waypoints_frame_last = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="last")

        trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isin(['progress', 'on_transit', 'confirmed']))]

        trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                    right_on='truck_id')

        trip_frame_final_last = pd.merge(trip_frame_final, waypoints_frame_last, how='left', left_on='trip_id',
                                         right_on='way_trip_id')

        trip_frame_final_last = trip_frame_final_last.loc[(trip_frame_final_last['waypoint'] == req_branch.id)]

        trip_frame_final_last = trip_frame_final_last.drop_duplicates(subset='truck_id', keep="first")

        trip_frame_final_last = trip_frame_final_last[trip_frame_final_last.truck_id.notnull()]

        return int(len(trip_frame_final_last))

    # trips = self.env['fleet.vehicle.trip'].search([('state','in',['progress','on_transit'])])
    # truck_final_ids = []
    # for tr in trips:
    # 	waypoints = self.env['fleet.vehicle.trip.waypoints'].search([('bsg_fleet_trip_id.id','=',tr.id)])
    # 	if waypoints:
    # 		last_branch = waypoints[-1]
    # 		if last_branch.waypoint.loc_branch_id.id == branch_id.id:
    # 			if tr.vehicle_id:
    # 				truck_final_ids.append(tr.vehicle_id.id)

    def get_car_details(self, branch):
        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', branch.id)], limit=1)
        last_month = datetime.now() - relativedelta(months=1)
        branch.shiping_cars = self.env['bsg_vehicle_cargo_sale_line'].search_count(
            [('is_package', '=',False),('create_date', '>=', last_month), ('cargo_sale_state', 'in', ['done', 'pod']),
             ('state', 'in', ['draft', 'on_transit']), '|', ('loc_from.id', '=', req_branch.id),
             ('pickup_loc.id', '=', req_branch.id)])

        # car_count_2 = self.env['bsg_vehicle_cargo_sale_line'].search_count([('loc_to.loc_branch_id.id','=',branch.id),('cargo_sale_state','in',['done','pod']),('state','in',['on_transit']),('added_to_trip','=',False),('fleet_trip_id','=',False)])
        # branch.shiping_cars = int(car_count_1) + int(car_count_2)

        branch.arrived_cars = self.env['bsg_vehicle_cargo_sale_line'].search_count(
            [('create_date', '>=', last_month), ('loc_to.loc_branch_id.id', '=', branch.id),
             ('state', 'in', ['Delivered'])])

        branch.trucks_available = self.env['fleet.vehicle'].search_count([('vehicle_type.include_in_fleet_status', '=', True),
            ('state_id', '=', 2), ('current_branch_id', '=', branch.id)])
