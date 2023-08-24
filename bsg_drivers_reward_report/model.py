# -*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

from odoo import api, models, fields
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning
from pytz import timezone, UTC
import pandas as pd


class BranchesLedgerReportSalesRevenue(models.AbstractModel):
    _name = 'report.bsg_drivers_reward_report.drivers_reward_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        print('................_get_report_values.............')
        model = self.env.context.get('active_model')
        record_wizard = self.env[model].browse(self.env.context.get('active_id'))
        data = data['form']

        form = record_wizard.form
        to = record_wizard.to
        driver_id = record_wizard.driver_id
        filters = record_wizard.filters
        report_type = record_wizard.report_type
        report_num = 0

        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        if form.hour != 0:
            form = UTC.localize(form).astimezone(tz).replace(tzinfo=None)
        if to.hour != 0:
            to = UTC.localize(to).astimezone(tz).replace(tzinfo=None)
        print_date = UTC.localize(datetime.now()).astimezone(tz).replace(tzinfo=None)

        driver_data = []
        if filters == 'all':
            driver_table_name = "hr_employee as driver"
            self.env.cr.execute(
                "select driver.id as driver_id,driver.name as driver_name,driver.driver_code as driver_code FROM " + driver_table_name + \
                " WHERE driver.is_driver = True")
            driver_result = self._cr.fetchall()
            driver_data = driver_result
        else:
            driver_table_name = "hr_employee as driver"
            drivers = driver_id.ids
            print('.................else drivers..............',drivers)
            drivers_cond = ""
            if drivers:
                drivers_str = len(drivers) == 1 and "(%s)" % drivers[0] or str(
                    tuple(drivers))
                drivers_cond = f"and driver.id in {drivers_str}"
            self.env.cr.execute(
                "select driver.id as driver_id,driver.name as driver_name,driver.driver_code as driver_code FROM " + driver_table_name + \
                " WHERE driver.is_driver = True %s"%(drivers_cond))
            driver_result = self._cr.fetchall()
            driver_data = driver_result
        print('..................driver_data...............',driver_data)
        from_str = str(form)
        to_str = str(to)
        date_condition = f"fvt_table.expected_start_date > '{from_str}' and fvt_table.expected_start_date < '{to_str}' "
        trip_type_cond = ''
        if record_wizard.trip_type:
            trip_type_cond = f"and fvt_table.trip_type = '{record_wizard.trip_type}'"
        fuel_expense_cond = ""
        if record_wizard.fuel_expense_method_ids:
            fuel_expense_method_ids = record_wizard.fuel_expense_method_ids.ids
            fuel_expense_methods_str = len(fuel_expense_method_ids) == 1 and "(%s)" %fuel_expense_method_ids[0] or  str(tuple(fuel_expense_method_ids))
            fuel_expense_cond = f"and fvt_table.fuel_exp_method_id in {fuel_expense_methods_str}"



        table_name = "fleet_vehicle_trip as fvt_table"

        if report_type == 'detail':

            report_num = 2

            main_data = []
            for x in driver_data:
                trips_data = []
                drivers_cond = ""
                if x:
                    drivers_str = "(%s)" % x[0]
                    drivers_cond = f"and fvt_table.driver_id in {drivers_str}"
                print('x...............', x)
                self.env.cr.execute(
                    "select fvt_table.id as fvt_id,fvt_table.name as fvt_name,fvt_route.route_name as fvt_route_name\
                     FROM " + table_name + \
                    " LEFT JOIN bsg_route fvt_route ON fvt_table.route_id=fvt_route.id"
                    " WHERE fvt_table.state = 'finished' and %s %s %s %s" % (
                    date_condition, trip_type_cond, fuel_expense_cond, drivers_cond))

                result = self._cr.fetchall()
                vehicle_trips = pd.DataFrame(list(result))

                vehicle_trips = vehicle_trips.rename(
                    columns={0: 'fvt_id', 1: 'fvt_name', 2: 'fvt_route_name'})
                print('vehicle_trips...............', vehicle_trips)
                for index, value in vehicle_trips.iterrows():
                    so_line = []
                    # if y.payment > 0 and y.total_fuel_amount > 0:
                    stock_picking_ids = self.env['fleet.vehicle.trip.pickings'].search([('bsg_fleet_trip_id','=',int(value['fvt_id']))])
                    for z in stock_picking_ids:
                        agree_dis = 0
                        agree_rev = 0
                        driver_reward = 0
                        for i in z.picking_name.trip_history_ids:
                            if i.fleet_trip_id.id == int(value['fvt_id']) and i.fleet_trip_id.driver_id.id == x[0]:
                                agree_dis = agree_dis + i.trip_distance
                                agree_rev = agree_rev + i.earned_revenue
                        # agree_dis = sum(z.picking_name.trip_history_ids.filtered(lambda i:i.fleet_trip_id.id == y.id and i.fleet_trip_id.driver_id.id == y.driver_id.id).mapped('trip_distance'))
                        # agree_rev = sum(z.picking_name.trip_history_ids.filtered(lambda i:i.fleet_trip_id.id == y.id and i.fleet_trip_id.driver_id.id == y.driver_id.id).mapped('earned_revenue'))

                        so_line.append({
                            'so_ref': z.picking_name.sale_line_rec_name,
                            'so_amt': z.picking_name.total_without_tax,
                            'driver_reward': driver_reward,
                            'agree_dis': agree_dis,
                            'agree_rev': agree_rev,
                            'trip_dis': z.bsg_fleet_trip_id.trip_distance,
                            'vehicle': z.bsg_fleet_trip_id.vehicle_id.taq_number,
                            'vehicle_type': z.bsg_fleet_trip_id.display_expense_mthod_id.vehicle_type and z.bsg_fleet_trip_id.display_expense_mthod_id.vehicle_type.vehicle_type_name or " ",
                            'loc_from': z.loc_from.route_waypoint_name,
                            'loc_to': z.loc_to.route_waypoint_name,
                            'state': z.state,
                            'actual_start_date': z.bsg_fleet_trip_id.actual_start_datetime,
                            'trip_status': z.bsg_fleet_trip_id.state,
                            'total_cars': z.bsg_fleet_trip_id.total_cars,
                        })

                    if len(so_line) > 0:
                        trips_data.append({
                            'trip': value['fvt_name'],
                            'route_name': value['fvt_route_name'],
                            'so_line': so_line,
                        })

                if len(trips_data) > 0:
                    main_data.append({
                        'name': x[1],
                        'code': x[2],
                        'trips_data': trips_data,
                    })
            print('....................main_data.................',main_data)
        if report_type == 'summary':

            report_num = 1

            main_data = []
            for x in driver_data:
                tot_agree_dis = 0
                tot_agree_rev = 0
                driver_reward = 0
                # tot_trip_dis = 0
                # tot_so_amt = 0
                drivers_cond = ""
                if x:
                    drivers_str = "(%s)" % x[0]
                    drivers_cond = f"and fvt_table.driver_id in {drivers_str}"
                print('x...............', x)
                self.env.cr.execute(
                    "select fvt_table.id as fvt_id,fvt_table.name as fvt_name,fvt_route.route_name as fvt_route_name\
                     ,fvt_table.fuel_exp_method_id as fuel_exp_method,fvt_fuel_expense.vehicle_type as vehicle_type\
                     ,vehicle_type_table.vehicle_type_name as vehicle_type_name,fvt_table.total_cars as fvt_total_cars,fvt_table.trip_distance as fvt_trip_distance FROM " + table_name + \
                    " LEFT JOIN bsg_route fvt_route ON fvt_table.route_id=fvt_route.id"
                    " LEFT JOIN bsg_fuel_expense_method fvt_fuel_expense ON fvt_table.fuel_exp_method_id=fvt_fuel_expense.id"
                    " LEFT JOIN bsg_vehicle_type_table vehicle_type_table ON fvt_fuel_expense.vehicle_type=vehicle_type_table.id"
                    " WHERE fvt_table.state = 'finished' and %s %s %s %s" % (
                        date_condition, trip_type_cond, fuel_expense_cond, drivers_cond))

                result = self._cr.fetchall()
                vehicle_trips = pd.DataFrame(list(result))

                vehicle_trips = vehicle_trips.rename(columns={0: 'fvt_id', 1: 'fvt_name', 2: 'fvt_route_name',3:'fuel_exp_method',
                                                              4:'vehicle_type',5:'vehicle_type_name',6:'fvt_total_cars',7:'fvt_trip_distance'})
                vehicle_trips = vehicle_trips.fillna(0)
                # print('.............summary..vehicle_trips...........',vehicle_trips)
                vehicle_types_list = []
                for key, value in vehicle_trips.iterrows():
                    vehicle_types_list.append(value['vehicle_type_name'])
                print('...............vehicle_types_list.............',vehicle_types_list)
                if vehicle_types_list:
                    vehicle_trips_groupby = vehicle_trips.groupby(['vehicle_type_name'])
                    # trips_mapped_vehicle_type = trips.mapped('display_expense_mthod_id').mapped('vehicle_type')
                    # print('..............trips_mapped_vehicle_type..............', trips_mapped_vehicle_type)
                    for key_vehicle_type,dataframe_vehicle_type in vehicle_trips_groupby:
                        total_cars = 0
                        trip_distance = 0
                        trip_ids = []
                    #     filtered_trips = trips.filtered(lambda l: l.display_expense_mthod_id.vehicle_type == vehicle_type and l.payment > 0 and l.total_fuel_amount > 0)
                        for key,value in dataframe_vehicle_type.iterrows():
                            # trip_dis = 0
                            # so_amt = 0
                            agree_dis = 0
                            agree_rev = 0
                            stock_picking_ids = self.env['fleet.vehicle.trip.pickings'].search(
                                [('bsg_fleet_trip_id', '=', int(value['fvt_id']))])
                            trip_ids.append(int(value['fvt_id']))
                            for z in stock_picking_ids:
                                for i in z.picking_name.trip_history_ids:
                                    # if i.fleet_trip_id.id == y.id and i.fleet_trip_id.driver_id.id == x.id:
                                    agree_dis = agree_dis + i.trip_distance
                                    agree_rev = agree_rev + i.earned_revenue

                            # so_amt = so_amt + (z.picking_name.bsg_cargo_sale_id.total_amount-z.picking_name.bsg_cargo_sale_id.tax_amount_total)

                            # trip_dis = trip_dis + z.bsg_fleet_trip_id.trip_distance

                            # tot_trip_dis = tot_trip_dis + trip_dis
                            # tot_so_amt = tot_so_amt + so_amt
                            tot_agree_dis = tot_agree_dis + agree_dis
                            tot_agree_rev = tot_agree_rev + agree_rev
                            total_cars += int(value['fvt_total_cars'])
                            trip_distance += float(value['fvt_trip_distance'])
                        trips_count = len(dataframe_vehicle_type)
                        if trips_count > 0:
                            so_count = len(stock_picking_ids)
                            # empty_trips = filtered_trips.filtered(lambda tr: not tr.stock_picking_id)
                            empty_trips = self.env['fleet.vehicle.trip'].search_count([('id','in',trip_ids),('stock_picking_id','=',False)])
                            empty_trips_count = empty_trips
                            loaded_trips_count = trips_count - empty_trips_count
                            main_data.append({
                                'name': x[1],
                                'code': x[2],
                                'vehicle_type': key_vehicle_type,
                                'agree_dis': tot_agree_dis,
                                'agree_rev': tot_agree_rev,
                                'driver_reward': driver_reward,
                                # 'so_amt':tot_so_amt,
                                'trip_dis': trip_distance,
                                'total_cars': total_cars,
                                'so_count': int(so_count),
                                'empty_trips_count': int(empty_trips_count),
                                'loaded_trips_count': int(loaded_trips_count)
                            })

        print('................main_data.............', main_data)
        print('................main_data.............', main_data)
        print('................main_data.............', main_data)
        print('................main_data.............', main_data)
        print('................main_data.............', main_data)
        print('................main_data.............', main_data)
        print('................main_data.............', main_data)
        return {
            'doc_ids': docids,
            'doc_model': 'fleet.vehicle.trip',
            'form': form,
            'to': to,
            'main_data': main_data,
            'report_num': report_num,
            'print_by': self.env.user.name,
            'print_date': print_date,
            'docs':record_wizard
        }
        # return {
        #     'doc_ids': docids,
        #     'doc_model': 'fleet.vehicle.trip',
        # }


