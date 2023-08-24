#-*- coding:utf-8 -*-
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

from odoo import api, models, fields, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning, ValidationError
from itertools import groupby
from pytz import timezone, UTC
import pandas as pd
import logging
_logger = logging.getLogger(__name__)

class BranchesLedgerReport(models.AbstractModel):
    _name = 'report.vehicle_revenue_report.vehicle_revenue_temp_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        record_wizard = self.env[model].browse(self.env.context.get('active_id'))
        print('..............docids.................',docids)
        print('..............record_wizard.................',record_wizard._name)


        form = record_wizard.form
        to = record_wizard.to
        vehicle_id = record_wizard.vehicle_id
        driver_id = record_wizard.driver_id
        trip_type = record_wizard.trip_type
        report_type = record_wizard.report_type
        vehicle_type = record_wizard.vehicle_type
        head = "Vehicle Revenue Report"

        report_type_num = 0
        report_type_name = " "


        driver_head = 0
        if len(driver_id) == 1:
            driver_head = 1

        veh_head = 0
        if len(vehicle_id) == 1:
            veh_head = 1


        report_num = 0
        if driver_head == 1 and veh_head == 0:
            report_num = 1
        if driver_head == 0 and veh_head == 1:
            report_num = 2
        if driver_head == 1 and veh_head == 1:
            report_num = 3

        all_fill = 0
        # vehicles =  self.env['fleet.vehicle'].browse()
        if not driver_id and not vehicle_id and not trip_type:
            all_fill = 1


        # if vehicle_id and not vehicle_type:
        # 	vehicles = vehicle_id
            # for v in vehicle_id:
            # 	vehicles.append(v)

        # if not vehicle_id and vehicle_type:
        # 	vehicles = self.env['fleet.vehicle'].search([('vehicle_type.id','in',vehicle_type.ids), ('state_id', 'not in', [1,7])])


        # if not vehicle_id and not vehicle_type:
        # 	vehicles = []
        # 	if not driver_id and not trip_type:
        # 		trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel')])
        # 	elif driver_id and not trip_type:
        # 		trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('driver_id.id','in',driver_id.ids)])
        # 	elif not driver_id and trip_type:
        # 		trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type)])
        # 	elif driver_id and trip_type:
        # 		trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type),('driver_id.id','in',driver_id.ids)])
        # 	vehicles = trips_id.mapped('vehicle_id')
            # for j in trips_id:
            # 	if j.vehicle_id not in vehicles:
            # 		vehicles.append(j.vehicle_id)
        domain = [('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('vehicle_id.state_id', 'not in', [1,7])]
        if record_wizard.fuel_expense_method_ids:
            domain.append(('display_expense_mthod_id', 'in', record_wizard.fuel_expense_method_ids.ids))
        if vehicle_id:
            domain.append(('vehicle_id.id', 'in', vehicle_id.ids))
        if vehicle_type:
            domain.append(('vehicle_id.vehicle_type.id', 'in', vehicle_type.ids))
        if driver_id:
            domain.append(('driver_id.id','in',driver_id.ids))
        if trip_type:
            domain.append(('trip_type','=',trip_type))
        all_trips = self.env['fleet.vehicle.trip'].search(domain,order="vehicle_id")
        # if not vehicles:
        # 	vehicles = self.env['fleet.vehicle'].search([])
        # if not vehicles:
        # 	vehicles = set(all_trips.mapped('vehicle_id'))
        main_data = []
        # sorted_all_trips =  sorted(all_trips ,key=lambda t:t.vehicle_id)
        grouped_all_trips = groupby(all_trips, lambda l: (l.vehicle_id, l.display_expense_mthod_id.display_name))
        print('......................grouped_all_trips.............', grouped_all_trips)
        if report_type == 'summary':

            report_type_num = 1
            report_type_name = "(Summary)"
            for group, trips in grouped_all_trips:
                vehicle_id = group[0]
                expense_method_name = group[1]
                print('.........vehicle_id........', vehicle_id)
                print('.........trips........', trips)
                # if not trips:
                # 	break
                # trips = all_trips.filtered(lambda r: r.vehicle_id.id == tr.id)
                # all_trips -= trips
                # if not driver_id and not trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('vehicle_id.id','=',tr.id)])
                # elif driver_id and not trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])
                # elif not driver_id and trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('trip_type','=',trip_type),('vehicle_id.id','=',tr.id)])
                # elif driver_id and trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('trip_type','=',trip_type),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])

                if trips:
                    tr_num = 0
                    sale_line_count = 0
                    fuel_trip_amount = 0
                    dis = 0
                    v_revenue = 0
                    empty_trip_count = 0
                    for rec in trips:
                        tr_num+=1
                        fuel_trip_amount += rec.fuel_trip_amt
                        dis += (rec.trip_distance + rec.extra_distance)
                        if not rec.stock_picking_id:
                            empty_trip_count += 1

                        # if rec.stock_picking_id:
                            # sale_line_count += len(rec.stock_picking_id)
                            # pickings = rec.stock_picking_id.filtered(lambda pick: pick.state in ['Delivered', 'done', 'released'])
                        for ch in rec.stock_picking_id:
                            sale_line_count +=1
                            so = ch.picking_name
                            if so.state not in ['Delivered', 'done', 'released']:
                                continue
                            # history_lines =  so.trip_history_ids.filtered(lambda hl: hl.fleet_trip_id.id == rec.id)
                            for hl in so.trip_history_ids:
                                if hl.fleet_trip_id.id  != rec.id:
                                    continue
                                v_revenue += hl.earned_revenue

                            # if history_lines:
                            # 	v_revenue += sum(history_lines.mapped('earned_revenue'))
                            # for his in ch.picking_name.trip_history_ids:
                            # 	v_revenue = v_revenue + his.earned_revenue

                    driver = vehicle_id.bsg_driver
                    main_data.append({
                        'v_code':vehicle_id.taq_number,
                        'v_brand':vehicle_id.model_id.brand_id.name or '',
                        'driver':driver.name,
                        'driver_code':driver.driver_code,
                        'tr_num':tr_num,
                        'tr_sale_lines':sale_line_count,
                        'fuel_exp': fuel_trip_amount,
                        'dis': dis,
                        'v_revenue':v_revenue,
                        'empty_trip_count': empty_trip_count,
                        'expense_method': expense_method_name
                        })

        if report_type == 'detail':

            report_type_name = "(Detail)"

            report_type_num = 2

            for group, trips in grouped_all_trips:
                vehicle_id = group[0]
                expense_method_id = group[1]
                # if not all_trips:
                # 	break
                # trips = all_trips.filtered(lambda r: r.vehicle_id.id == tr.id)
                # all_trips -= trips
                # if not driver_id and not trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('vehicle_id.id','=',tr.id)])
                # if driver_id and not trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])
                # if not driver_id and trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('trip_type','=',trip_type),('vehicle_id.id','=',tr.id)])
                # if driver_id and trip_type:
                # 	trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','not in', ['draft','cancel']),('trip_type','=',trip_type),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])

                if trips:
                    trip_data = []

                    for rec in trips:

                        v_revenue = 0
                        sale_line_count = 0

                        # if rec.stock_picking_id:
                            # sale_line_count = len(rec.stock_picking_id)
                            # so_lines = rec.stock_picking_id.filtered(lambda l: l.state in ['Delivered', 'done', 'released'])
                        for ch in rec.stock_picking_id:
                            so = ch.picking_name
                            sale_line_count +=1
                            if so.state not in ['Delivered', 'done', 'released']:
                                continue
                            # history_lines =  so.trip_history_ids.filtered(lambda hl: hl.fleet_trip_id.id == rec.id)
                            for hl in so.trip_history_ids:
                                if hl.fleet_trip_id.id  != rec.id:
                                    continue
                                v_revenue += hl.earned_revenue
                            # for his in ch.picking_name.trip_history_ids:
                            # 	v_revenue = v_revenue + his.earned_revenue

                        trip_data.append({
                            'trip_num':rec.name,
                            'route':rec.route_id.route_name,
                            'tr_sale_lines':sale_line_count,
                            'fuel_exp': rec.fuel_trip_amt,
                            'dis': (rec.trip_distance + rec.extra_distance),
                            'v_revenue':v_revenue,
                            'expected_start_date': rec.expected_start_date and rec.expected_start_date.strftime('%Y-%m-%d') or '',
                            'fuel_expense_method': rec.display_expense_mthod_id.display_name,
                            'trip_type': rec.trip_type,
                            'trip_state': rec.state
                            })

                    driver = vehicle_id.bsg_driver
                    main_data.append({
                        'v_code':vehicle_id.taq_number,
                        'v_brand': vehicle_id.model_id.brand_id.name or '',
                        'driver':driver.name,
                        'driver_code':driver.driver_code,
                        'trip_data':trip_data,
                        })





        return {
            'doc_ids': docids,
            'doc_model':'fleet.vehicle.trip',
            'form': form,
            'to': to,
            'head': head,
            'vehicle_id': record_wizard.vehicle_id,
            'driver_id': record_wizard.driver_id,
            'trip_type': record_wizard.trip_type,
            'main_data': main_data,
            'report_num': report_num,
            'driver_head': driver_head,
            'veh_head': veh_head,
            'all_fill': all_fill,
            'report_type_num': report_type_num,
            'report_type_name': report_type_name,
            'docs':record_wizard

        }

class VehicleRevenueReportXlsx(models.AbstractModel):
    _name = 'report.vehicle_revenue_report.vehicle_revenue_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):
        model = lines['context']['active_model']
        active_id = lines['context']['active_id']
        record_wizard = self.env[model].browse(active_id)

        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '10',
        })
        main_heading1 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": 'white',
            'font_size': '14',
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
        sheet = workbook.add_worksheet('Vehicle Revenue Report')
        sheet.set_column('A:Q', 15)
        row = 0
        col = 0
        form = record_wizard.form
        to = record_wizard.to
        vehicle_id = record_wizard.vehicle_id
        driver_id = record_wizard.driver_id
        trip_type = record_wizard.trip_type
        report_type = record_wizard.report_type
        vehicle_type = record_wizard.vehicle_type
        head = "Vehicle Revenue Report"

        report_type_num = 0
        report_type_name = " "

        driver_head = 0
        if len(driver_id) == 1:
            driver_head = 1

        veh_head = 0
        if len(vehicle_id) == 1:
            veh_head = 1

        report_num = 0
        if driver_head == 1 and veh_head == 0:
            report_num = 1
        if driver_head == 0 and veh_head == 1:
            report_num = 2
        if driver_head == 1 and veh_head == 1:
            report_num = 3

        all_fill = 0
        # vehicles =  self.env['fleet.vehicle'].browse()
        if not driver_id and not vehicle_id and not trip_type:
            all_fill = 1

        from_str = str(form)
        to_str = str(to)
        date_condition = f"fvt_table.expected_start_date > '{from_str}' and fvt_table.expected_start_date < '{to_str}'"

        fuel_expense_cond = ""
        if record_wizard.fuel_expense_method_ids:
            fuel_expense_method_ids = record_wizard.fuel_expense_method_ids.ids
            fuel_expense_methods_str = len(fuel_expense_method_ids) == 1 and "(%s)" % fuel_expense_method_ids[0] or str(
                tuple(fuel_expense_method_ids))
            fuel_expense_cond = f"and fvt_table.fuel_exp_method_id in {fuel_expense_methods_str}"

        vehicle_cond = ""
        if record_wizard.vehicle_id:
            vehicle_ids = record_wizard.vehicle_id.ids
            vehicle_ids_str = len(vehicle_ids) == 1 and "(%s)" % vehicle_ids[0] or str(
                tuple(vehicle_ids))
            vehicle_cond = f"and fvt_table.vehicle_id in {fuel_expense_methods_str}"

        vehicle_type_cond = ""
        if record_wizard.vehicle_type:
            vehicle_type_ids = record_wizard.vehicle_type.ids
            vehicle_type_ids_str = len(vehicle_type_ids) == 1 and "(%s)" % vehicle_type_ids[0] or str(
                tuple(vehicle_type_ids))
            vehicle_cond = f"and vehicle.vehicle_type in {vehicle_type_ids_str}"

        driver_cond = ""
        if record_wizard.driver_id:
            driver_ids = record_wizard.driver_id.ids
            driver_ids_str = len(driver_ids) == 1 and "(%s)" % driver_ids[0] or str(
                tuple(driver_ids))
            driver_cond = f"and fvt_table.driver_id in {driver_ids_str}"

        trip_type_cond = ""
        if record_wizard.trip_type:
            trip_type = record_wizard.trip_type
            trip_type_cond = f"and fvt_table.trip_type = '{trip_type}'"

        route_type_cond = ""
        if record_wizard.route_type:
            route_type = record_wizard.route_type
            route_type_cond = f"and route.route_type = '{route_type}'"

        # print('...........result length.............', len(result))
        # print('...........result.............', result)
    # domain = [('expected_start_date', '>=', form), ('expected_start_date', '<=', to),
    #           ('state', 'not in', ['draft', 'cancel']), ('vehicle_id.state_id', 'not in', [1, 7])]
    # if record_wizard.fuel_expense_method_ids:
    #     domain.append(('display_expense_mthod_id', 'in', record_wizard.fuel_expense_method_ids.ids))
    # if vehicle_id:
    #     domain.append(('vehicle_id.id', 'in', vehicle_id.ids))
    # if vehicle_type:
    #     domain.append(('vehicle_id.vehicle_type.id', 'in', vehicle_type.ids))
    # if driver_id:
    #     domain.append(('driver_id.id', 'in', driver_id.ids))
    # if trip_type:
    #     domain.append(('trip_type', '=', trip_type))
    # all_trips = self.env['fleet.vehicle.trip'].search(domain, order="vehicle_id")
    # grouped_all_trips = groupby(all_trips, lambda l: (l.vehicle_id, l.display_expense_mthod_id.display_name))
    # print('......................grouped_all_trips.............', grouped_all_trips)
        if record_wizard.report_type == 'summary':
            self.env.ref(
                'vehicle_revenue_report.vehicle_revenue_xlsx_report').report_file = "Vehicle Revenue Report (Summary)"
            sheet.merge_range('A1:M1', 'تقرير انتاجية الشاحنات (اجمالي)', main_heading3)
            row += 1
            sheet.merge_range('A2:M2', 'Vehicle Revenue Report (Summary)', main_heading3)
            row += 2

            sheet.write(row, col, 'Print By', main_heading2)
            sheet.write_string(row, col + 1, str(self.env.user.display_name), main_heading)
            sheet.write(row, col + 2, 'طباعة بواسطة', main_heading2)

            sheet.write(row, col + 4, 'Print Date', main_heading2)
            sheet.write_string(row, col + 5, str(date.today()), main_heading)
            sheet.write(row, col + 6, 'تاريخ الطباعة', main_heading2)

            row += 1

            sheet.write(row, col, 'From Date', main_heading2)
            sheet.write_string(row, col + 1, str(form), main_heading)
            sheet.write(row, col + 2, 'من التاريخ', main_heading2)

            sheet.write(row, col + 4, 'To Date', main_heading2)
            sheet.write_string(row, col + 5, str(to), main_heading)
            sheet.write(row, col + 6, 'حتى تاريخه', main_heading2)

            row += 1

            en_col=0
            if veh_head != 1:
                sheet.write(row, en_col, 'Vehicle Code', main_heading2)
                en_col+=1
                sheet.write(row, en_col, 'Vehicle Brand', main_heading2)
                en_col += 1
            if driver_head != 1:
                sheet.write(row, en_col, 'Driver Name', main_heading2)
                en_col += 1
                sheet.write(row, en_col, 'Driver Code', main_heading2)
                en_col += 1
            sheet.write(row, en_col, 'The Number Of Empty Trips', main_heading2)
            en_col += 1
            sheet.write(row, en_col, 'Number of Trips', main_heading2)
            en_col += 1
            sheet.write(row, en_col, 'Number of Shipped Cars', main_heading2)
            en_col += 1
            sheet.write(row, en_col, 'Vehicle Fuel Expenses', main_heading2)
            en_col += 1
            sheet.write(row, en_col, 'Actual Trip Distance', main_heading2)
            en_col += 1
            sheet.write(row, en_col, 'Vehicle Revenue', main_heading2)
            en_col += 1
            sheet.write(row, en_col, 'Fuel Expense Method', main_heading2)
            row += 1
            ar_col = 0
            if veh_head != 1:
                sheet.write(row, ar_col, 'رقم الشاحنه', main_heading2)
                ar_col += 1
                sheet.write(row, ar_col, 'ماركة الشاحنه', main_heading2)
                ar_col += 1
            if driver_head != 1:
                sheet.write(row, ar_col, 'اسم السائق', main_heading2)
                ar_col += 1
                sheet.write(row, ar_col, 'رمز السائق', main_heading2)
                ar_col += 1
            sheet.write(row, ar_col, 'عدد الرحلات الفارغة', main_heading2)
            ar_col += 1
            sheet.write(row, ar_col, 'عدد الرحلات', main_heading2)
            ar_col += 1
            sheet.write(row, ar_col, 'عدد السيارات المحمله', main_heading2)
            ar_col += 1
            sheet.write(row, ar_col, 'مصروفات الطريق', main_heading2)
            ar_col += 1
            sheet.write(row, ar_col, 'المسافه المقطوعه للشاحنه', main_heading2)
            ar_col += 1
            sheet.write(row, ar_col, 'ايرادات الشاحنه', main_heading2)
            ar_col += 1
            sheet.write(row, ar_col, 'قسيمة الوقود', main_heading2)
            row += 1
            main_data = []
            tot_trip = 0
            tot_sale = 0
            tot_exp = 0
            tot_rev = 0
            tot_dis = 0
            table_name = "fleet_vehicle_trip as fvt_table"
            self.env.cr.execute(
                "select fvt_table.id as fvt_id,fvt_table.vehicle_id as vehicle_id,vehicle.vehicle_type as vehicle_type_id\
                ,fvt_table.driver_id as fvt_driver_id,fvt_table.trip_type as trip_type,fvt_table.fuel_exp_method_id as fuel_exp_method_id\
                ,fvt_table.fuel_trip_amt as fuel_trip_amt,fvt_table.trip_distance as trip_distance,fvt_table.extra_distance as extra_distance\
                ,vehicle.taq_number as taq_number,vehicle_model_brand.name as brand_name,driver.name as driver_name,driver.driver_code as driver_code\
                ,fvt_table.total_cars as fvt_number_of_cars,fvt_table.total_fuel_amount as fvt_total_fuel_amount,fvt_table.total_reward_amount as fvt_total_reward_amount\
                ,fvt_table.additional_fuel_exp as fvt_additional_fuel_exp FROM " + table_name + \
                " LEFT JOIN fleet_vehicle vehicle ON fvt_table.vehicle_id=vehicle.id"
                " LEFT JOIN fleet_vehicle_model vehicle_model ON vehicle.model_id=vehicle_model.id"
                " LEFT JOIN fleet_vehicle_model_brand vehicle_model_brand ON vehicle_model.brand_id=vehicle_model_brand.id"
                " LEFT JOIN hr_employee driver ON vehicle.bsg_driver=driver.id"
                " LEFT JOIN bsg_route route ON fvt_table.route_id=route.id"
                " WHERE fvt_table.state not in ('draft','cancel') and vehicle.state_id not in (1,7) and fvt_table.total_fuel_amount > 0 and %s %s %s %s %s %s %s order by fvt_table.vehicle_id " % (
                    date_condition, fuel_expense_cond, vehicle_cond, vehicle_type_cond, driver_cond, trip_type_cond, route_type_cond))

            result = self._cr.fetchall()
            all_trips = pd.DataFrame(list(result))

            all_trips = all_trips.rename(
                columns={0: 'fvt_id', 1: 'vehicle_id', 2: 'vehicle_type_id', 3: 'fvt_driver_id', 4: 'trip_type',
                         5: 'fuel_exp_method_id', 6: 'fuel_trip_amt', 7: 'trip_distance', 8: 'extra_distance',
                         9: 'taq_number', 10: 'brand_name', 11: 'driver_name', 12: 'driver_code',13:'fvt_number_of_cars',
                         14:'fvt_total_fuel_amount',15:'fvt_total_reward_amount',16:'fvt_additional_fuel_exp'})
            print('vehicle_trips...............', all_trips)
            grouped_all_trips = all_trips.groupby(['vehicle_id', 'fuel_exp_method_id'])
            for group,trips in grouped_all_trips:
                print('...............group............',group)
                vehicle_id = group[0]
                expense_method_id = group[1]
                if not trips.empty:
                    tr_num = 0
                    sale_line_count = 0
                    fuel_trip_amount = 0
                    dis = 0
                    v_revenue = 0
                    empty_trip_count = 0
                    for key,value in trips.iterrows():
                        fuel_trip_amount += (float(value['fvt_total_fuel_amount']) + float(value['fvt_total_reward_amount']) + float(value['fvt_additional_fuel_exp']))
                        dis += (float(value['trip_distance']) + float(value['extra_distance']))
                        stock_picking_ids = self.env['fleet.vehicle.trip.pickings'].search(
                            [('bsg_fleet_trip_id', '=', int(value['fvt_id']))])
                        print('.............fvt_total_fuel_amount...........',value['fvt_total_fuel_amount'])
                        if int(value['fvt_number_of_cars']) == 0:
                            empty_trip_count += 1
                        else:
                            tr_num += 1
                        for ch in stock_picking_ids:
                            if not ch.is_package:
                                sale_line_count +=1
                                so = ch.picking_name
                                if so.state not in ['Delivered', 'done', 'released']:
                                    continue
                                for hl in so.trip_history_ids:
                                    if hl.fleet_trip_id.id  != int(value['fvt_id']):
                                        continue
                                    v_revenue += hl.earned_revenue
                    # driver = vehicle_id.bsg_driver
                    data_col = 0
                    if veh_head != 1:
                        if value['taq_number']:
                            sheet.write_string(row, data_col, str(value['taq_number']), main_heading)
                        data_col += 1
                        if value['brand_name']:
                            sheet.write_string(row, data_col, str(value['brand_name']), main_heading)
                        data_col += 1
                    if driver_head != 1:
                        if value['driver_name']:
                            sheet.write_string(row, data_col, str(value['driver_name']), main_heading)
                        data_col += 1
                        if value['driver_code']:
                            sheet.write_string(row, data_col, str(value['driver_code']), main_heading)
                        data_col += 1
                    if empty_trip_count:
                        sheet.write_number(row, data_col, empty_trip_count, main_heading)
                    data_col += 1
                    if tr_num:
                        sheet.write_number(row, data_col, tr_num, main_heading)
                        tot_trip += tr_num
                    data_col += 1
                    if sale_line_count:
                        sheet.write_number(row, data_col, sale_line_count,
                                           main_heading)
                        tot_sale += sale_line_count
                    data_col += 1
                    if fuel_trip_amount:
                        sheet.write_number(row, data_col, fuel_trip_amount,
                                           main_heading)
                        tot_exp += fuel_trip_amount
                    data_col += 1
                    if dis:
                        sheet.write_number(row, data_col,dis,main_heading)
                        tot_dis += dis
                    data_col += 1
                    if v_revenue:
                        sheet.write_number(row, data_col, v_revenue,
                                           main_heading)
                        tot_rev += v_revenue
                    data_col += 1
                    expense_method_id = self.env['bsg.fuel.expense.method'].search([('id','=',int(expense_method_id))])
                    if expense_method_id:
                        sheet.write_string(row, data_col, str(expense_method_id.display_name),
                                           main_heading)
                    data_col += 1
                    row += 1
            sheet.write(row, col, 'Total', main_heading2)
            if report_num == 1:
                col += 3
            elif report_num == 2:
                col += 3
            elif report_num == 3:
                col += 1
            else:
                col += 5
            sheet.write_number(row, col, float(tot_trip),main_heading)
            sheet.write_number(row, col+1, float(tot_sale),main_heading)
            sheet.write_number(row, col+2, float(tot_exp),main_heading)
            sheet.write_number(row, col+3, float(tot_dis),main_heading)
            sheet.write_number(row, col+4, float(tot_rev),main_heading)
        if record_wizard.report_type == 'detail':
            self.env.ref(
                'vehicle_revenue_report.vehicle_revenue_xlsx_report').report_file = "Vehicle Revenue Report (Details)"
            sheet.merge_range('A1:M1', 'تقرير انتاجية الشاحنات (تفصيلي) ', main_heading3)
            row += 1
            sheet.merge_range('A2:M2', 'Vehicle Revenue Report (Details)', main_heading3)
            row += 2

            sheet.write(row, col, 'Print By', main_heading2)
            sheet.write_string(row, col + 1, str(self.env.user.display_name), main_heading)
            sheet.write(row, col + 2, 'طباعة بواسطة', main_heading2)

            sheet.write(row, col + 4, 'Print Date', main_heading2)
            sheet.write_string(row, col + 5, str(date.today()), main_heading)
            sheet.write(row, col + 6, 'تاريخ الطباعة', main_heading2)

            row += 1

            sheet.write(row, col, 'From Date', main_heading2)
            sheet.write_string(row, col + 1, str(form), main_heading)
            sheet.write(row, col + 2, 'من التاريخ', main_heading2)

            sheet.write(row, col + 4, 'To Date', main_heading2)
            sheet.write_string(row, col + 5, str(to), main_heading)
            sheet.write(row, col + 6, 'حتى تاريخه', main_heading2)

            row += 1

            sheet.write(row, col, 'Vehicle Code', main_heading2)
            sheet.write(row, col+1, 'Vehicle brand', main_heading2)
            sheet.write(row, col+2, 'Driver Name', main_heading2)
            sheet.write(row, col+3, 'Driver Code', main_heading2)
            sheet.write(row, col+4, 'Trip Number', main_heading2)
            sheet.write(row, col+5, 'Trip Date', main_heading2)
            sheet.write(row, col+6, 'Fuel Expense Method', main_heading2)
            sheet.write(row, col+7, 'Trip Type', main_heading2)
            sheet.write(row, col+8, 'Trip State', main_heading2)
            sheet.write(row, col+9, 'Route', main_heading2)
            sheet.write(row, col+10, 'Number of Shipped Cars', main_heading2)
            sheet.write(row, col+11, 'Vehicle Fuel Expenses', main_heading2)
            sheet.write(row, col+12, 'Actual Trip Distance', main_heading2)
            sheet.write(row, col+13, 'Vehicle Revenue', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنه', main_heading2)
            sheet.write(row, col + 2, 'اسم السائق', main_heading2)
            sheet.write(row, col + 3, 'رمز السائق', main_heading2)
            sheet.write(row, col + 4, 'رقم الرحلة', main_heading2)
            sheet.write(row, col + 5, 'تاريخ الرحلة', main_heading2)
            sheet.write(row, col + 6, 'قسيمة الوقود', main_heading2)
            sheet.write(row, col + 7, 'نوع الرحلة', main_heading2)
            sheet.write(row, col + 8, 'حالة الرحلة', main_heading2)
            sheet.write(row, col + 9, 'الطريق', main_heading2)
            sheet.write(row, col + 10, 'عدد السيارات المحمله', main_heading2)
            sheet.write(row, col + 11, 'مصروفات الطريق', main_heading2)
            sheet.write(row, col + 12, 'المسافه المقطوعه للشاحنه', main_heading2)
            sheet.write(row, col + 13, 'ايرادات الشاحنه', main_heading2)
            row += 1
            main_data = []
            table_name = "fleet_vehicle_trip as fvt_table"
            self.env.cr.execute(
                "select fvt_table.id as fvt_id,fvt_table.vehicle_id as vehicle_id,vehicle.vehicle_type as vehicle_type_id\
                ,fvt_table.driver_id as fvt_driver_id,fvt_table.trip_type as trip_type,fvt_table.fuel_exp_method_id as fuel_exp_method_id\
                ,fvt_table.fuel_trip_amt as fuel_trip_amt,fvt_table.trip_distance as trip_distance,fvt_table.extra_distance as extra_distance\
                ,vehicle.taq_number as taq_number,vehicle_model_brand.name as brand_name,driver.name as driver_name,driver.driver_code as driver_code\
                ,fvt_table.expected_start_date as expected_start_date,fvt_table.state as fvt_state,fvt_table.name as trip_name,route.route_name as route_name\
                ,fvt_table.total_fuel_amount as fvt_total_fuel_amount,fvt_table.total_reward_amount as fvt_total_reward_amount\
                ,fvt_table.additional_fuel_exp as fvt_additional_fuel_exp FROM " + table_name + \
                " LEFT JOIN fleet_vehicle vehicle ON fvt_table.vehicle_id=vehicle.id"
                " LEFT JOIN fleet_vehicle_model vehicle_model ON vehicle.model_id=vehicle_model.id"
                " LEFT JOIN fleet_vehicle_model_brand vehicle_model_brand ON vehicle_model.brand_id=vehicle_model_brand.id"
                " LEFT JOIN hr_employee driver ON vehicle.bsg_driver=driver.id"
                " LEFT JOIN bsg_route route ON fvt_table.route_id=route.id"
                " WHERE fvt_table.state not in ('draft','cancel') and vehicle.state_id not in (1,7) and fvt_table.total_fuel_amount > 0 and %s %s %s %s %s %s %s order by fvt_table.vehicle_id " % (
                    date_condition, fuel_expense_cond, vehicle_cond, vehicle_type_cond, driver_cond, trip_type_cond, route_type_cond))

            result = self._cr.fetchall()
            all_trips = pd.DataFrame(list(result))

            all_trips = all_trips.rename(
                columns={0: 'fvt_id', 1: 'vehicle_id', 2: 'vehicle_type_id', 3: 'fvt_driver_id', 4: 'trip_type',
                         5: 'fuel_exp_method_id', 6: 'fuel_trip_amt', 7: 'trip_distance', 8: 'extra_distance',
                         9: 'taq_number',10: 'brand_name', 11: 'driver_name', 12: 'driver_code',13:'expected_start_date',
                         14:'fvt_state',15:'trip_name',16:'route_name',17:'fvt_total_fuel_amount',18:'fvt_total_reward_amount',
                         19:'fvt_additional_fuel_exp'})
            print('vehicle_trips...............', all_trips)
            grouped_all_trips = all_trips.groupby(['vehicle_id', 'fuel_exp_method_id'])
            for group, trips in grouped_all_trips:
                print('...............group............', group)
                vehicle_id = group[0]
                expense_method_id = group[1]
                if not trips.empty:
                    vehicle = self.env['fleet.vehicle'].search([('id','=',int(vehicle_id))])
                    if vehicle.taq_number:
                        sheet.write_string(row, col, str(vehicle.taq_number), main_heading1)
                    if vehicle.model_id.brand_id.name:
                        sheet.write_string(row, col + 1, str(vehicle.model_id.brand_id.name), main_heading1)
                    if vehicle.bsg_driver.name:
                        sheet.write_string(row, col + 2, str(vehicle.bsg_driver.name), main_heading1)
                    if vehicle.bsg_driver.driver_code:
                        sheet.write_string(row, col + 3, str(vehicle.bsg_driver.driver_code), main_heading1)
                    row += 1
                    trip_col = 4
                    trip_data = []
                    tot_trip = 0
                    tot_sale = 0
                    tot_exp = 0
                    tot_rev = 0
                    tot_dis = 0
                    for key,value in trips.iterrows():
                        v_revenue = 0
                        sale_line_count = 0
                        vehicle_fuel_expenses = 0
                        stock_picking_ids = self.env['fleet.vehicle.trip.pickings'].search(
                            [('bsg_fleet_trip_id', '=', int(value['fvt_id']))])
                        for ch in stock_picking_ids:
                            if not ch.is_package:
                                so = ch.picking_name
                                sale_line_count +=1
                                if so.state not in ['Delivered', 'done', 'released']:
                                    continue
                                for hl in so.trip_history_ids:
                                    if hl.fleet_trip_id.id  != int(value['fvt_id']):
                                        continue
                                    v_revenue += hl.earned_revenue
                        dis = (float(value['trip_distance']) + float(value['extra_distance']))
                        vehicle_fuel_expenses = (float(value['fvt_total_fuel_amount']) + float(value['fvt_total_reward_amount']) + float(value['fvt_additional_fuel_exp']))
                        expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['fuel_exp_method_id']))])
                        if value['trip_name']:
                            sheet.write_string(row, trip_col, str(value['trip_name']), main_heading)
                        if value['expected_start_date']:
                            print('.............expect start date type.............',type(value['expected_start_date']))
                            # sheet.write_string(row, trip_col + 1, str(rec.expected_start_date.strftime('%Y-%m-%d')), main_heading)
                            sheet.write_string(row, trip_col + 1, str(value['expected_start_date']), main_heading)
                        if expense_method_id:
                            sheet.write_string(row, trip_col + 2, str(expense_method_id.display_name), main_heading)
                        if value['trip_type']:
                            sheet.write_string(row, trip_col + 3, str(value['trip_type']), main_heading)
                        if value['fvt_state']:
                            sheet.write_string(row, trip_col + 4, str(value['fvt_state']), main_heading)
                        if value['route_name']:
                            sheet.write_string(row, trip_col + 5, str(value['route_name']), main_heading)
                        if sale_line_count:
                            sheet.write_number(row, trip_col + 6, sale_line_count, main_heading)
                            tot_sale += sale_line_count
                        if vehicle_fuel_expenses:
                            sheet.write_number(row, trip_col + 7, float(vehicle_fuel_expenses), main_heading)
                            tot_exp += vehicle_fuel_expenses
                        if dis:
                            sheet.write_number(row, trip_col + 8,dis, main_heading)
                            tot_dis += dis
                        if v_revenue:
                            sheet.write_number(row, trip_col + 9,v_revenue, main_heading)
                            tot_rev += v_revenue
                        row+=1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_number(row, col + 10, tot_sale, main_heading2)
                    sheet.write_number(row, col + 11, tot_exp, main_heading2)
                    sheet.write_number(row, col + 12, tot_dis, main_heading2)
                    sheet.write_number(row, col + 13, tot_rev, main_heading2)
                    row += 1


