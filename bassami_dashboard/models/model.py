# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
from odoo import api, fields, models
from odoo.http import request
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError



class BassamiBranchDashboard(models.Model):
    _name = 'bassami.dash'

    name = fields.Char(required=True)
    time_filter = fields.Selection(string="Time Filter", default="curr_week", selection=[
        ('curr_week', 'Current Week'),
        ('last_week', 'Last Week'),
        ('curr_month', 'Current Month'),
        ('last_month', 'Last Month'),
        ('curr_year', 'Current Year'),
        ('last_year', 'Last Year'),
    ], required=True)
    # branches = fields.Many2one('bsg_branches.bsg_branches', string="Branches")
    branches = fields.Many2one(string="Branches", comodel_name="bsg_branches.bsg_branches", readonly=True)

    from_total_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_nonshipped_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_shipped_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_ontransit_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_delivered_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_released_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_cash_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_credit_cars_num = fields.Integer(compute='get_shipped_vehicles')
    from_pod_cars_num = fields.Integer(compute='get_shipped_vehicles')

    to_total_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_nonshipped_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_shipped_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_ontransit_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_delivered_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_released_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_cash_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_credit_cars_num = fields.Integer(compute='get_shipped_vehicles_to')
    to_pod_cars_num = fields.Integer(compute='get_shipped_vehicles_to')

    trucks_available = fields.Integer(compute='get_trucks_data')
    trucks_last_stop = fields.Integer(compute='get_trucks_data')
    trucks_first_stop = fields.Integer(compute='get_trucks_data')
    trucks_coming = fields.Integer(compute='get_trucks_data')

    @api.onchange('time_filter', 'branches')
    def get_all_data(self):
        self.get_shipped_vehicles()
        self.get_shipped_vehicles_to()
        self.get_trucks_data()

    # @api.one
    def get_shipped_vehicles(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])
        # self.branches.id = get_shipped_vehicles

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        total_cars_frame_from = 0
        nonshipped_cars_frame_from = 0
        shipped_cars_frame_from = 0
        on_transit_cars_frame_from = 0
        delivered_cars_frame_from = 0
        released_cars_frame_from = 0
        cash_cars_frame_from = 0
        credit_cars_frame_from = 0
        pod_cars_frame_from = 0
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]
        if len(bsg_cargo_lines) > 0:
            bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
            bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
            bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
            payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
            payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
            payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids

            if self.time_filter == 'curr_week':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id))]
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_week':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id))]
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_month':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['on_transit']))]
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_month':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['on_transit']))]
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_year':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['on_transit']))]
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_year':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['on_transit']))]
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]
            self.from_total_cars_num = int(len(total_cars_frame_from))
            self.from_nonshipped_cars_num = int(len(nonshipped_cars_frame_from))
            self.from_shipped_cars_num = int(len(shipped_cars_frame_from))
            self.from_ontransit_cars_num = int(len(on_transit_cars_frame_from))
            self.from_delivered_cars_num = int(len(delivered_cars_frame_from))
            self.from_released_cars_num = int(len(released_cars_frame_from))
            self.from_cash_cars_num = int(len(cash_cars_frame_from))
            self.from_credit_cars_num = int(len(credit_cars_frame_from))
            self.from_pod_cars_num = int(len(pod_cars_frame_from))
        else:
            self.from_total_cars_num = total_cars_frame_from
            self.from_nonshipped_cars_num = nonshipped_cars_frame_from
            self.from_shipped_cars_num = shipped_cars_frame_from
            self.from_ontransit_cars_num = on_transit_cars_frame_from
            self.from_delivered_cars_num = delivered_cars_frame_from
            self.from_released_cars_num = released_cars_frame_from
            self.from_cash_cars_num = cash_cars_frame_from
            self.from_credit_cars_num = credit_cars_frame_from
            self.from_pod_cars_num = pod_cars_frame_from

    # @api.one
    def get_shipped_vehicles_to(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one,charges_stored, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'charges_stored', 23: 'drop_loc',
                     24: 'create_date'})
        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]
        if len(bsg_cargo_lines) > 0:
            bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
            bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
            bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
            payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
            payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
            payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids

            if self.time_filter == 'curr_week':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id))]
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]
                delivered_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_week':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id))]
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]
                delivered_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_month':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                delivered_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_month':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                delivered_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_year':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                delivered_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_year':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]
                delivered_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_cash)]
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_credit)]
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines[
                        'payment_method'].isin(
                        payment_method_pod)]

            self.to_total_cars_num = int(len(total_cars_frame_to))
            self.to_nonshipped_cars_num = int(len(nonshipped_cars_frame_to))
            self.to_shipped_cars_num = int(len(shipped_cars_frame_to))
            self.to_ontransit_cars_num = int(len(on_transit_cars_frame_to))
            self.to_delivered_cars_num = int(len(delivered_cars_frame_to))
            self.to_released_cars_num = int(len(released_cars_frame_to))
            self.to_cash_cars_num = int(len(cash_cars_frame_to))
            self.to_credit_cars_num = int(len(credit_cars_frame_to))
            self.to_pod_cars_num = int(len(pod_cars_frame_to))
        else:
            self.to_total_cars_num = 0
            self.to_nonshipped_cars_num = 0
            self.to_shipped_cars_num = 0
            self.to_ontransit_cars_num = 0
            self.to_delivered_cars_num = 0
            self.to_released_cars_num = 0
            self.to_cash_cars_num = 0
            self.to_credit_cars_num = 0
            self.to_pod_cars_num = 0

    # @api.one
    def get_trucks_data(self):

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)

        table_name = "fleet_vehicle"
        self.env.cr.execute("select id,current_branch_id FROM " + table_name + " where vehicle_type in (22, 28)")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})

        print('.............trucks_frame...........',trucks_frame)

        table_name = "fleet_vehicle_trip"
        self.env.cr.execute("select id,state,vehicle_id FROM " + table_name + " ")
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet'})

        table_name = "fleet_vehicle_trip_waypoints"
        self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
        waypoints_result = self._cr.fetchall()
        waypoints_frame = pd.DataFrame(list(waypoints_result))
        waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

        waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

        waypoints_frame_coming = waypoints_frame.loc[(waypoints_frame['waypoint'] == req_branch.id)]

        waypoints_frame_coming = waypoints_frame_coming.drop_duplicates(subset='way_trip_id', keep="last")

        waypoints_frame_last = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="last")
        waypoints_frame_first = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="first")

        trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isin(['progress', 'on_transit']))]

        if trucks_frame.empty:
            raise UserError('Empty data frame can not be merged because no truck information found against given vehicle types')

        trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                    right_on='truck_id')

        trip_frame_final_last = pd.merge(trip_frame_final, waypoints_frame_last, how='left', left_on='trip_id',
                                         right_on='way_trip_id')

        trip_frame_final_last = trip_frame_final_last.loc[(trip_frame_final_last['waypoint'] == req_branch.id)]

        trip_frame_final_last = trip_frame_final_last.drop_duplicates(subset='truck_id', keep="first")

        trip_frame_final_last = trip_frame_final_last[trip_frame_final_last.truck_id.notnull()]

        trip_frame_final_first = pd.merge(trip_frame_final, waypoints_frame_first, how='left', left_on='trip_id',
                                          right_on='way_trip_id')

        trip_frame_final_first = trip_frame_final_first.loc[(trip_frame_final_first['waypoint'] == req_branch.id)]

        trip_frame_final_first = trip_frame_final_first.drop_duplicates(subset='truck_id', keep="first")

        trip_frame_final_first = trip_frame_final_first[trip_frame_final_first.truck_id.notnull()]

        trip_frame_final_coming = pd.merge(trip_frame_final, waypoints_frame_coming, how='left', left_on='trip_id',
                                           right_on='way_trip_id')
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.way_trip_id.notnull()]
        trip_frame_final_coming = trip_frame_final_coming.drop_duplicates(subset='truck_id', keep="first")
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.truck_id.notnull()]

        trucks_available = trucks_frame.loc[(trucks_frame['current_branch_id'] == self.env.user.user_branch_id.id)]

        self.trucks_available = int(len(trucks_available))
        self.trucks_last_stop = int(len(trip_frame_final_last))
        self.trucks_first_stop = int(len(trip_frame_final_first))
        self.trucks_coming = int(len(trip_frame_final_coming))

    # @api.multi
    def from_total_cars(self):

        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date  FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        total_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id))]

            if self.time_filter == 'last_week':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id))]

            if self.time_filter == 'curr_month':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]

            if self.time_filter == 'last_month':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]

            if self.time_filter == 'curr_year':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]

            if self.time_filter == 'last_year':
                total_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id))]

        bsg_sale_ids = []
        if len(total_cars_frame_from) > 0:
            for index, line in total_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Total Cars From',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_nonshipped_cars(self):

        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        nonshipped_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'last_week':
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'curr_month':
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'last_month':
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'curr_year':
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'last_year':
                nonshipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

        bsg_sale_ids = []
        if len(nonshipped_cars_frame_from) > 0:
            for index, line in nonshipped_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Non-Shipped Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_shipped_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        shipped_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_week':
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'curr_month':
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_month':
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'curr_year':
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_year':
                shipped_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

        bsg_sale_ids = []
        if len(shipped_cars_frame_from) > 0:
            for index, line in shipped_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Shipped Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_ontransit_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        on_transit_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]

            if self.time_filter == 'last_week':
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]

            if self.time_filter == 'curr_month':
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]

            if self.time_filter == 'last_month':
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]

            if self.time_filter == 'curr_year':
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]

            if self.time_filter == 'last_year':
                on_transit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['pickup_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['on_transit']))]

        bsg_sale_ids = []
        if len(on_transit_cars_frame_from) > 0:
            for index, line in on_transit_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'On-Transit Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_delivered_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        delivered_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

            if self.time_filter == 'last_week':
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

            if self.time_filter == 'curr_month':
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

            if self.time_filter == 'last_month':
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

            if self.time_filter == 'curr_year':
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

            if self.time_filter == 'last_year':
                delivered_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

        bsg_sale_ids = []
        if len(delivered_cars_frame_from) > 0:
            for index, line in delivered_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivered Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_released_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        released_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'last_week':
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'curr_month':
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'last_month':
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'curr_year':
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

            if self.time_filter == 'last_year':
                released_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]

        bsg_sale_ids = []
        if len(released_cars_frame_from) > 0:
            for index, line in released_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Released Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_cash_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        cash_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'last_week':
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'curr_month':
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'last_month':
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'curr_year':
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'last_year':
                cash_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

        bsg_sale_ids = []
        if len(cash_cars_frame_from) > 0:
            for index, line in cash_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cash Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_credit_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        credit_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'last_week':
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'curr_month':
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'last_month':
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'curr_year':
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'last_year':
                credit_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

        bsg_sale_ids = []
        if len(credit_cars_frame_from) > 0:
            for index, line in credit_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def from_pod_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        pod_cars_frame_from = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_week':
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_month':
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_month':
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_year':
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_year':
                pod_cars_frame_from = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_from'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

        bsg_sale_ids = []
        if len(pod_cars_frame_from) > 0:
            for index, line in pod_cars_frame_from.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'POD Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_total_cars(self):

        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one,charges_stored, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'charges_stored', 23: 'drop_loc',
                     24: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        total_cars_frame_to = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id))]

            if self.time_filter == 'last_week':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id))]

            if self.time_filter == 'curr_month':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]

            if self.time_filter == 'last_month':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]

            if self.time_filter == 'curr_year':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]

            if self.time_filter == 'last_year':
                total_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id))]

        bsg_sale_ids = []
        if len(total_cars_frame_to) > 0:
            for index, line in total_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Total Cars To',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_nonshipped_cars(self):

        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        nonshipped_cars_frame_to = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'last_week':
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'curr_month':
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'last_month':
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'curr_year':
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

            if self.time_filter == 'last_year':
                nonshipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['draft', 'confirm']))]

        bsg_sale_ids = []
        if len(nonshipped_cars_frame_to) > 0:
            for index, line in nonshipped_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Non-Shipped Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_shipped_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        shipped_cars_frame_to = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_week':
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'curr_month':
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_month':
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'curr_year':
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_year':
                shipped_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

        bsg_sale_ids = []
        if len(shipped_cars_frame_to) > 0:
            for index, line in shipped_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shipped Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_ontransit_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        on_transit_cars_frame_to = []
        if len(on_transit_cars_frame_to)> 0:
            if self.time_filter == 'curr_week':
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_week':
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & (
                        (bsg_cargo_lines['loc_to'] != req_branch.id)) & (bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'curr_month':
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & ((bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_month':
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & ((bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'curr_year':
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & ((bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

            if self.time_filter == 'last_year':
                on_transit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['drop_loc'] == req_branch.id)) & (
                        (bsg_cargo_lines['loc_from'] != req_branch.id)) & ((bsg_cargo_lines['loc_to'] != req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['shipped']))]

        bsg_sale_ids = []
        if len(on_transit_cars_frame_to) > 0:
            for index, line in on_transit_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'On-Transit Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_delivered_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)

        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + " ")
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
                bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids

        if self.time_filter == 'curr_week':
            delivered_cars_frame_to = bsg_cargo_lines.loc[
                (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                    (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                    bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

        if self.time_filter == 'last_week':
            delivered_cars_frame_to = bsg_cargo_lines.loc[
                (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                    (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                    bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

        if self.time_filter == 'curr_month':
            delivered_cars_frame_to = bsg_cargo_lines.loc[
                (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                    bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

        if self.time_filter == 'last_month':
            delivered_cars_frame_to = bsg_cargo_lines.loc[
                (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                    bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

        if self.time_filter == 'curr_year':
            delivered_cars_frame_to = bsg_cargo_lines.loc[
                (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                    bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

        if self.time_filter == 'last_year':
            delivered_cars_frame_to = bsg_cargo_lines.loc[
                (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                    bsg_cargo_lines['state'].isin(['Delivered', 'released', 'done']))]

        bsg_sale_ids = []
        for index, line in delivered_cars_frame_to.iterrows():
            bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivered Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_released_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)
        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        released_cars_frame_to = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'last_week':
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'curr_month':
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'last_month':
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]

            if self.time_filter == 'curr_year':
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released']))]

            if self.time_filter == 'last_year':
                released_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['done']))]

        bsg_sale_ids = []
        if len(released_cars_frame_to) > 0:
            for index, line in released_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Released Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_cash_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)
        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        cash_cars_frame_to = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'last_week':
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'curr_month':
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'last_month':
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'curr_year':
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

            if self.time_filter == 'last_year':
                cash_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_cash)]

        bsg_sale_ids = []
        if len(cash_cars_frame_to) > 0:
            for index, line in cash_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cash Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_credit_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)
        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        credit_cars_frame_to = []
        if len(bsg_cargo_lines) > 0:
            if self.time_filter == 'curr_week':
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'last_week':
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'curr_month':
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'last_month':
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'curr_year':
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

            if self.time_filter == 'last_year':
                credit_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_credit)]

        bsg_sale_ids = []
        if len(credit_cars_frame_to) > 0:
            for index, line in credit_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def to_pod_cars(self):
        today_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
        week_day = today_date.strftime("%A")
        start_week = today_date
        if week_day == "Monday":
            start_week = today_date
        elif week_day == "Tuesday":
            start_week = today_date - relativedelta(days=1)
        elif week_day == "Wednesday":
            start_week = today_date - relativedelta(days=2)
        elif week_day == "Thursday":
            start_week = today_date - relativedelta(days=3)
        elif week_day == "Friday":
            start_week = today_date - relativedelta(days=4)
        elif week_day == "Saturday":
            start_week = today_date - relativedelta(days=5)
        elif week_day == "Sunday":
            start_week = today_date - relativedelta(days=6)

        end_week = start_week + relativedelta(days=6)
        last_week = start_week - relativedelta(days=7)

        start_week = str(start_week)
        end_week = str(end_week)
        last_week = str(last_week)

        start_week = str(start_week[:10])
        end_week = str(end_week[:10])
        last_week = str(last_week[:10])

        last_month = today_date - relativedelta(months=1)
        last_year = today_date - relativedelta(years=1)
        today_date = str(today_date)
        last_month = str(last_month)
        last_year = str(last_year)
        curr_month = str(today_date[:7])
        last_month = str(last_month[:7])
        curr_year = str(today_date[:4])
        last_year = str(last_year[:4])

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)
        where_clause = ""
        if self.time_filter == 'curr_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                start_week, end_week)
        if self.time_filter == 'last_week':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and order_date between '%s' and '%s'" % (
                last_week, start_week)
        if self.time_filter == 'curr_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                curr_month)
        if self.time_filter == 'last_month':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('month', order_date) = '%s' " % (
                last_month)
        if self.time_filter == 'curr_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                curr_year)
        if self.time_filter == 'last_year':
            where_clause = " where state != 'cancel' and sale_line_rec_name NOT LIKE '%%P%%' and date_part('year', order_date) = '%s' " % (
                last_year)
        table_name = "bsg_vehicle_cargo_sale_line"
        self.env.cr.execute(
            "select id,order_date,loc_from_branch_id,loc_to,create_uid,bsg_cargo_sale_id,payment_method,customer_id,loc_to_branch_id,state,fleet_trip_id,loc_from,pickup_loc,car_model,year,car_color,sale_line_rec_name,expected_delivery,add_to_cc,plate_no,car_make,palte_one, drop_loc, create_date FROM " + table_name + where_clause)
        result = self._cr.fetchall()
        bsg_cargo_lines = pd.DataFrame(list(result))
        bsg_cargo_lines = bsg_cargo_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'loc_from_branch_id', 3: 'loc_to', 4: 'create_uid',
                     5: 'bsg_cargo_sale_id', 6: 'payment_method', 7: 'customer_id', 8: 'loc_to_branch_id', 9: 'state',
                     10: 'fleet_trip_id', 11: 'loc_from', 12: 'pickup_loc', 13: 'car_model', 14: 'year',
                     15: 'car_color', 16: 'sale_line_rec_name', 17: 'expected_delivery', 18: 'add_to_cc',
                     19: 'plate_no', 20: 'car_make', 21: 'palte_one', 22: 'drop_loc', 23: 'create_date'})

        # bsg_cargo_lines = bsg_cargo_lines.loc[(bsg_cargo_lines['state'] != 'cancel') & (
        #         bsg_cargo_lines['sale_line_rec_name'].str.startswith(('*', 'P')) != True)]

        bsg_cargo_lines['month_date'] = bsg_cargo_lines['create_date'].astype(str).str[:7]
        bsg_cargo_lines['curr_date'] = bsg_cargo_lines['create_date'].astype(str).str[:10]
        bsg_cargo_lines['year_date'] = bsg_cargo_lines['create_date'].astype(str).str[:4]
        payment_method_cash = self.env['cargo_payment_method'].search([('payment_type', '=', 'cash')]).ids
        payment_method_credit = self.env['cargo_payment_method'].search([('payment_type', '=', 'credit')]).ids
        payment_method_pod = self.env['cargo_payment_method'].search([('payment_type', '=', 'pod')]).ids
        pod_cars_frame_to = []
        if len(bsg_cargo_lines)>0:
            if self.time_filter == 'curr_week':
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= start_week) & (bsg_cargo_lines['curr_date'] <= end_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_week':
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['curr_date'] >= last_week) & (bsg_cargo_lines['curr_date'] < start_week) & (
                        (bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_month':
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == curr_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_month':
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['month_date'] == last_month) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'curr_year':
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == curr_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

            if self.time_filter == 'last_year':
                pod_cars_frame_to = bsg_cargo_lines.loc[
                    (bsg_cargo_lines['year_date'] == last_year) & ((bsg_cargo_lines['loc_to'] == req_branch.id)) & (
                        bsg_cargo_lines['state'].isin(['Delivered', 'released'])) & bsg_cargo_lines['payment_method'].isin(
                        payment_method_pod)]

        bsg_sale_ids = []
        if len(pod_cars_frame_to)>0:
            for index, line in pod_cars_frame_to.iterrows():
                bsg_sale_ids.append(int(line['self_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'POD Cars',
            'res_model': 'bsg_vehicle_cargo_sale_line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', bsg_sale_ids)],
            'views': [(self.env.ref('bsg_cargo_sale.view_bsg_vehicle_cargo_sale_line_tree').id, 'tree')],
        }

    # @api.multi
    def trucks_last_stop_detail(self):

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)

        table_name = "fleet_vehicle"
        self.env.cr.execute("select id,current_branch_id FROM " + table_name + " where vehicle_type in (22, 28)")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})

        table_name = "fleet_vehicle_trip"
        self.env.cr.execute("select id,state,vehicle_id FROM " + table_name + " ")
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet'})

        table_name = "fleet_vehicle_trip_waypoints"
        self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
        waypoints_result = self._cr.fetchall()
        waypoints_frame = pd.DataFrame(list(waypoints_result))
        waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

        waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

        waypoints_frame_coming = waypoints_frame.loc[(waypoints_frame['waypoint'] == req_branch.id)]

        waypoints_frame_coming = waypoints_frame_coming.drop_duplicates(subset='way_trip_id', keep="last")

        waypoints_frame_last = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="last")
        waypoints_frame_first = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="first")

        trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isin(['progress', 'on_transit']))]

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

        return {
            'type': 'ir.actions.act_window',
            'name': 'Trucks Final Stop',
            'res_model': 'fleet.vehicle',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', truck_ids)],
            'views': [(self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
        }

    # @api.multi
    def trucks_coming_details(self):

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)

        table_name = "fleet_vehicle"
        self.env.cr.execute("select id,current_branch_id FROM " + table_name + " where vehicle_type in (22, 28)")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})

        table_name = "fleet_vehicle_trip"
        self.env.cr.execute("select id,state,vehicle_id FROM " + table_name + " ")
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet'})

        table_name = "fleet_vehicle_trip_waypoints"
        self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
        waypoints_result = self._cr.fetchall()
        waypoints_frame = pd.DataFrame(list(waypoints_result))
        waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

        waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

        waypoints_frame_coming = waypoints_frame.loc[(waypoints_frame['waypoint'] == req_branch.id)]

        waypoints_frame_coming = waypoints_frame_coming.drop_duplicates(subset='way_trip_id', keep="last")

        waypoints_frame_last = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="last")
        waypoints_frame_first = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="first")

        trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isin(['progress', 'on_transit']))]

        trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                    right_on='truck_id')

        trip_frame_final_coming = pd.merge(trip_frame_final, waypoints_frame_coming, how='left', left_on='trip_id',
                                           right_on='way_trip_id')
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.way_trip_id.notnull()]
        trip_frame_final_coming = trip_frame_final_coming.drop_duplicates(subset='truck_id', keep="first")
        trip_frame_final_coming = trip_frame_final_coming[trip_frame_final_coming.truck_id.notnull()]

        truck_ids = []
        for index, line in trip_frame_final_coming.iterrows():
            truck_ids.append(int(line['truck_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Trucks Coming',
            'res_model': 'fleet.vehicle',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', truck_ids)],
            'views': [(self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
        }

    # @api.multi
    def trucks_first_stop_detail(self):

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)

        table_name = "fleet_vehicle"
        self.env.cr.execute("select id,current_branch_id FROM " + table_name + " where vehicle_type in (22, 28)")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})

        table_name = "fleet_vehicle_trip"
        self.env.cr.execute("select id,state,vehicle_id FROM " + table_name + " ")
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet'})

        table_name = "fleet_vehicle_trip_waypoints"
        self.env.cr.execute("select id,waypoint,bsg_fleet_trip_id FROM " + table_name + " ")
        waypoints_result = self._cr.fetchall()
        waypoints_frame = pd.DataFrame(list(waypoints_result))
        waypoints_frame = waypoints_frame.rename(columns={0: 'way_id', 1: 'waypoint', 2: 'way_trip_id'})

        waypoints_frame = waypoints_frame.sort_values(by=['way_trip_id', 'way_id'])

        waypoints_frame_coming = waypoints_frame.loc[(waypoints_frame['waypoint'] == req_branch.id)]

        waypoints_frame_coming = waypoints_frame_coming.drop_duplicates(subset='way_trip_id', keep="last")

        waypoints_frame_last = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="last")
        waypoints_frame_first = waypoints_frame.drop_duplicates(subset='way_trip_id', keep="first")

        trip_frame_final = trip_frame.loc[(trip_frame['trip_state'].isin(['progress', 'on_transit']))]

        trip_frame_final = pd.merge(trip_frame_final, trucks_frame, how='left', left_on='trip_fleet',
                                    right_on='truck_id')

        trip_frame_final_first = pd.merge(trip_frame_final, waypoints_frame_first, how='left', left_on='trip_id',
                                          right_on='way_trip_id')

        trip_frame_final_first = trip_frame_final_first.loc[(trip_frame_final_first['waypoint'] == req_branch.id)]

        trip_frame_final_first = trip_frame_final_first.drop_duplicates(subset='truck_id', keep="first")

        trip_frame_final_first = trip_frame_final_first[trip_frame_final_first.truck_id.notnull()]

        truck_ids = []
        for index, line in trip_frame_final_first.iterrows():
            truck_ids.append(int(line['truck_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Trucks Leaving',
            'res_model': 'fleet.vehicle',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', truck_ids)],
            'views': [(self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
        }

    # @api.multi
    def trucks_available_details(self):

        req_branch = self.env['bsg_route_waypoints'].search([('loc_branch_id', '=', self.env.user.user_branch_id.id)],
                                                            limit=1)

        table_name = "fleet_vehicle"
        self.env.cr.execute("select id,current_branch_id FROM " + table_name + " where vehicle_type in (22, 28)")
        result = self._cr.fetchall()
        trucks_frame = pd.DataFrame(list(result))
        trucks_frame = trucks_frame.rename(columns={0: 'truck_id', 1: 'current_branch_id'})

        table_name = "fleet_vehicle_trip"
        self.env.cr.execute("select id,state,vehicle_id FROM " + table_name + " ")
        trip_result = self._cr.fetchall()
        trip_frame = pd.DataFrame(list(trip_result))
        trip_frame = trip_frame.rename(columns={0: 'trip_id', 1: 'trip_state', 2: 'trip_fleet'})

        trucks_available = trucks_frame.loc[(trucks_frame['current_branch_id'] == self.env.user.user_branch_id.id)]

        truck_ids = []
        for index, line in trucks_available.iterrows():
            truck_ids.append(int(line['truck_id']))

        return {
            'type': 'ir.actions.act_window',
            'name': 'Trucks Available',
            'res_model': 'fleet.vehicle',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', truck_ids)],
            'views': [(self.env.ref('bsg_fleet_operations.fleet_vehicle_tree_list_inherit_truck_coming').id, 'tree')],
        }


class bsg_inherit_cargo_sale_line_dash(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'

    loc_to_branch_id = fields.Many2one(related="loc_to.loc_branch_id", store=True, track_visibility=True,
                                       String="Branch To")


class IrHttpDash(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        res = super(IrHttpDash, self).session_info()
        res['branch-id'] = user.user_branch_id.id if request.session.uid else None
        res['user_banch'] = {'current_branch': (user.user_branch_id.id, user.user_branch_id.branch_ar_name),
                             'allowed_branch': [(branch.id, branch.branch_ar_name) for branch in user.user_branch_ids]},

        branch_dash = self.env['bassami.dash'].search([], limit=1)
        branch_dash.branches = int(res['branch-id'])

        return res