class DriverRewardsReportXlsx(models.AbstractModel):
    _name = 'report.bsg_drivers_reward_report.reward_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):
        model = lines['context']['active_model']
        active_id = lines['context']['active_id']
        record_wizard = self.env[model].browse(active_id)
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        form_tz = UTC.localize(record_wizard.form).astimezone(tz).replace(tzinfo=None)
        to_tz = UTC.localize(record_wizard.to).astimezone(tz).replace(tzinfo=None)

        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '10',
        })
        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#00cc44',
            'font_size': '12',
        })
        main_heading3 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#ffffff',
            'font_size': '13',
        })
        sheet = workbook.add_worksheet('Vehicle Details Report')
        sheet.set_column('A:Q', 15)
        row = 0
        col = 0
        # if record_wizard.filters == 'all':
        #     driver_data = self.env['hr.employee'].search([('is_driver', '=', True)])
        # else:
        #     driver_data = []
        #     for ser in record_wizard.driver_id:
        #         driver_data.append(ser)
        driver_data = []
        if record_wizard.filters == 'all':
            driver_table_name = "hr_employee as driver"
            self.env.cr.execute(
                "select driver.id as driver_id,driver.name as driver_name,driver.driver_code as driver_code FROM " + driver_table_name + \
                " WHERE driver.is_driver = True")
            driver_result = self._cr.fetchall()
            driver_data = driver_result
        else:
            driver_table_name = "hr_employee as driver"
            drivers = record_wizard.driver_id.ids
            print('.................else drivers..............', drivers)
            drivers_cond = ""
            if drivers:
                drivers_str = len(drivers) == 1 and "(%s)" % drivers[0] or str(
                    tuple(drivers))
                drivers_cond = f"and driver.id in {drivers_str}"
            self.env.cr.execute(
                "select driver.id as driver_id,driver.name as driver_name,driver.driver_code as driver_code FROM " + driver_table_name + \
                " WHERE driver.is_driver = True %s" % (drivers_cond))
            driver_result = self._cr.fetchall()
            driver_data = driver_result
        print('..................driver_data...............', driver_data)
        from_str = str(form_tz)
        to_str = str(to_tz)
        date_condition = f"fvt_table.expected_start_date > '{from_str}' and fvt_table.expected_start_date < '{to_str}' "
        trip_type_cond = ''
        if record_wizard.trip_type:
            trip_type_cond = f"and fvt_table.trip_type = '{record_wizard.trip_type}'"
        fuel_expense_cond = ""
        if record_wizard.fuel_expense_method_ids:
            fuel_expense_method_ids = record_wizard.fuel_expense_method_ids.ids
            fuel_expense_methods_str = len(fuel_expense_method_ids) == 1 and "(%s)" % fuel_expense_method_ids[0] or str(
                tuple(fuel_expense_method_ids))
            fuel_expense_cond = f"and fvt_table.fuel_exp_method_id in {fuel_expense_methods_str}"

        table_name = "fleet_vehicle_trip as fvt_table"
        if record_wizard.report_type == 'detail':
            self.env.ref(
                'bsg_drivers_reward_report.driver_reward_report_xlsx').report_file = "Drivers Reward Report (Details)"
            sheet.merge_range('A1:M1', 'تقرير انتاجية السائقين (تفصيلي) ', main_heading3)
            row += 1
            sheet.merge_range('A2:M2', 'Drivers Reward Report (Details)', main_heading3)
            row += 2

            sheet.write(row, col, 'Print By', main_heading2)
            sheet.write_string(row, col + 1, str(self.env.user.display_name), main_heading)
            sheet.write(row, col + 2, 'طباعة بواسطة', main_heading2)

            sheet.write(row, col + 4, 'Print Date', main_heading2)
            sheet.write_string(row, col + 5, str(date.today()), main_heading)
            sheet.write(row, col + 6, 'تاريخ الطباعة', main_heading2)

            row += 1

            sheet.write(row, col, 'From Date', main_heading2)
            sheet.write_string(row, col + 1, str(form_tz), main_heading)
            sheet.write(row, col + 2, 'من التاريخ', main_heading2)

            sheet.write(row, col + 4, 'To Date', main_heading2)
            sheet.write_string(row, col + 5, str(to_tz), main_heading)
            sheet.write(row, col + 6, 'حتى تاريخه', main_heading2)

            row += 1

            sheet.write(row, col, 'Driver Code', main_heading2)
            sheet.write(row, col + 1, 'Driver Name', main_heading2)
            sheet.write(row, col + 2, 'Trip NO', main_heading2)
            sheet.write(row, col + 3, 'Trip Type', main_heading2)
            sheet.write(row, col + 4, 'Location From', main_heading2)
            sheet.write(row, col + 5, 'Location To', main_heading2)
            sheet.write(row, col + 6, 'Actual Start Date', main_heading2)
            sheet.write(row, col + 7, 'Vehicle', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 9, 'Trip Distance', main_heading2)
            sheet.write(row, col + 10, 'Agreement Revenue', main_heading2)
            sheet.write(row, col + 11, 'Total Of Cars', main_heading2)
            sheet.write(row, col + 12, 'Trip Status', main_heading2)
            row += 1
            sheet.write(row, col, 'كود السائق', main_heading2)
            sheet.write(row, col + 1, 'اسم السائق', main_heading2)
            sheet.write(row, col + 2, 'رقم الرحلة', main_heading2)
            sheet.write(row, col + 3, 'نوع الرحلة', main_heading2)
            sheet.write(row, col + 4, 'فرع الشحن', main_heading2)
            sheet.write(row, col + 5, 'فرع الوصول', main_heading2)
            sheet.write(row, col + 6, 'تاريخ البدء الفعلي', main_heading2)
            sheet.write(row, col + 7, 'الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'نوع الشاحنة ', main_heading2)
            sheet.write(row, col + 9, 'مسافة الرحلة', main_heading2)
            sheet.write(row, col + 10, 'إيرادات الاتفاقية', main_heading2)
            sheet.write(row, col + 11, 'عدد الأتفاقيات', main_heading2)
            sheet.write(row, col + 12, 'حالة الرحلة', main_heading2)
            row += 1
            # main_data = []
            # for x in driver_data:
            #     trips_data = []
            #     domain = [('expected_start_date', '>=', record_wizard.form),
            #               ('expected_start_date', '<=', record_wizard.to),
            #               ('driver_id.id', '=', x.id), ('state', '=', 'finished')]
            #     if record_wizard.trip_type:
            #         domain.append(('trip_type', '=', record_wizard.trip_type))
            #     if record_wizard.fuel_expense_method_ids:
            #         domain.append(('display_expense_mthod_id', 'in', record_wizard.fuel_expense_method_ids.ids))
            #     trips = self.env['fleet.vehicle.trip'].search(domain)
            #     for y in trips:
            #         so_line = []
            #         if y.payment > 0 and y.total_fuel_amount > 0:
            #             for z in y.stock_picking_id:
            #                 agree_dis = 0
            #                 agree_rev = 0
            #                 driver_reward = 0
            #                 for i in z.picking_name.trip_history_ids:
            #                     if i.fleet_trip_id.id == y.id and i.fleet_trip_id.driver_id.id == x.id:
            #                         agree_dis = agree_dis + i.trip_distance
            #                         agree_rev = agree_rev + i.earned_revenue
            main_data = []
            for x in driver_data:
                trips_data = []
                drivers_cond = ""
                if x:
                    drivers_str = "(%s)" % x[0]
                    drivers_cond = f"and fvt_table.driver_id in {drivers_str}"
                print('x...............', x)
                self.env.cr.execute(
                    "select fvt_table.id as fvt_id,fvt_table.name as fvt_name,fvt_route.route_name as fvt_route_name\
                    ,fvt_table.trip_type as fvt_trip_type,fvt_table.actual_start_datetime as fvt_actual_start_datetime\
                    ,vehicle.taq_number,vehicle_type.vehicle_type_name as fvt_vehicle_type_name,fvt_table.state as fvt_state\
                    ,fvt_table.total_cars as fvt_total_cars,fvt_table.trip_distance as fvt_trip_distance\
                    ,start_route_waypoint.route_waypoint_name as start_branch,end_route_waypoint.route_waypoint_name as end_branch\
                    ,fvt_table.total_fuel_amount as fvt_total_fuel_amount,fvt_table.extra_distance as fvt_extra_distance FROM " + table_name + \
                    " LEFT JOIN bsg_route fvt_route ON fvt_table.route_id=fvt_route.id"
                    " LEFT JOIN fleet_vehicle vehicle ON fvt_table.vehicle_id=vehicle.id"
                    " LEFT JOIN bsg_fuel_expense_method fuel_expense_method ON fvt_table.fuel_exp_method_id=fuel_expense_method.id"
                    " LEFT JOIN bsg_vehicle_type_table vehicle_type ON fuel_expense_method.vehicle_type=vehicle_type.id"
                    " LEFT JOIN bsg_route_waypoints start_route_waypoint ON fvt_table.start_branch=start_route_waypoint.id"
                    " LEFT JOIN bsg_route_waypoints end_route_waypoint ON fvt_table.end_branch=end_route_waypoint.id"
                    " WHERE fvt_table.state = 'finished' and %s %s %s %s" % (date_condition, trip_type_cond, fuel_expense_cond, drivers_cond))


                result = self._cr.fetchall()
                vehicle_trips = pd.DataFrame(list(result))

                vehicle_trips = vehicle_trips.rename(
                    columns={0: 'fvt_id', 1: 'fvt_name', 2: 'fvt_route_name',3:'fvt_trip_type',4:'fvt_actual_start_datetime',
                             5:'vehicle_name',6:'fvt_vehicle_type_name',7:'fvt_state',8:'fvt_total_cars',9:'fvt_trip_distance',
                             10:'start_branch',11:'end_branch',12:'fvt_total_fuel_amount',13:'fvt_extra_distance'})
                print('vehicle_trips...............', vehicle_trips)
                for index, value in vehicle_trips.iterrows():
                    so_line = []
                    if float(value['fvt_total_fuel_amount']) > 0:
                        pkg_stock_pickings = 0
                        stock_picking_ids = self.env['fleet.vehicle.trip.pickings'].search(
                            [('bsg_fleet_trip_id', '=', int(value['fvt_id']))])
                        agree_dis = 0
                        agree_rev = 0
                        driver_reward = 0
                        loc_from = False
                        loc_to = False
                        if stock_picking_ids:
                            pkg_stock_picking_ids = stock_picking_ids.filtered(lambda l: l.is_package == True)
                            if pkg_stock_picking_ids:
                                pkg_stock_pickings = len(pkg_stock_picking_ids)
                            for z in stock_picking_ids:
                                for i in z.picking_name.trip_history_ids:
                                    if i.fleet_trip_id.id == int(value['fvt_id']) and i.fleet_trip_id.driver_id.id == x[0]:
                                        agree_dis = agree_dis + i.trip_distance
                                        agree_rev = agree_rev + i.earned_revenue
                                if z.loc_from.route_waypoint_name:
                                    loc_from = z.loc_from.route_waypoint_name
                                if z.loc_to.route_waypoint_name:
                                    loc_to = z.loc_to.route_waypoint_name
                                picking_name = z.picking_name
                        if x[2]:
                            sheet.write_string(row, col, str(x[2]), main_heading)
                        if x[1]:
                            sheet.write_string(row, col + 1, str(x[1]), main_heading)
                        if value['fvt_name']:
                            sheet.write_string(row, col + 2, str(value['fvt_name']), main_heading)
                        if value['fvt_trip_type']:
                            sheet.write_string(row, col + 3, str(value['fvt_trip_type']), main_heading)
                        if value['start_branch']:
                            sheet.write_string(row, col + 4, str(value['start_branch']), main_heading)
                        if value['end_branch']:
                            sheet.write_string(row, col + 5, str(value['end_branch']), main_heading)
                        if value['fvt_actual_start_datetime']:
                            sheet.write_string(row, col + 6, str(value['fvt_actual_start_datetime']),
                                               main_heading)
                        if value['vehicle_name']:
                            sheet.write_string(row, col + 7, str(value['vehicle_name']),
                                               main_heading)
                        if value['fvt_vehicle_type_name']:
                            sheet.write_string(row, col + 8,str(value['fvt_vehicle_type_name']),
                                               main_heading)
                        if value['fvt_trip_distance']:
                            sheet.write_string(row, col + 9, str(float(value['fvt_trip_distance'])+float(value['fvt_extra_distance'])),
                                               main_heading)
                        if agree_rev:
                            sheet.write_string(row, col + 10, str(agree_rev),
                                               main_heading)
                        if value['fvt_total_cars']:
                            sheet.write_string(row, col + 11, str(int(value['fvt_total_cars'])-pkg_stock_pickings),
                                               main_heading)
                        if value['fvt_state']:
                            sheet.write_string(row, col + 12, str(value['fvt_state']), main_heading)
                        row += 1
        if record_wizard.report_type == 'summary':
            self.env.ref(
                'bsg_drivers_reward_report.driver_reward_report_xlsx').report_file = "Drivers Reward Report (Summary)"
            sheet.merge_range('A1:G1', 'تقرير انتاجية السائقين (ملخص) ', main_heading3)
            row += 1
            sheet.merge_range('A2:G2', 'Drivers Reward Report (Summary)', main_heading3)
            row += 2

            sheet.write(row, col, 'Print By', main_heading2)
            sheet.write_string(row, col + 1, str(self.env.user.display_name), main_heading)
            sheet.write(row, col + 2, 'طباعة بواسطة', main_heading2)

            sheet.write(row, col + 4, 'Print Date', main_heading2)
            sheet.write_string(row, col + 5, str(date.today()), main_heading)
            sheet.write(row, col + 6, 'تاريخ الطباعة', main_heading2)

            row += 1

            sheet.write(row, col, 'From Date', main_heading2)
            sheet.write_string(row, col + 1, str(form_tz), main_heading)
            sheet.write(row, col + 2, 'من التاريخ', main_heading2)

            sheet.write(row, col + 4, 'To Date', main_heading2)
            sheet.write_string(row, col + 5, str(to_tz), main_heading)
            sheet.write(row, col + 6, 'حتى تاريخه', main_heading2)

            row += 1

            sheet.write(row, col, 'Driver Code', main_heading2)
            sheet.write(row, col + 1, 'Driver Name', main_heading2)
            sheet.write(row, col + 2, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 3, 'Trip Distance', main_heading2)
            sheet.write(row, col + 4, 'Total Agreements Revenue', main_heading2)
            sheet.write(row, col + 5, 'Total Agreements Count', main_heading2)
            sheet.write(row, col + 6, 'Total Loaded Trips Count', main_heading2)
            sheet.write(row, col + 7, 'Total Empty Trips Count', main_heading2)
            row += 1
            sheet.write(row, col, 'كود السائق', main_heading2)
            sheet.write(row, col + 1, 'اسم السائق', main_heading2)
            sheet.write(row, col + 2, 'نوع الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'مسافة الرحلات', main_heading2)
            sheet.write(row, col + 4, 'إجمالي إيرادات الإتفاقيات', main_heading2)
            sheet.write(row, col + 5, 'إجمالي عدد الإتفاقيات', main_heading2)
            sheet.write(row, col + 6, 'إجمالي عدد الرحلات المحملة', main_heading2)
            sheet.write(row, col + 7, 'إجمالي عدد الرحلات الفارغة', main_heading2)
            row += 1

            # main_data = []
            # for x in driver_data:
            #     tot_agree_dis = 0
            #     tot_agree_rev = 0
            #     driver_reward = 0
            #     # tot_trip_dis = 0
            #     # tot_so_amt = 0
            #     domain = [('expected_start_date', '>=', record_wizard.form),
            #               ('expected_start_date', '<=', record_wizard.to),
            #               ('driver_id.id', '=', x.id), ('state', '=', 'finished')]
            #     if record_wizard.trip_type:
            #         domain.append(('trip_type', '=', record_wizard.trip_type))
            #     if record_wizard.fuel_expense_method_ids:
            #         domain.append(('display_expense_mthod_id', 'in', record_wizard.fuel_expense_method_ids.ids))
            #     trips = self.env['fleet.vehicle.trip'].search(domain)
            #     trips_mapped_vehicle_type = trips.mapped('display_expense_mthod_id').mapped('vehicle_type')
            #     print('..............trips_mapped_vehicle_type..............', trips_mapped_vehicle_type)
            #     for vehicle_type in trips_mapped_vehicle_type:
            #         filtered_trips = trips.filtered(lambda l: l.vehicle_id.vehicle_type == vehicle_type and l.payment > 0 and l.total_fuel_amount > 0)
            #         for y in filtered_trips:
            #             # trip_dis = 0
            #             # so_amt = 0
            #             agree_dis = 0
            #             agree_rev = 0
            #             for z in y.stock_picking_id:
            #
            #                 for i in z.picking_name.trip_history_ids:
            #                     if i.fleet_trip_id.id == y.id and i.fleet_trip_id.driver_id.id == x.id:
            #                         agree_dis = agree_dis + i.trip_distance
            #                         agree_rev = agree_rev + i.earned_revenue
            #
            #             # so_amt = so_amt + (z.picking_name.bsg_cargo_sale_id.total_amount-z.picking_name.bsg_cargo_sale_id.tax_amount_total)
            #
            #             # trip_dis = trip_dis + z.bsg_fleet_trip_id.trip_distance
            #
            #             # tot_trip_dis = tot_trip_dis + trip_dis
            #             # tot_so_amt = tot_so_amt + so_amt
            #             tot_agree_dis = tot_agree_dis + agree_dis
            #             tot_agree_rev = tot_agree_rev + agree_rev
            #         trips_count = len(filtered_trips)
            #         if trips_count > 0:
            #             so_count = len(filtered_trips.mapped('stock_picking_id'))
            #             empty_trips = filtered_trips.filtered(lambda tr: not tr.stock_picking_id)
            #             empty_trips_count = len(empty_trips)
            #             loaded_trips_count = trips_count - empty_trips_count
            #             trip_distance = sum(filtered_trips.mapped('trip_distance'))
            main_data = []
            for x in driver_data:
                tot_agree_dis = 0
                tot_agree_rev = 0
                driver_reward = 0
                # tot_trip_dis = 0
                # tot_so_amt = 0
                drivers_cond = ""
                if x:
                    drivers_str = "(%s)" % x[0]
                    drivers_cond = f"and fvt_table.driver_id in {drivers_str}"
                print('x...............', x)
                self.env.cr.execute(
                    "select fvt_table.id as fvt_id,fvt_table.name as fvt_name,fvt_route.route_name as fvt_route_name\
                     ,fvt_table.fuel_exp_method_id as fuel_exp_method,fvt_fuel_expense.vehicle_type as vehicle_type\
                     ,vehicle_type_table.vehicle_type_name as vehicle_type_name,fvt_table.total_cars as fvt_total_cars\
                     ,fvt_table.trip_distance as fvt_trip_distance,fvt_table.extra_distance as fvt_extra_distance FROM " + table_name + \
                    " LEFT JOIN bsg_route fvt_route ON fvt_table.route_id=fvt_route.id"
                    " LEFT JOIN bsg_fuel_expense_method fvt_fuel_expense ON fvt_table.fuel_exp_method_id=fvt_fuel_expense.id"
                    " LEFT JOIN bsg_vehicle_type_table vehicle_type_table ON fvt_fuel_expense.vehicle_type=vehicle_type_table.id"
                    " WHERE fvt_table.state = 'finished' and fvt_table.total_fuel_amount > 0 and %s %s %s %s" % (
                        date_condition, trip_type_cond, fuel_expense_cond, drivers_cond))

                result = self._cr.fetchall()
                vehicle_trips = pd.DataFrame(list(result))

                vehicle_trips = vehicle_trips.rename(
                    columns={0: 'fvt_id', 1: 'fvt_name', 2: 'fvt_route_name', 3: 'fuel_exp_method',
                             4: 'vehicle_type', 5: 'vehicle_type_name', 6: 'fvt_total_cars',
                             7: 'fvt_trip_distance',8:'fvt_extra_distance'})
                vehicle_trips = vehicle_trips.fillna(0)
                # print('.............summary..vehicle_trips...........',vehicle_trips)
                vehicle_types_list = []
                for key, value in vehicle_trips.iterrows():
                    vehicle_types_list.append(value['vehicle_type_name'])
                print('...............vehicle_types_list.............', vehicle_types_list)
                if vehicle_types_list:
                    vehicle_trips_groupby = vehicle_trips.groupby(['vehicle_type_name'])
                    # trips_mapped_vehicle_type = trips.mapped('display_expense_mthod_id').mapped('vehicle_type')
                    # print('..............trips_mapped_vehicle_type..............', trips_mapped_vehicle_type)
                    for key_vehicle_type, dataframe_vehicle_type in vehicle_trips_groupby:
                        total_cars = 0
                        trip_distance = 0
                        trip_ids = []
                        #     filtered_trips = trips.filtered(lambda l: l.display_expense_mthod_id.vehicle_type == vehicle_type and l.payment > 0 and l.total_fuel_amount > 0)
                        for key, value in dataframe_vehicle_type.iterrows():
                            # trip_dis = 0
                            # so_amt = 0
                            agree_dis = 0
                            agree_rev = 0
                            pkg_stock_pickings = 0
                            stock_picking_ids = self.env['fleet.vehicle.trip.pickings'].search(
                                [('bsg_fleet_trip_id', '=', int(value['fvt_id']))])
                            if stock_picking_ids:
                                pkg_stock_picking_ids = stock_picking_ids.filtered(lambda l:l.is_package == True)
                                if pkg_stock_picking_ids:
                                    pkg_stock_pickings = len(pkg_stock_picking_ids)
                            trip_ids.append(int(value['fvt_id']))
                            for z in stock_picking_ids:
                                for i in z.picking_name.trip_history_ids:
                                    # if i.fleet_trip_id.id == y.id and i.fleet_trip_id.driver_id.id == x.id:
                                    agree_dis = agree_dis + i.trip_distance
                                    agree_rev = agree_rev + i.earned_revenue

                            # so_amt = so_amt + (z.picking_name.bsg_cargo_sale_id.total_amount-z.picking_name.bsg_cargo_sale_id.tax_amount_total)

                            # trip_dis = trip_dis + z.bsg_fleet_trip_id.trip_distance

                            # tot_trip_dis = tot_trip_dis + trip_dis
                            # tot_so_amt = tot_so_amt + so_amt
                            tot_agree_dis = tot_agree_dis + agree_dis
                            tot_agree_rev = tot_agree_rev + agree_rev
                            total_cars += (int(value['fvt_total_cars']) - pkg_stock_pickings)
                            trip_distance += (float(value['fvt_trip_distance']) + float(value['fvt_extra_distance']))
                        trips_count = len(dataframe_vehicle_type)
                        if trips_count > 0:
                            so_count = len(stock_picking_ids)
                            # empty_trips = filtered_trips.filtered(lambda tr: not tr.stock_picking_id)
                            empty_trips = self.env['fleet.vehicle.trip'].search_count(
                                [('id', 'in', trip_ids), ('stock_picking_id', '=', False)])
                            empty_trips_count = empty_trips
                            loaded_trips_count = trips_count - empty_trips_count
                            if x[2]:
                                sheet.write_string(row, col, str(x[2]), main_heading)
                            if x[1]:
                                sheet.write_string(row, col + 1, str(x[1]), main_heading)
                            if key_vehicle_type:
                                sheet.write_string(row, col + 2, str(key_vehicle_type), main_heading)
                            if trip_distance:
                                sheet.write_number(row, col + 3, trip_distance, main_heading)
                            if tot_agree_rev:
                                sheet.write_number(row, col + 4, tot_agree_rev, main_heading)
                            if so_count:
                                sheet.write_number(row, col + 5, int(total_cars), main_heading)
                            if loaded_trips_count:
                                sheet.write_number(row, col + 6, int(loaded_trips_count), main_heading)
                            if empty_trips_count:
                                sheet.write_number(row, col + 7, int(empty_trips_count), main_heading)
                            row += 1








