from odoo import models
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
import math
from pytz import timezone,UTC


class TripsReportExcel(models.AbstractModel):
    _name = 'report.bsg_trips_reports.trips_report_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        wiz_id = self.env[model].browse(self.env.context.get('active_id'))
        tz = timezone(self.env.context.get('tz') or self.env.user.tz)
        form_tz = UTC.localize(wiz_id.form).astimezone(tz).replace(tzinfo=None)
        to_tz = UTC.localize(wiz_id.to).astimezone(tz).replace(tzinfo=None)
        # domain = [('expected_start_date', '>=', form_tz), ('expected_start_date', '<=', to_tz)]
        # if wiz_id.vehicle_type:
        #     domain.append(('vehicle_id.vehicle_type', 'in', wiz_id.vehicle_type.ids))

        from_str = str(form_tz)
        to_str = str(to_tz)
        date_condition = f"fvt_table.expected_start_date > '{from_str}' and fvt_table.expected_start_date < '{to_str}'"

        # if wiz_id.trip_type:
        #     domain.append(('trip_type', '=', wiz_id.trip_type))

        trip_type_cond = ""
        if wiz_id.trip_type:
            trip_type = wiz_id.trip_type
            trip_type_cond = f"and fvt_table.trip_type = '{trip_type}'"

        # if wiz_id.branch_from:
        #     domain.append(('start_branch', 'in', wiz_id.branch_from.ids))

        branch_from_cond = ""
        if wiz_id.branch_from:
            branch_from_ids = wiz_id.branch_from.ids
            branch_from_ids_str = len(branch_from_ids) == 1 and "(%s)" % branch_from_ids[0] or str(tuple(branch_from_ids))
            branch_from_cond = f"and fvt_table.start_branch in {branch_from_ids_str}"

        # if wiz_id.branch_to:
        #     domain.append(('end_branch', 'in', wiz_id.branch_to.ids))

        branch_to_cond = ""
        if wiz_id.branch_to:
            branch_to_ids = wiz_id.branch_to.ids
            branch_to_ids_str = len(branch_to_ids) == 1 and "(%s)" % branch_to_ids[0] or str(tuple(branch_to_ids))
            branch_to_cond = f"and fvt_table.start_branch in {branch_to_ids_str}"

        # if wiz_id.trip_status:
        #     domain.append(('state', '=', wiz_id.trip_status))

        trip_status_cond = ""
        if wiz_id.trip_status:
            trip_status = wiz_id.trip_status
            trip_status_cond = f"and fvt_table.state = '{trip_status}'"


        # if wiz_id.vehicle_group_id:
        #     domain.append(('vehicle_id.vehicle_group_name', '=', wiz_id.vehicle_group_id.id))

        vehicle_group_id_cond = ""
        if wiz_id.vehicle_group_id:
            vehicle_group_id = wiz_id.vehicle_group_id.id
            vehicle_group_id_cond = f"and vehicle.vehicle_group_name = '{vehicle_group_id}'"


        # if wiz_id.truck_load == 'empty':
        #     domain.append(('total_cars', '=', 0))

        empty_truck_load_cond = ""
        if wiz_id.truck_load == 'empty':
            empty_tuck_load_cond = f"and fvt_table.total_cars = 0"

        # if wiz_id.truck_load == 'full':
        #     domain.append(('total_cars', '!=', 0))

        full_truck_load_cond = ""
        if wiz_id.truck_load == 'full':
            full_truck_load_cond = f"and fvt_table.total_cars != 0"

        # if wiz_id.user_id:
        #     domain.append(('create_uid', '=', wiz_id.user_id.id))

        create_uid_cond = ""
        if wiz_id.user_id:
            user_id = wiz_id.user_id.id
            create_uid_cond = f"and fvt_table.create_uid = '{user_id}'"

        # trip_ids = self.env['fleet.vehicle.trip'].search(domain)
        # print('...................trip_ids length..............',len(trip_ids))

        table_name = "fleet_vehicle_trip as fvt_table"
        self.env.cr.execute(
            "select fvt_table.id as fvt_id,fvt_table.name as fvt_name,fvt_table.vehicle_id as vehicle_id\
            ,vehicle.vehicle_type as vehicle_type_id,fvt_table.expected_start_date as fvt_expected_start_date\
            ,fvt_table.additional_fuel_exp as fvt_additional_fuel_exp,partner.name as create_user_name\
            ,fvt_table.trip_type as fvt_trip_type,fvt_table.state as fvt_state,vehicle.taq_number as vehicle_taq_number\
            ,driver.driver_code as driver_code,driver.name as driver_name,vehicle_type.vehicle_type_name as vehicle_type_name\
            ,start_waypoint.route_waypoint_name as start_branch_name,end_waypoint.route_waypoint_name as end_branch_name\
            ,route.route_name as route_name,fvt_table.expected_end_date as fvt_expected_end_date\
            ,fvt_table.actual_start_datetime as fvt_actual_start_datetime,fvt_table.actual_end_datetime as fvt_actual_end_datetime\
            ,write_partner.name as write_user_name,fvt_table.total_cars as fvt_total_cars,fvt_table.trip_distance as fvt_trip_distance\
            ,fvt_table.extra_distance as fvt_extra_distance,fvt_table.total_fuel_amount as fvt_total_fuel_amount\
            ,fvt_table.total_reward_amount as fvt_tot_reward_amt_frontend,fvt_table.additional_fuel_exp as fvt_add_reward_amt_frontend\
            ,fvt_table.is_done_fuel as fvt_is_done_fuel,fvt_table.description as fvt_description\
            ,fvt_table.total_on_transit_cars as fvt_total_on_transit_cars FROM " + table_name + \
            " LEFT JOIN fleet_vehicle vehicle ON fvt_table.vehicle_id=vehicle.id"
            " LEFT JOIN res_users user_id ON fvt_table.create_uid=user_id.id"
            " LEFT JOIN res_partner partner ON user_id.partner_id=partner.id"
             " LEFT JOIN res_users write_user_id ON fvt_table.write_uid=write_user_id.id"
            " LEFT JOIN res_partner write_partner ON write_user_id.partner_id=write_partner.id"
            " LEFT JOIN hr_employee driver ON fvt_table.driver_id=driver.id"
            " LEFT JOIN bsg_vehicle_type_table vehicle_type ON vehicle.vehicle_type=vehicle_type.id"
            " LEFT JOIN bsg_route_waypoints start_waypoint ON fvt_table.start_branch=start_waypoint.id"
            " LEFT JOIN bsg_route_waypoints end_waypoint ON fvt_table.end_branch=end_waypoint.id"
            " LEFT JOIN bsg_route route ON fvt_table.route_id=route.id"
            " WHERE %s %s %s %s %s %s %s %s %s order by fvt_table.vehicle_id " % (
                date_condition,trip_type_cond,branch_from_cond,branch_to_cond,trip_status_cond,vehicle_group_id_cond,empty_truck_load_cond,full_truck_load_cond,create_uid_cond))

        result = self._cr.fetchall()
        all_trips = pd.DataFrame(list(result))
        # fvt_table.total_on_transit_cars
        all_trips = all_trips.rename(
            columns={0: 'fvt_id',1: 'fvt_name', 2: 'vehicle_id', 3: 'vehicle_type_id', 4: 'fvt_expected_start_date',
                     5:'fvt_additional_fuel_exp',6:'create_user_name',7:'fvt_trip_type',8:'fvt_state',9:'vehicle_taq_number',
                     10:'driver_code',11:'driver_name',12:'vehicle_type_name',13:'start_branch_name',14:'end_branch_name',
                     15:'route_name',16:'fvt_expected_end_date',17:'fvt_actual_start_datetime',18:'fvt_actual_end_datetime',
                     19:'write_user_name',20:'fvt_total_cars',21:'fvt_trip_distance',22:'fvt_extra_distance',
                     23:'fvt_total_fuel_amount',24:'fvt_tot_reward_amt_frontend',25:'fvt_add_reward_amt_frontend',26:'fvt_is_done_fuel',
                     27:'fvt_description', 28: 'fvt_total_on_transit_cars'})

        print('vehicle_trips...............', all_trips)
        # print('vehicle_trips...............', all_trips['create_user_name'])
        # grouped_all_trips = all_trips.groupby(['vehicle_id', 'fuel_exp_method_id'])
        #
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
        sheet = workbook.add_worksheet('Vehicle Drivers Reports')
        sheet.set_column('A:Q',15)
        row = 0
        col = 0
        self.env.ref('bsg_trips_reports.trips_reports_xlsx_id').report_file = "Trips Report Xlsx"
        sheet.merge_range('A1:Q1', 'تقرير الرحلات', main_heading3)
        row += 1
        sheet.merge_range('A2:Q2', 'Trips Report', main_heading3)
        row += 2
        sheet.write(row, col, 'Print By', main_heading2)
        sheet.write_string(row, col+1, str(self.env.user.display_name), main_heading)
        sheet.write(row, col+2, 'طباعة بواسطة', main_heading2)
        sheet.write(row, col+4, 'Print Date', main_heading2)
        sheet.write_string(row, col+5, str(date.today()), main_heading)
        sheet.write(row, col+6, 'تاريخ الطباعة', main_heading2)
        sheet.write(row, col+8, 'Vehicle Type', main_heading2)
        if wiz_id.vehicle_type:
            rec_names = wiz_id.vehicle_type.mapped('display_name')
            names = ','.join(rec_names)
            sheet.write_string(row, col+9, str(names), main_heading)
        sheet.write(row, col+10, 'نوع الشاحنة', main_heading2)
        row += 1
        sheet.write(row, col, 'From Date', main_heading2)
        sheet.write_string(row, col + 1, str(wiz_id.form), main_heading)
        sheet.write(row, col + 2, 'من التاريخ', main_heading2)
        sheet.write(row, col + 4, 'To Date', main_heading2)
        sheet.write_string(row, col + 5, str(wiz_id.to), main_heading)
        sheet.write(row, col + 6, 'حتي اليوم', main_heading2)
        row += 1
        sheet.write(row, col, 'Branch From', main_heading2)
        if wiz_id.branch_from:
            branch_from_rec_names = wiz_id.branch_from.mapped('display_name')
            branch_from_names = ','.join(branch_from_rec_names)
            sheet.write_string(row, col + 1, str(branch_from_names), main_heading)
        sheet.write(row, col + 2, 'من الفرع', main_heading2)
        sheet.write(row, col + 4, 'Branch To', main_heading2)
        if wiz_id.branch_to:
            branch_to_rec_names = wiz_id.branch_to.mapped('display_name')
            branch_to_names = ','.join(branch_to_rec_names)
            sheet.write_string(row, col + 5, str(branch_to_names), main_heading)
        sheet.write(row, col + 6, 'لفرع', main_heading2)
        row += 1
        sheet.write(row, col, 'Trip Refence', main_heading2)
        sheet.write(row, col+1, 'Scheduled Start Date', main_heading2)
        sheet.write(row, col+2, 'Employee Name', main_heading2)
        sheet.write(row, col+3, 'Trip Type', main_heading2)
        sheet.write(row, col+4, 'Trip Status', main_heading2)
        sheet.write(row, col+5, 'Vehicle', main_heading2)
        sheet.write(row, col+6, 'Driver Code', main_heading2)
        sheet.write(row, col+7, 'Driver', main_heading2)
        sheet.write(row, col+8, 'Vehicle Type', main_heading2)
        sheet.write(row, col+9, 'Start Branch', main_heading2)
        sheet.write(row, col+10 , 'End Branch', main_heading2)
        sheet.write(row, col+11, 'Route', main_heading2)
        sheet.write(row, col+12, 'Scheduled End Date', main_heading2)
        sheet.write(row, col+13, 'Actual Start Date', main_heading2)
        sheet.write(row, col+14, 'Actual End Date', main_heading2)
        sheet.write(row, col+15, 'Employee Registering Trip Arrival', main_heading2)
        sheet.write(row, col+16, 'Truck Load', main_heading2)
        sheet.write(row, col+17, 'Car Load', main_heading2)
        sheet.write(row, col+18, 'Transit Branch Number', main_heading2)
        sheet.write(row, col+19, 'Trip Distance', main_heading2)
        sheet.write(row, col+20, 'Extra Distance', main_heading2)
        sheet.write(row, col+21, 'Description', main_heading2)
        sheet.write(row, col+22, 'Total Distance', main_heading2)
        sheet.write(row, col+23, 'Total Fuel Expense', main_heading2)
        sheet.write(row, col+24, 'Total Reward Amount', main_heading2)
        sheet.write(row, col+25, 'Additional Reward Amount', main_heading2)
        sheet.write(row, col+26, 'Fuel Voucher', main_heading2)
        sheet.write(row, col+27, 'Payment Amount', main_heading2)
        # sheet.write(row, col+28, 'Earned Revenue', main_heading2)
        row += 1
        sheet.write(row, col, 'رقم الرحلة', main_heading2)
        sheet.write(row, col + 1, 'تاريخ بدء المجدولة', main_heading2)
        sheet.write(row, col + 2, 'اسم الموظف', main_heading2)
        sheet.write(row, col + 3, 'نوع الرحلة', main_heading2)
        sheet.write(row, col + 4, 'حالة الرحلة', main_heading2)
        sheet.write(row, col + 5, 'رقم الشاحنة', main_heading2)
        sheet.write(row, col + 6, 'رقم السائق', main_heading2)
        sheet.write(row, col + 7, 'اسم السائق', main_heading2)
        sheet.write(row, col + 8, 'نوع الشاحنة', main_heading2)
        sheet.write(row, col + 9, 'فرع الانطلاق', main_heading2)
        sheet.write(row, col + 10, 'فرع الوصول', main_heading2)
        sheet.write(row, col + 11, 'خط السير', main_heading2)
        sheet.write(row, col + 12, 'تاريخ انتهاء المجدولة ', main_heading2)
        sheet.write(row, col + 13, 'تاريخ الانطلاق الفعلى ', main_heading2)
        sheet.write(row, col + 14, 'تاريخ الانتهاء الفعلى ', main_heading2)
        sheet.write(row, col + 15, 'اسم مسجل اخر وصول', main_heading2)
        sheet.write(row, col + 16, 'حمولة الشاحنة', main_heading2)
        sheet.write(row, col + 17, 'عدد السيارات', main_heading2)
        sheet.write(row, col + 18, 'عدد فروع الترانزيت ', main_heading2)
        sheet.write(row, col + 19, 'مسافة الرحلة ', main_heading2)
        sheet.write(row, col + 20, 'المسافة الاضافية ', main_heading2)
        sheet.write(row, col + 21, 'الشرح', main_heading2)
        sheet.write(row, col + 22, 'مجموع المسافة ', main_heading2)
        sheet.write(row, col + 23, 'قيمة المصروف', main_heading2)
        sheet.write(row, col + 24, 'قيمة مكافاة الحمولة ', main_heading2)
        sheet.write(row, col + 25, 'قيمة مكافاة الحمولة الاضافية ', main_heading2)
        sheet.write(row, col + 26, 'رقم سند الصرف', main_heading2)
        sheet.write(row, col + 27, 'قيمة سند الصرف', main_heading2)
        # sheet.write(row, col + 28, 'حافز السائق', main_heading2)
        row += 1
        total_transit_branch_no = 0
        total_trip_distance = 0
        total_extra_distance = 0
        total_fuel_expense = 0
        total_reward_amount = 0
        total_additional_reward_amount = 0
        total_payment_amount = 0
        total_earned_revenue = 0

        for key,trip in all_trips.iterrows():
            earned_revenue = 0
            total_distance = trip['fvt_trip_distance'] + trip['fvt_extra_distance']
            # payment_id = self.env['account.payment'].search(
            #     [('is_pay_trip_money', '=', True), ('fleet_trip_id', '=', trip.id), ('state', '!=', 'reversal_entry')],limit=1)
            # so_line_id = self.env['bsg_vehicle_cargo_sale_line'].search([('fleet_trip_id', '=', trip.id)],limit=1)
            # if so_line_id.trip_history_ids:
            #     earned_revenue = sum(so_line_id.trip_history_ids.mapped('earned_revenue'))
            payment_amount = float(trip['fvt_total_fuel_amount']) +float(trip['fvt_tot_reward_amt_frontend']) + float(trip['fvt_add_reward_amt_frontend'])
            if trip['fvt_name']:
                sheet.write_string(row, col,str(trip['fvt_name']), main_heading)
            if trip['fvt_expected_start_date']:
                sheet.write_string(row, col + 1,str(trip['fvt_expected_start_date']), main_heading)
            if trip['create_user_name']:
                sheet.write_string(row, col + 2, str(trip['create_user_name']), main_heading)
            if trip['fvt_trip_type']:
                sheet.write_string(row, col + 3, str(trip['fvt_trip_type']), main_heading)
            if trip['fvt_state']:
                sheet.write_string(row, col + 4,str(trip['fvt_state']), main_heading)
            if trip['vehicle_taq_number']:
                sheet.write_string(row, col + 5,str(trip['vehicle_taq_number']), main_heading)
            if trip['driver_code']:
                sheet.write_string(row, col + 6,str(trip['driver_code']), main_heading)
            if trip['driver_name']:
                sheet.write_string(row, col + 7, str(trip['driver_name']), main_heading)
            if trip['vehicle_type_name']:
                sheet.write_string(row, col + 8,str(trip['vehicle_type_name']), main_heading)
            if trip['start_branch_name']:
                sheet.write_string(row, col + 9,str(trip['start_branch_name']), main_heading)
            if trip['end_branch_name']:
                sheet.write_string(row, col + 10, str(trip['end_branch_name']), main_heading)
            if trip['route_name']:
                sheet.write_string(row, col + 11,str(trip['route_name']), main_heading)
            if trip['fvt_expected_end_date']:
                sheet.write_string(row, col + 12,str(trip['fvt_expected_end_date']), main_heading)
            if trip['fvt_actual_start_datetime']:
                sheet.write_string(row, col + 13,str(trip['fvt_actual_start_datetime']), main_heading)
            if trip['fvt_actual_end_datetime']:
                sheet.write_string(row, col + 14,str(trip['fvt_actual_end_datetime']), main_heading)
            if trip['write_user_name']:
                sheet.write_string(row, col + 15,str(trip['write_user_name']), main_heading)
            if int(trip['fvt_total_cars']) == 0:
                sheet.write_string(row, col + 16,str('Empty'), main_heading)
            if int(trip['fvt_total_cars']) != 0:
                sheet.write_string(row, col + 16,str('Full'), main_heading)
            if trip['fvt_total_cars']:
                sheet.write_string(row, col + 17,str(trip['fvt_total_cars']), main_heading)
                # sheet.write_string(row, col + 17,str(trip.total_cars - len(trip.stock_picking_id.filtered(lambda l:l.is_package==True))), main_heading)
            if trip['fvt_total_on_transit_cars']:
                # route_names = trip.route_id.route_name.split('-')
                # transit_branch_no = len(route_names) - 1
                # print('.............route_names....................', route_names)
                transit_branch_no = trip['fvt_total_on_transit_cars']
                sheet.write_number(row, col + 18, float(transit_branch_no), main_heading)
                total_transit_branch_no += float(transit_branch_no)
            if trip['fvt_trip_distance']:
                sheet.write_number(row, col + 19,float(trip['fvt_trip_distance']), main_heading)
                total_trip_distance += float(trip['fvt_trip_distance'])
            if trip['fvt_extra_distance']:
                sheet.write_number(row, col + 20,float(trip['fvt_extra_distance']), main_heading)
                total_extra_distance += float(trip['fvt_extra_distance'])
            if trip['fvt_description']:
                sheet.write_string(row, col + 21, str(trip['fvt_description']), main_heading)
            if total_distance:
                sheet.write_string(row, col + 22, str(total_distance), main_heading)
            if trip['fvt_total_fuel_amount']:
                sheet.write_number(row, col + 23, float(trip['fvt_total_fuel_amount']), main_heading)
                total_fuel_expense += float(trip['fvt_total_fuel_amount'])
            if trip['fvt_tot_reward_amt_frontend']:
                sheet.write_number(row, col + 24, float(trip['fvt_tot_reward_amt_frontend']), main_heading)
                total_reward_amount += float(trip['fvt_tot_reward_amt_frontend'])
            if trip['fvt_add_reward_amt_frontend']:
                sheet.write_number(row, col + 25, float(trip['fvt_add_reward_amt_frontend']), main_heading)
                total_additional_reward_amount += float(trip['fvt_add_reward_amt_frontend'])
            if trip['fvt_is_done_fuel']:
                sheet.write_string(row, col + 26, str("True"), main_heading)
            if not trip['fvt_is_done_fuel']:
                sheet.write_string(row, col + 26, str("False"), main_heading)
            if payment_amount:
                sheet.write_number(row, col + 27,payment_amount , main_heading)
                total_payment_amount += payment_amount

            # if earned_revenue:
            #     sheet.write_number(row, col + 28, float(earned_revenue), main_heading)
            #     total_earned_revenue += float(earned_revenue)
            row+=1
        sheet.write(row, col, 'Total', main_heading2)
        sheet.write_number(row, col + 18, float(total_transit_branch_no), main_heading)
        sheet.write_number(row, col + 19, float(total_trip_distance), main_heading)
        sheet.write_number(row, col + 20, float(total_extra_distance), main_heading)
        sheet.write_number(row, col + 23, float(total_fuel_expense), main_heading)
        sheet.write_number(row, col + 24, float(total_reward_amount), main_heading)
        sheet.write_number(row, col + 25, float(total_additional_reward_amount), main_heading)
        sheet.write_number(row, col + 27, float(total_payment_amount), main_heading)
        # sheet.write_number(row, col + 28, float(total_earned_revenue), main_heading)