class VehicleTruckRevenueReport(models.AbstractModel):
    _name = 'report.vehicle_revenue_report.vehicle_truck_revenue_temp_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        record_wizard = self.env[model].browse(self.env.context.get('active_id'))


        form = record_wizard.form
        to = record_wizard.to
        vehicle_id = record_wizard.vehicle_id
        # vehicle_id = self.env['bsg.vehicle.type.table'].browse([23, 24])
        driver_id = record_wizard.driver_id
        trip_type = record_wizard.trip_type
        report_type = record_wizard.report_type
        vehicle_type = self.env['bsg.vehicle.type.table'].browse([23, 24])
        head = "Vehicle Truck Revenue Report"

        report_type_num = 0
        report_type_name = " "


        driver_head = 0
        if len(driver_id) == 1:
            driver_head = 1

        veh_head = 0
        if len(vehicle_id) == 1:
            veh_head = 1


        report_num = 0
        if driver_head == 1 and veh_head == 0:
            report_num = 1
        if driver_head == 0 and veh_head == 1:
            report_num = 2
        if driver_head == 1 and veh_head == 1:
            report_num = 3

        all_fill = 0
        if not driver_id and not vehicle_id and not trip_type:
            all_fill = 1


        if vehicle_id and not vehicle_type:
            vehicles = []
            for v in vehicle_id:
                vehicles.append(v)

        if not vehicle_id and vehicle_type:
            vehicles = self.env['fleet.vehicle'].search([('vehicle_type.id','in',vehicle_type.ids)])
        if vehicle_id and vehicle_type:
            vehicles = []
            for v in vehicle_id:
                vehicles.append(v)
        if vehicle_id and vehicle_type:
            vehicles = []
            for v in vehicle_id:
                vehicles.append(v)


        if not vehicle_id and not vehicle_type:
            vehicles = []
            if not driver_id and not trip_type:
                trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel')])
            if driver_id and not trip_type:
                trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('driver_id.id','in',driver_id.ids)])
            if not driver_id and trip_type:
                trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type)])
            if driver_id and trip_type:
                trips_id = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type),('driver_id.id','in',driver_id.ids)])
            for j in trips_id:
                if j.vehicle_id not in vehicles:
                    vehicles.append(j.vehicle_id)

        main_data = []
        default_revenue = float(self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('bsg_trip_mgmt.local_trip_revenue'))
        local_revenue = default_revenue > 0 and default_revenue or 35
        if report_type == 'summary':

            report_type_num = 1
            report_type_name = "(Summary)"

            for tr in vehicles:

                if not driver_id and not trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('vehicle_id.id','=',tr.id)])
                if driver_id and not trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=','cancel'),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])
                if not driver_id and trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type),('vehicle_id.id','=',tr.id)])
                if driver_id and trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])

                if trips:
                    sale_line_count = 0
                    fuel_trip_amount = 0
                    dis = 0
                    v_revenue = 0
                    total_trip_count = 0
                    local_trips_count = 0
                    local_trips_revenue = 0
                    manual_trips_count = 0
                    manual_trips_revenue = 0
                    for rec in trips:
                        if not rec.stock_picking_id:
                            continue
                        total_trip_count+=1
                        fuel_trip_amount = fuel_trip_amount + rec.fuel_trip_amt
                        # dis = dis + (rec.trip_distance + rec.extra_distance)
                        so_lines = rec.stock_picking_id.filtered(lambda l: l.picking_name.state != 'cancel')
                        sale_line_count += len(so_lines)
                        t_dtstance = sum(rec.route_id.waypoint_to_ids.mapped('distance'))
                        dis += t_dtstance
                        t_trip_type = rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trip_type
                        if t_trip_type != 'local':
                            manual_trips_count += 1
                        else:
                            local_trips_count +=1
                        for so_line in so_lines:
                            drop_point = rec.route_id.waypoint_to_ids.filtered(lambda wl:wl.waypoint.id == so_line.picking_name.drop_loc.id)
                            sequence = 1
                            if drop_point:
                                sequence = drop_point[0].sequence
                            elif rec.route_id.waypoint_to_ids.mapped('sequence'):
                                 sequence = max(rec.route_id.waypoint_to_ids.mapped('sequence'))
                            trip_distance = sum(rec.route_id.waypoint_to_ids.filtered(lambda wyl:wyl.sequence <= sequence).mapped('distance'))
                            earned_revenue = 0
                            # branchRecord = self.env['branch.distance'].search([('branch_from','=',so_line.picking_name.pickup_loc.id),('branch_to','=',so_line.picking_name.drop_loc.id)], limit=1)
                            # trip_distance = branchRecord.distance
                            # if not trip_distance:
                                # trip_distance = 1
                            # history_lines =  ch.picking_name.trip_history_ids.filtered(lambda hl: hl.fleet_trip_id.id == rec.id)
                            # if history_lines:
                            if t_trip_type != 'local':
                                earned_revenue = (trip_distance * so_line.picking_name.total_without_tax) / (t_dtstance or 1)
                                manual_trips_revenue += earned_revenue
                            else:
                                other_service = self.env['other_service_items'].search([('cargo_sale_line_id', '=', so_line.id)], limit=1)
                                earned_revenue = other_service and sum(other_service.mapped('cost')) or float(local_revenue)
                                local_trips_revenue += earned_revenue
                            v_revenue += earned_revenue




                            # pickings = rec.stock_picking_id.filtered(lambda pick: pick.state != 'cancel')
                            # for ch in pickings:
                            # 	history_lines =  ch.picking_name.trip_history_ids.filtered(lambda hl: hl.fleet_trip_id.id == rec.id)
                            # 	if history_lines:
                            # 		for th in history_lines:
                            # 			if th.fleet_trip_id.trip_type != 'local':
                            # 				trip_distance = 1
                            # 				branchRecord = self.env['branch.distance'].search([('branch_from','=',ch.pickup_loc.id),('branch_to','=',ch.drop_loc.id)], limit=1)
                            # 				if branchRecord:
                            # 					trip_distance = branchRecord.distance
                            # 				earned_revenue = (trip_distance * th.cargo_sale_line_id.total_without_tax) / (dis or 1)
                            # 			else:
                            # 				earned_revenue = float(local_revenue)
                            # 			v_revenue += earned_revenue
                                # for his in ch.picking_name.trip_history_ids:
                                # 	v_revenue = v_revenue + his.earned_revenue


                    main_data.append({
                        'v_code':tr.taq_number,
                        'driver':tr.bsg_driver.name,
                        'driver_code':tr.bsg_driver.driver_code,
                        'tr_num':total_trip_count,
                        'local_trips_count': local_trips_count,
                        'local_trips_revenue': round(local_trips_revenue),
                        'manual_trips_count': manual_trips_count,
                        'manual_trips_revenue': round(manual_trips_revenue),
                        'tr_sale_lines':sale_line_count,
                        'fuel_exp': fuel_trip_amount,
                        'dis': dis,
                        'v_revenue':round(v_revenue),
                        })

        if report_type == 'detail':

            report_type_name = "(Detail)"

            report_type_num = 2

            for tr in vehicles:

                if not driver_id and not trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('vehicle_id.id','=',tr.id)])
                if driver_id and not trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])
                if not driver_id and trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type),('vehicle_id.id','=',tr.id)])
                if driver_id and trip_type:
                    trips = self.env['fleet.vehicle.trip'].search([('expected_start_date','>=',form),('expected_start_date','<=',to),('state','!=', 'cancel'),('trip_type','=',trip_type),('driver_id.id','in',driver_id.ids),('vehicle_id.id','=',tr.id)])

                if trips:
                    trip_data = []
                    dis = 0
                    for rec in trips:
                        if not rec.stock_picking_id:
                            continue
                        sale_line_count = 0
                        so_lines = rec.stock_picking_id.filtered(lambda l: l.picking_name.state != 'cancel')
                        sale_line_count = len(so_lines)
                        if sale_line_count == 0:
                            continue
                        t_dtstance = sum(rec.route_id.waypoint_to_ids.mapped('distance'))
                        dis += t_dtstance
                        v_revenue = 0
                        t_trip_type = rec.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).trip_type
                        for so_line in so_lines:
                            drop_point = rec.route_id.waypoint_to_ids.filtered(lambda wl:wl.waypoint.id == so_line.picking_name.drop_loc.id)
                            if drop_point:
                                sequence = drop_point[0].sequence
                            elif rec.route_id.waypoint_to_ids.mapped('sequence'):
                                 sequence = max(rec.route_id.waypoint_to_ids.mapped('sequence'))
                            trip_distance = sum(rec.route_id.waypoint_to_ids.filtered(lambda wyl:wyl.sequence <= sequence).mapped('distance'))
                            earned_revenue = 0
                            # branchRecord = self.env['branch.distance'].search([('branch_from','=',so_line.picking_name.pickup_loc.id),('branch_to','=',so_line.picking_name.drop_loc.id)], limit=1)
                            # trip_distance = branchRecord.distance
                            # if not trip_distance:
                                # trip_distance = 1
                            # history_lines =  ch.picking_name.trip_history_ids.filtered(lambda hl: hl.fleet_trip_id.id == rec.id)
                            # if history_lines:
                            if t_trip_type != 'local':
                                earned_revenue = (trip_distance * so_line.picking_name.total_without_tax) / (t_dtstance or 1)
                            else:
                                earned_revenue = float(local_revenue)
                            v_revenue += earned_revenue

                            # for th in history_lines:
                            # 	if th.trip_type != 'local':
                            # 		earned_revenue = (th.trip_distance * th.cargo_sale_line_id.total_without_tax) / (dis or 1)
                            # 	else:
                            # 		earned_revenue = float(local_revenue)
                            # 	v_revenue += earned_revenue
                            # for his in ch.picking_name.trip_history_ids:
                            # 	v_revenue = v_revenue + his.earned_revenue

                        trip_data.append({
                            'trip_num':rec.name,
                            'route':rec.route_id.route_name,
                            'tr_sale_lines':sale_line_count,
                            'fuel_exp': rec.fuel_trip_amt,
                            'dis': t_dtstance,
                            'v_revenue':v_revenue,
                            'state': rec.state,
                            'trip_type': rec.trip_type,
                            'vehicle_type': rec.vehicle_id.vehicle_type.vehicle_type_name
                            })


                    main_data.append({
                        'v_code':tr.taq_number,
                        'driver':tr.bsg_driver.name,
                        'driver_code':tr.bsg_driver.driver_code,
                        'trip_data':trip_data,
                        })





        return {
            'doc_ids': docids,
            'doc_model':'fleet.vehicle.trip',
            'form': form,
            'to': to,
            'head': head,
            'vehicle_id': vehicle_id,
            'driver_id': driver_id,
            'trip_type': trip_type,
            'main_data': main_data,
            'report_num': report_num,
            'driver_head': driver_head,
            'veh_head': veh_head,
            'all_fill': all_fill,
            'report_type_num': report_type_num,
            'report_type_name': report_type_name,

        }
