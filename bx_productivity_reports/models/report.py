import os
import xlsxwriter
from datetime import date
from datetime import date, timedelta
import datetime
import time
import re
import pandas as pd
import numpy as np
import psycopg2 as pg
import pandas.io.sql as psql
import getpass
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import string


class BxpProductivityReportXlsx(models.TransientModel):
    _name = 'report.bx_productivity_reports.bx_productivity_reports_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_sum(self,bsg_driver_id, transport_lines):
        all_data = transport_lines.loc[(transport_lines['bsg_driver']) == bsg_driver_id]

        all_data = all_data.groupby(['bsg_driver'], as_index=False).sum()
        data_dict = {}
        for index, line in all_data.iterrows():
            data_dict['all_amt'] = line['total_before_taxes']
            data_dict['all_numz'] = line['counter']
            data_dict['distance_trip'] = line['trip_distance']
            data_dict['ex_distance'] = line['extra_distance']
            data_dict['tot_distance'] = line['total_distance']
            data_dict['tot_fuel_amount'] = line['total_fuel_amount']
            data_dict['tot_reward_amount'] = line['total_reward_amount']
            data_dict['tot_amount'] = line['total_amount']
        return data_dict
    def get_sum_by_user(self,user_name_id, transport_lines):
        all_data = transport_lines.loc[(transport_lines['create_uid']) == user_name_id]

        all_data = all_data.groupby(['create_uid'], as_index=False).sum()
        data_dict = {}
        for index, line in all_data.iterrows():
            data_dict['total_before_taxes'] = line['total_before_taxes']
            data_dict['counter']  = line['counter']
            data_dict['trip_distance']  = line['trip_distance']
            data_dict['extra_distance']  = line['extra_distance']
            data_dict['total_distance']  = line['total_distance']
            data_dict['total_fuel_amount']  = line['total_fuel_amount']
            data_dict['total_reward_amount']  = line['total_reward_amount']
            data_dict['total_amount']  = line['total_amount']

        return data_dict

    # @api.multi
    def generate_xlsx_report(self, workbook, input_records, lines):
        data = input_records['form']

        table_name = "transport_management"
        self.env.cr.execute(
            "select id,order_date,payment_method,state,total_amount,form_transport,to_transport,create_uid,customer,"
            "transportation_no,total_before_taxes,tax_amount,"
            "total_distance,transportation_vehicle,driver_number,total_fuel_amount,total_reward_amount,transportation_driver,trip_distance,extra_distance,driver,route_id,fleet_type_transport,loading_date FROM " + table_name + " ")
        result = self._cr.fetchall()
        transport_lines = pd.DataFrame(list(result))
        transport_lines = transport_lines.rename(
            columns={0: 'self_id', 1: 'order_date', 2: 'payment_method', 3: 'state', 4: 'total_amount',
                     5: 'form_transport', 6: 'to_transport', 7: 'create_uid', 8: 'customer', 9: 'transportation_no',
                     10: 'total_before_taxes', 11: 'tax_amount',12:'total_distance', 13:'transportation_vehicle',
                     14:'driver_number', 15:'total_fuel_amount', 16:'total_reward_amount',
                     17:'transportation_driver', 18:'trip_distance', 19:'extra_distance', 20:'driver', 21:'route_id', 22:'fleet_type_transport', 23:'loading_date'})

        bsg_customer_table = "res_partner"
        self.env.cr.execute("select id,name FROM " + bsg_customer_table + " ")
        result_bsg_customer = self._cr.fetchall()
        bsg_customer_frame = pd.DataFrame(list(result_bsg_customer))
        bsg_customer_frame = bsg_customer_frame.rename(columns={0: 'bsg_customer_id', 1: 'bsg_customer_name'})
        transport_lines = pd.merge(transport_lines, bsg_customer_frame, how='left', left_on='customer',
                                   right_on='bsg_customer_id')

        payment_frame_table = "cargo_payment_method"
        self.env.cr.execute("select id,payment_method_name FROM " + payment_frame_table + " ")
        result_payment_frame = self._cr.fetchall()
        payment_frame = pd.DataFrame(list(result_payment_frame))
        payment_frame = payment_frame.rename(columns={0: 'bsg_pay_method_id', 1: 'bsg_pay_method_name'})
        transport_lines = pd.merge(transport_lines, payment_frame, how='left', left_on='payment_method',
                                   right_on='bsg_pay_method_id')

        loc_from_frame_table = "bsg_route_waypoints"
        self.env.cr.execute("select id,route_waypoint_name FROM " + loc_from_frame_table + " ")
        result_loc_from_frame = self._cr.fetchall()
        loc_from_frame = pd.DataFrame(list(result_loc_from_frame))
        loc_from_frame = loc_from_frame.rename(columns={0: 'bsg_loc_from_id', 1: 'bsg_loc_from_name'})
        transport_lines = pd.merge(transport_lines, loc_from_frame, how='left', left_on='form_transport',
                                   right_on='bsg_loc_from_id')

        loc_to_frame_table = "bsg_route_waypoints"
        self.env.cr.execute("select id,route_waypoint_name FROM " + loc_to_frame_table + " ")
        result_loc_to_frame = self._cr.fetchall()
        loc_to_frame = pd.DataFrame(list(result_loc_to_frame))
        loc_to_frame = loc_to_frame.rename(columns={0: 'bsg_loc_to_id', 1: 'bsg_loc_to_name'})
        transport_lines = pd.merge(transport_lines, loc_to_frame, how='left', left_on='to_transport',
                                   right_on='bsg_loc_to_id')

        fleet_vehicle_table = "fleet_vehicle"
        self.env.cr.execute("select bsg_driver,vehicle_type,vehicle_status,taq_number FROM " + fleet_vehicle_table + " ")
        result_fleet_vehicle = self._cr.fetchall()
        fleet_vehicle_frame = pd.DataFrame(list(result_fleet_vehicle))
        fleet_vehicle_frame = fleet_vehicle_frame.rename(columns={0: 'bsg_driver', 1: 'vehicle_type', 2: 'vehicle_status', 3: 'taq_number'})
        transport_lines = pd.merge(transport_lines, fleet_vehicle_frame, how='left', left_on='driver',
                                   right_on='bsg_driver')

        transport_lines = transport_lines.loc[(transport_lines['state'] != 'cancel')]
        transport_lines = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher', 'receive_pod', 'done']))]

        if data['state']:
            transport_lines = transport_lines.loc[(transport_lines['state'] == data['state'])]



        if data['customer_ids']:
            transport_lines = transport_lines.loc[(transport_lines['customer'].isin(data['customer_ids']))]

        if data['branch_ids']:
            branch_ids = []
            for x in data['branch_ids']:
                way_points = self.env['bsg_route_waypoints'].search([('loc_branch_id.id', '=', x)], limit=1)
                if way_points:
                    branch_ids.append(way_points.id)

            transport_lines = transport_lines.loc[(transport_lines['form_transport'].isin(branch_ids))]

        if data['branch_ids_to']:
            transport_lines = transport_lines.loc[(transport_lines['to_transport'].isin(data['branch_ids_to']))]

        if data['users']:
            transport_lines = transport_lines.loc[(transport_lines['create_uid'].isin(data['users']))]


        transport_lines['loading_date'] = transport_lines['order_date'].astype(str)
        transport_lines['arrival_date'] = transport_lines['order_date'].astype(str)
        transport_lines['date'] = transport_lines['order_date'].astype(str)
        transport_lines['counter'] = 1
        if data['fleet_type_transport']:
            transport_lines = transport_lines.loc[(transport_lines['fleet_type_transport'] == (data['fleet_type_transport']))]
        if data['truck_load']:
            transport_lines = transport_lines.loc[(transport_lines['truck_load'] == (data['truck_load']))]
        if data['truck_load']:
            transport_lines = transport_lines.loc[(transport_lines['truck_load'] == (data['truck_load']))]
        if data['date_type'] == "is equal to":
            transport_lines = transport_lines.loc[(transport_lines['date'] == (data['date']))]
        if data['date_type'] == "is not equal to":
            transport_lines = transport_lines.loc[(transport_lines['date'] != data['date'])]
        if data['date_type'] == "is after":
            transport_lines = transport_lines.loc[(transport_lines['date'] > data['date'])]
        if data['date_type'] == "is before":
            transport_lines = transport_lines.loc[(transport_lines['date'] < data['date'])]
        if data['date_type'] == "is after or equal to":
            transport_lines = transport_lines.loc[(transport_lines['date'] >= data['date'])]
        if data['date_type'] == "is before or equal to":
            transport_lines = transport_lines.loc[(transport_lines['date'] <= data['date'])]
        if data['date_type'] == "is between":
            transport_lines = transport_lines.loc[
                (transport_lines['date'] >= data['form']) & (transport_lines['date'] <= data['to'])]
        if data['date_type'] == "is set":
            transport_lines = transport_lines.loc[(transport_lines.order_date.notnull())]
        if data['date_type'] == "is not set":
            transport_lines = transport_lines.loc[(transport_lines.order_date.isnull())]

        main_heading = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'center',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
        })

        main_heading1 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
        })

        main_heading2 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'right',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '10',
        })

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': '13',
            "font_color": 'black',
            'bg_color': '#D3D3D3'})

        main_data = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            'font_size': '8',
        })
        merge_format.set_shrink()
        main_heading.set_text_justlast(1)
        main_data.set_border()
        worksheet = workbook.add_worksheet('Bx Productivity Report')

        letters = list(string.ascii_uppercase)

        if not data['report_mode']:

            worksheet.merge_range('A1:N1', "Bx Vehicle productivity Summery Report", merge_format)
            worksheet.merge_range('A2:N2', "تقرير تفصيلي انتاجيه شاحنات نقل البضائع", merge_format)

            unique_bx = transport_lines.taq_number.unique()

            worksheet.write('A4', 'استيكر الشاحنة', main_heading1)
            worksheet.write('B4', 'نوع الشاحنة', main_heading1)
            worksheet.write('C4', 'حالة الشاحنة', main_heading1)
            worksheet.write('D4', 'كود السائق', main_heading1)
            worksheet.write('E4', 'اسم السائق', main_heading1)
            worksheet.write('F4', 'عدد اتفاقيات', main_heading1)
            worksheet.write('G4', 'قيمه اتفاقيات', main_heading1)
            worksheet.write('H4', 'المسافة المقطوعة', main_heading1)
            worksheet.write('I4', 'المسافة الإضافية', main_heading1)
            worksheet.write('J4', 'اجمالي المسافة', main_heading1)
            worksheet.write('K4', 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write('L4', 'قيمة الديزل', main_heading1)
            worksheet.write('M4', 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write('N4', 'اجمالي مصروف الطريق', main_heading1)


            worksheet.write('A5', 'Vehicle Sticker', main_heading1)
            worksheet.write('B5', 'Vehicle Type Name', main_heading1)
            worksheet.write('C5', 'Vehicle States', main_heading1)
            worksheet.write('D5', 'Employee ID', main_heading1)
            worksheet.write('E5', 'Driver Name', main_heading1)
            worksheet.write('F5', 'No. Bx Agreement', main_heading1)
            worksheet.write('G5', 'Tot Invoice Amt Before Tax', main_heading1)
            worksheet.write('H5', 'Trip Distance', main_heading1)
            worksheet.write('I5', 'Extra Distance', main_heading1)
            worksheet.write('J5', 'Total Distance', main_heading1)
            worksheet.write('K5', 'Extra Distance Amt', main_heading1)
            worksheet.write('L5', 'Total Fuel Expense', main_heading1)
            worksheet.write('M5', 'Total Reward amount Backend', main_heading1)
            worksheet.write('N5', 'Total Fuel Amt', main_heading1)

            worksheet.set_column('A:AB', 15)


            total_bx = 0
            total_bxx = 0
            tripp_distance = 0
            extr_distance = 0
            totl_distance = 0
            total_distance = 0
            total_fuel_amount = 0
            total_reward_amount = 0
            total_amount = 0
            total_d_amount = 0

            row = 5
            col = 0

            for rec in list(unique_bx):

                all_data = transport_lines.loc[(transport_lines['taq_number']) == rec]

                all_data = all_data.groupby(['taq_number'], as_index=False).sum()

                all_amt = 0
                all_numz = 0
                distance_trip = 0
                distance_trip = 0
                ex_distance = 0
                tot_distance = 0
                tot_extra_d_amt = 0
                tot_fuel_amount = 0
                tot_reward_amount = 0

                if len(all_data) > 0:
                    for index, line in all_data.iterrows():
                        delivery = self.env['transport.management'].search([('id', '=', line['self_id'])])

                        all_amt = line['total_before_taxes']
                        all_numz = line['counter']
                        distance_trip = line['trip_distance']
                        ex_distance = line['extra_distance']
                        tot_distance = line['total_distance']
                        tot_extra_d_amt = delivery.extra_distance_amount

                        tot_fuel_amount = line['total_fuel_amount']
                        tot_reward_amount = line['total_reward_amount']

                trans_vehicle = self.env['fleet.vehicle'].search([('taq_number','=',rec)],limit=1)

                worksheet.write_string(row, col + 0, str(trans_vehicle.taq_number), main_data)
                worksheet.write_string(row, col + 1, str(trans_vehicle.vehicle_type.vehicle_type_name), main_data)
                worksheet.write_string(row, col + 2, str(trans_vehicle.vehicle_status.vehicle_status_name), main_data)
                worksheet.write_string(row, col + 3, str(trans_vehicle.driver_code), main_data)
                worksheet.write_string(row, col + 4, str(trans_vehicle.bsg_driver.name), main_data)
                worksheet.write_string(row, col + 5, str(all_numz), main_data)
                worksheet.write_string(row, col + 6, str(all_amt), main_data)
                worksheet.write_string(row, col + 7, str(distance_trip), main_data)
                worksheet.write_string(row, col + 8, str(ex_distance), main_data)
                worksheet.write_string(row, col + 9, str(tot_distance), main_data)
                worksheet.write_string(row, col + 10, str(tot_extra_d_amt), main_data)
                worksheet.write_string(row, col + 11, str(tot_fuel_amount), main_data)
                worksheet.write_string(row, col + 12, str(tot_reward_amount), main_data)
                worksheet.write_string(row, col + 13, str(tot_fuel_amount + tot_reward_amount), main_data)

                total_bx = total_bx + all_numz
                total_bxx = total_bxx + all_amt
                tripp_distance = tripp_distance + distance_trip
                extr_distance = extr_distance + ex_distance
                totl_distance = totl_distance + tot_distance
                total_fuel_amount = total_fuel_amount + tot_fuel_amount
                total_reward_amount = total_reward_amount + tot_reward_amount
                total_amount = total_amount + (tot_fuel_amount + tot_reward_amount)
                total_d_amount = total_d_amount + tot_extra_d_amt

                row += 1

            loc = 'A' + str(row + 1)
            loc = 'B' + str(row + 1)
            loc = 'C' + str(row + 1)
            loc = 'D' + str(row + 1)
            loc = 'E' + str(row + 1)
            loc1 = 'F' + str(row + 1)
            loc2 = 'G' + str(row + 1)
            loc3 = 'H' + str(row + 1)
            loc4 = 'I' + str(row + 1)
            loc5 = 'J' + str(row + 1)
            loc6 = 'K' + str(row + 1)
            loc7 = 'L' + str(row + 1)
            loc8 = 'M' + str(row + 1)
            loc9 = 'N' + str(row + 1)
            loc10 = 'O' + str(row + 1)

            end_loc = str(loc) + ':' + str(loc)
            worksheet.merge_range(str(end_loc), 'Grand Total', main_heading)
            worksheet.write_string(str(loc1), str("{0:.2f}".format(total_bx)), main_heading1)
            worksheet.write_string(str(loc2), str("{0:.2f}".format(total_bxx)), main_heading1)
            worksheet.write_string(str(loc3), str("{0:.2f}".format(tripp_distance)), main_heading1)
            worksheet.write_string(str(loc4), str("{0:.2f}".format(extr_distance)), main_heading1)
            worksheet.write_string(str(loc5), str("{0:.2f}".format(totl_distance)), main_heading1)
            worksheet.write_string(str(loc6), str("{0:.2f}".format(total_d_amount)), main_heading1)
            worksheet.write_string(str(loc7), str("{0:.2f}".format(total_fuel_amount)), main_heading1)
            worksheet.write_string(str(loc8), str("{0:.2f}".format(total_reward_amount)), main_heading1)
            worksheet.write_string(str(loc9), str("{0:.2f}".format(total_amount)), main_heading1)
            # # worksheet.write_string(str(loc5), str(" "), main_heading1)

        if data['report_mode'] == 'Bx Vehicle productivity Detail Report':

            worksheet.merge_range('A1:L1', "Bx Vehicle productivity Detail Report", merge_format)
            worksheet.merge_range('A2:L2', "تقرير تفصيلي انتاجيه شاحنات نقل البضائع", merge_format)

            # unique_vehicle = transport_lines.vehicle_type.unique()



            worksheet.write('A4', 'استيكر الشاحنة', main_heading1)
            worksheet.write('B4', 'نوع الشاحنة', main_heading1)
            worksheet.write('C4', 'حالة الشاحنة', main_heading1)
            worksheet.write('D4', 'كود السائق', main_heading1)
            worksheet.write('E4', 'اسم السائق', main_heading1)
            worksheet.write('F4', 'عدد اتفاقيات', main_heading1)
            worksheet.write('G4', 'اسم خط السير', main_heading1)
            worksheet.write('H4', 'قيمه اتفاقيات', main_heading1)
            worksheet.write('I4', 'اجمالي المسافة', main_heading1)
            worksheet.write('J4', 'قيمة الديزل', main_heading1)
            worksheet.write('K4', 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write('L4', 'اجمالي مصروف الطريق', main_heading1)


            worksheet.write('A5', 'Vehicle Sticker', main_heading1)
            worksheet.write('B5', 'Vehicle Type Name', main_heading1)
            worksheet.write('C5', 'Vehicle States', main_heading1)
            worksheet.write('D5', 'Employee ID', main_heading1)
            worksheet.write('E5', 'Driver Name', main_heading1)
            worksheet.write('F5', 'No. Bx Agreement', main_heading1)
            worksheet.write('G5', 'Route Name', main_heading1)
            worksheet.write('H5', 'Tot Invoice Amt Before Tax', main_heading1)
            worksheet.write('I5', 'Total Distance', main_heading1)
            worksheet.write('J5', 'Total Fuel Expense', main_heading1)
            worksheet.write('K5', 'Total Reward amount Backend', main_heading1)
            worksheet.write('L5', 'Total Fuel Amt', main_heading1)


            worksheet.set_column('A:AB', 15)

            total_before_taxes = 0
            total_distance = 0
            total_fuel_amount = 0
            total_reward_amount = 0
            total_amount = 0

            row = 5
            col = 0

            # transport_lines['taq_number'] = transport_lines['order_date'].astype(str)

            transport_lines = transport_lines.sort_values(by='order_date')
            transport_lines = transport_lines.sort_values(by='taq_number')

            for index, rec in transport_lines.iterrows():
                trans_vehicle = self.env['transport.management'].browse(rec.self_id).transportation_vehicle
                trans_route = self.env['bsg_route'].browse(int(rec['route_id'])).route_name
                trans_routeee = self.env['fleet.vehicle'].browse(int(rec['transportation_vehicle'])).taq_number


                worksheet.write_string(row, col + 0, str(trans_routeee), main_data)
                worksheet.write_string(row, col + 1, str(trans_vehicle.vehicle_type.vehicle_type_name), main_data)
                worksheet.write_string(row, col + 2, str(trans_vehicle.vehicle_status.vehicle_status_name), main_data)
                worksheet.write_string(row, col + 3, str(trans_vehicle.driver_code), main_data)
                worksheet.write_string(row, col + 4, str(trans_vehicle.bsg_driver.name), main_data)
                worksheet.write_string(row, col + 5, str(rec['transportation_no']), main_data)
                worksheet.write_string(row, col + 6, str(trans_route), main_data)
                worksheet.write_string(row, col + 7, str(rec['total_before_taxes']), main_data)
                worksheet.write_string(row, col + 8, str(rec['total_distance']), main_data)
                worksheet.write_string(row, col + 9, str(rec['total_fuel_amount']), main_data)
                worksheet.write_string(row, col + 10, str(rec['total_reward_amount']), main_data)
                worksheet.write_string(row, col + 11, str(rec['total_fuel_amount'] + rec['total_reward_amount']), main_data)


                total_before_taxes = total_before_taxes + rec['total_before_taxes']
                total_distance = total_distance + rec['total_distance']
                total_fuel_amount = total_fuel_amount + rec['total_fuel_amount']
                total_reward_amount = total_reward_amount + rec['total_reward_amount']
                total_amount = total_amount + rec['total_amount']

                row += 1

            loc = 'A' + str(row + 1)
            loc = 'B' + str(row + 1)
            loc = 'C' + str(row + 1)
            loc = 'D' + str(row + 1)
            loc = 'E' + str(row + 1)
            loc1 = 'F' + str(row + 1)
            loc2 = 'G' + str(row + 1)
            loc3 = 'H' + str(row + 1)
            loc4 = 'I' + str(row + 1)
            loc5 = 'J' + str(row + 1)
            loc6 = 'K' + str(row + 1)
            loc7 = 'L' + str(row + 1)

            end_loc = str(loc) + ':' + str(loc1)
            worksheet.merge_range(str(end_loc), 'Grand Total', main_heading)
            worksheet.write_string(str(loc3), str("{0:.2f}".format(total_before_taxes)), main_heading1)
            worksheet.write_string(str(loc4), str("{0:.2f}".format(total_distance)), main_heading1)
            worksheet.write_string(str(loc5), str("{0:.2f}".format(total_fuel_amount)), main_heading1)
            worksheet.write_string(str(loc6), str("{0:.2f}".format(total_reward_amount)), main_heading1)
            worksheet.write_string(str(loc7), str("{0:.2f}".format(total_amount)), main_heading1)
            # worksheet.write_string(str(loc5), str(" "), main_heading1)

        if data['report_mode'] == 'Bx Vehicle Type Summary Report':

            worksheet.merge_range('A1:J1', "Bx Vehicle Type Summary Report", merge_format)
            worksheet.merge_range('A2:J2', "تقرير ملخص انتاجيه أنواع شاحنات نقل البضائع", merge_format)

            unique_type = transport_lines.fleet_type_transport.unique()

            # print(transport_lines.fleet_type_transport)

            worksheet.write('A4', 'نوع الشاحنة', main_heading1)
            worksheet.write('B4', 'رقم الرحلة', main_heading1)
            worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
            worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
            worksheet.write('E4', 'المسافة الإضافية', main_heading1)
            worksheet.write('F4', 'اجمالي المسافة', main_heading1)
            worksheet.write('G4', 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write('H4', 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write('I4', 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write('J4', 'اجمالي مصروف الطريق', main_heading1)

            worksheet.write('A5', 'Vehicle Type Name', main_heading1)
            worksheet.write('B5', 'Bx Agreement', main_heading1)
            worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
            worksheet.write('D5', 'Trip Distance', main_heading1)
            worksheet.write('E5', 'Extra Distance', main_heading1)
            worksheet.write('F5', 'Total Distance', main_heading1)
            worksheet.write('G5', 'extra Distance Amount', main_heading1)
            worksheet.write('H5', 'Total Fuel Expense', main_heading1)
            worksheet.write('I5', 'Total Reward amount Backend', main_heading1)
            worksheet.write('J5', 'Total Amt', main_heading1)

            worksheet.set_column('A:AB', 15)

            tot_bx = 0
            tot_invc_amt = 0
            tot_trip = 0
            tot_extra = 0
            tott_distance = 0
            tot_fuel_amt = 0
            tot_rewrd_amt = 0
            tot_amt = 0

            row = 5
            col = 0

            for rec in list(unique_type):
                all_data = transport_lines.loc[(transport_lines['fleet_type_transport'] == rec)]
                all_data = all_data.groupby(['fleet_type_transport'], as_index=False).sum()

                all_amt = 0
                all_numz = 0
                distance_trip = 0
                ex_distance = 0
                tot_distance = 0
                tot_fuel_amount = 0
                tot_reward_amount = 0
                extra_distance_amt = 0
                tot_amount = 0

                if len(all_data) > 0:
                    for index, line in all_data.iterrows():
                        all_amt = line['total_before_taxes']
                        all_numz = line['counter']
                        distance_trip = line['trip_distance']
                        ex_distance = line['extra_distance']
                        tot_distance = line['total_distance']
                        tot_fuel_amount = line['total_fuel_amount']
                        tot_reward_amount = line['total_reward_amount']
                        # extra_distance_amt = line['extra_distance_amount']
                        tot_amount = line['total_amount']


                s_vehicle = self.env['fleet.vehicle'].search([('vehicle_type', '=', rec)], limit=1)

                worksheet.write_string(row, col + 0, str(s_vehicle.vehicle_type.display_name), main_data)
                worksheet.write_string(row, col + 1, str(all_numz), main_data)
                worksheet.write_string(row, col + 2, str(all_amt), main_data)
                worksheet.write_string(row, col + 3, str(distance_trip), main_data)
                worksheet.write_string(row, col + 4, str(ex_distance), main_data)
                worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                # worksheet.write_string(row, col + 6, str(extra_distance_amt), main_data)
                worksheet.write_string(row, col + 7, str(tot_fuel_amount), main_data)
                worksheet.write_string(row, col + 8, str(tot_reward_amount), main_data)
                worksheet.write_string(row, col + 9, str(tot_amount), main_data)

                tot_bx = tot_bx + all_numz
                tot_invc_amt = tot_invc_amt + all_amt
                tot_trip = tot_trip + distance_trip
                tot_extra = tot_extra + ex_distance
                tott_distance = tott_distance + tot_distance
                tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                tot_amt = tot_amt + tot_amount





                row += 1

            loc = 'A' + str(row + 1)
            loc1 = 'B' + str(row + 1)
            loc2 = 'C' + str(row + 1)
            loc3 = 'D' + str(row + 1)
            loc4 = 'E' + str(row + 1)
            loc5 = 'F' + str(row + 1)
            loc6 = 'G' + str(row + 1)
            loc7 = 'H' + str(row + 1)
            loc8 = 'I' + str(row + 1)
            loc9 = 'J' + str(row + 1)


            worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
            worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
            worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
            worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip)), main_heading1)
            worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra)), main_heading1)
            worksheet.write_string(str(loc5), str("{0:.2f}".format(tott_distance)), main_heading1)
            # worksheet.write_string(str(loc6), str("{0:.2f}".format(extra_distance_amt)), main_heading1)
            worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
            worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
            worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_amt)), main_heading1)
            # worksheet.write_string(str(loc8), str(" "), main_heading1)

        if data['report_mode'] == 'Bx Driver Summary Report':

            worksheet.merge_range('A1:P1', "Bx Driver Summary Report", merge_format)
            worksheet.merge_range('A2:P2', "تقرير اجمالي إيرادات نقل البضاع بحسب المستخدم", merge_format)



            worksheet.write('A4', 'كود السائق', main_heading1)
            worksheet.write('B4', 'اسم السائق', main_heading1)
            worksheet.write('C4', 'تاريخ التعيين', main_heading1)
            worksheet.write('D4', 'حالة السائق', main_heading1)
            worksheet.write('E4', 'استيكر الشاحنة', main_heading1)
            worksheet.write('F4', 'نوع الشاحنة', main_heading1)
            worksheet.write('G4', 'حالة الشاحنة', main_heading1)
            worksheet.write('H4', 'عدد اتفاقيات', main_heading1)
            worksheet.write('I4', 'قيمه اتفاقيات', main_heading1)
            worksheet.write('J4', 'المسافة المقطوعة', main_heading1)
            worksheet.write('K4', 'المسافة الإضافية', main_heading1)
            worksheet.write('L4', 'اجمالي المسافة', main_heading1)
            worksheet.write('M4', 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write('N4', 'قيمة الديزل', main_heading1)
            worksheet.write('O4', 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write('P4', 'اجمالي مصروف الطريق', main_heading1)

            worksheet.write('A5', 'Employee ID', main_heading1)
            worksheet.write('B5', 'Driver Name', main_heading1)
            worksheet.write('C5', 'Date of Join', main_heading1)
            worksheet.write('D5', 'Employee State', main_heading1)
            worksheet.write('E5', 'Vehicle Sticker', main_heading1)
            worksheet.write('F5', 'Vehicle Type Name', main_heading1)
            worksheet.write('G5', 'Vehicle States', main_heading1)
            worksheet.write('H5', 'No. Bx Agreement', main_heading1)
            worksheet.write('I5', 'Tot Invoice Amt Before Tax', main_heading1)
            worksheet.write('J5', 'Trip Distance', main_heading1)
            worksheet.write('K5', 'Extra Distance', main_heading1)
            worksheet.write('L5', 'Total Distance', main_heading1)
            worksheet.write('M5', 'Extra Distance Amt', main_heading1)
            worksheet.write('N5', 'Total Fuel Expense', main_heading1)
            worksheet.write('O5', 'Total Reward amount Backend', main_heading1)
            worksheet.write('P5', 'Total Amt', main_heading1)


            worksheet.set_column('A:AB', 15)

            tot_pos_num = 0
            tot_pos_amt = 0
            tot_unpos_num = 0
            tot_unpos_amt = 0
            tot_dis_num = 0
            tot_fuel_num = 0
            tot_rwrd_num = 0
            tot_all_num = 0
            all_numz = 0

            row = 5
            col = 0


            bsg_driver_list = []
            transport_lines = transport_lines.sort_values(by='order_date')
            for index, rec in transport_lines.iterrows():

                trans_vehicle = self.env['transport.management'].browse(rec.self_id).transportation_vehicle
                trans_driver = self.env['transport.management'].browse(rec.self_id).transportation_driver
                if trans_vehicle.bsg_driver.id not in bsg_driver_list:
                    worksheet.write_string(row, col + 0, str(trans_driver.driver_code), main_data)
                    worksheet.write_string(row, col + 1, str(trans_vehicle.bsg_driver.name), main_data)
                    worksheet.write_string(row, col + 2, str(trans_driver.bsgjoining_date), main_data)
                    worksheet.write_string(row, col + 3, str(trans_driver.employee_state), main_data)
                    worksheet.write_string(row, col + 4, str(trans_vehicle.taq_number), main_data)
                    worksheet.write_string(row, col + 5, str(trans_vehicle.vehicle_type.vehicle_type_name), main_data)
                    worksheet.write_string(row, col + 6, str(trans_vehicle.vehicle_status.vehicle_status_name), main_data)
                    sum = self.get_sum(trans_vehicle.bsg_driver.id,transport_lines)

                    worksheet.write_string(row, col + 7, str(sum['all_numz']), main_data)
                    # worksheet.write_string(row, col + 8, str(sum['all_amt']), main_data)
                    # worksheet.write_string(row, col + 9, str(sum['distance_trip']), main_data)
                    # worksheet.write_string(row, col + 10, str(sum['ex_distance']), main_data)
                    # worksheet.write_string(row, col + 11, str(sum['tot_distance']), main_data)
                    # # worksheet.write_string(row, col + 12, str(sum['extra_distance_amount']), main_data)
                    # worksheet.write_string(row, col + 13, str(sum['tot_fuel_amount']), main_data)
                    # worksheet.write_string(row, col + 14, str(sum['tot_reward_amount']), main_data)
                    # worksheet.write_string(row, col + 15, str(sum['tot_amount']), main_data)
                    bsg_driver_list.append(trans_vehicle.bsg_driver.id)
                    row += 1

                    # tot_pos_amt = tot_pos_amt + sum['all_numz']
                    # tot_pos_num = tot_pos_num + sum['all_amt']
                    # tot_unpos_amt = tot_unpos_amt + sum['distance_trip']
                    # tot_unpos_num = tot_unpos_num + sum['ex_distance']
                    # tot_dis_num = tot_dis_num + sum['tot_distance']
                    # tot_fuel_num = tot_fuel_num + sum['tot_fuel_amount']
                    # tot_rwrd_num = tot_rwrd_num + sum['tot_reward_amount']
                    # tot_all_num = tot_all_num + sum['tot_amount']
                    # tot_amt = tot_amt + all_amt
                    # tot_num = tot_num + all_numz

            row += 1

            loc = 'A' + str(row + 1)
            loc1 = 'B' + str(row + 1)
            loc2 = 'C' + str(row + 1)
            loc3 = 'D' + str(row + 1)
            loc4 = 'E' + str(row + 1)
            loc5 = 'F' + str(row + 1)
            loc6 = 'G' + str(row + 1)
            loc7 = 'H' + str(row + 1)
            loc8 = 'I' + str(row + 1)
            loc9 = 'J' + str(row + 1)
            loc10 = 'K' + str(row + 1)
            loc11 = 'L' + str(row + 1)
            loc12 = 'M' + str(row + 1)
            loc13 = 'N' + str(row + 1)
            loc14 = 'O' + str(row + 1)
            loc15 = 'P' + str(row + 1)

            worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
            # worksheet.write_string(str(loc1), str(" "), main_heading1)
            # worksheet.write_string(str(loc2), str(" "), main_heading1)
            # worksheet.write_string(str(loc3), str(" "), main_heading1)
            # worksheet.write_string(str(loc4), str(" "), main_heading1)
            # worksheet.write_string(str(loc5), str(" "), main_heading1)
            # worksheet.write_string(str(loc6), str(" "), main_heading1)
            # worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_pos_amt)), main_heading1)
            # worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_pos_num)), main_heading1)
            # worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_unpos_amt)), main_heading1)
            # worksheet.write_string(str(loc10), str("{0:.2f}".format(tot_unpos_num)), main_heading1)
            # worksheet.write_string(str(loc11), str("{0:.2f}".format(tot_dis_num)), main_heading1)
            # # worksheet.write_string(str(loc12), str("{0:.2f}".format(tot_dis_num)), main_heading1)
            # worksheet.write_string(str(loc13), str("{0:.2f}".format(tot_fuel_num)), main_heading1)
            # worksheet.write_string(str(loc14), str("{0:.2f}".format(tot_rwrd_num)), main_heading1)
            # worksheet.write_string(str(loc15), str("{0:.2f}".format(tot_all_num)), main_heading1)

        if data['report_mode'] == 'Bx User Summary Report':

            worksheet.merge_range('A1:N1', "Bx User Summary Report", merge_format)
            worksheet.merge_range('A2:N2', "تقرير اجمالي إيرادات نقل البضاع بحسب العميل", merge_format)

            worksheet.write('A4', 'ركود المستخدم', main_heading1)
            worksheet.write('B4', 'اسم المستخدم', main_heading1)
            worksheet.write('C4', 'تاريخ التعيين', main_heading1)
            worksheet.write('D4', 'حالة المستخدم', main_heading1)
            worksheet.write('E4', 'اسم الفرع الحالي', main_heading1)
            worksheet.write('F4', 'عدد اتفاقيات', main_heading1)
            worksheet.write('G4', 'قيمه اتفاقيات', main_heading1)
            worksheet.write('H4', 'المسافة المقطوعة', main_heading1)
            worksheet.write('I4', 'المسافة الإضافية', main_heading1)
            worksheet.write('J4', 'اجمالي المسافة', main_heading1)
            worksheet.write('K4', 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write('L4', 'قيمة الديزل', main_heading1)
            worksheet.write('M4', 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write('N4', 'اجمالي مصروف الطريق', main_heading1)


            worksheet.write('A5', 'Employee ID', main_heading1)
            worksheet.write('B5', 'User Name', main_heading1)
            worksheet.write('C5', 'Date of Join', main_heading1)
            worksheet.write('D5', 'Employee State', main_heading1)
            worksheet.write('E5', 'Current Branch', main_heading1)
            worksheet.write('F5', 'No. Bx Agreement', main_heading1)
            worksheet.write('G5', 'Tot Invoice Amt Before Tax', main_heading1)
            worksheet.write('H5', 'Trip Distance', main_heading1)
            worksheet.write('I5', 'Extra Distance', main_heading1)
            worksheet.write('J5', 'Total Distance', main_heading1)
            worksheet.write('K5', 'Extra Distance Amt', main_heading1)
            worksheet.write('L5', 'Total Fuel Expense', main_heading1)
            worksheet.write('M5', 'Total Reward amount Backend', main_heading1)
            worksheet.write('N5', 'Total Amt', main_heading1)

            worksheet.set_column('A:AB', 15)


            user_name_list = []
            row = 5
            col = 0
            tot_count = 0
            tot_count_bx = 0
            tot_count_trip = 0
            tot_count_extra = 0
            tot_count_tot = 0
            tot_count_fuel = 0
            tot_count_rwrd = 0
            tot_count_amt = 0
            transport_lines = transport_lines.sort_values(by='order_date')
            for index, rec in transport_lines.iterrows():

                trans_driver = self.env['transport.management'].browse(rec.self_id).transportation_driver
                id_x = self.env['transport.management'].browse(rec.self_id).create_uid.id
                if id_x not in user_name_list:
                    worksheet.write_string(row, col + 0, str(trans_driver.driver_code), main_data)
                    worksheet.write_string(row, col + 1, str(self.env['transport.management'].browse(rec.self_id).create_uid.name), main_data)
                    worksheet.write_string(row, col + 2, str(trans_driver.bsgjoining_date), main_data)
                    worksheet.write_string(row, col + 3, str(trans_driver.employee_state), main_data)
                    worksheet.write_string(row, col + 4, str(trans_driver.branch_id.branch_ar_name), main_data)
                    sum = self.get_sum_by_user(id_x,transport_lines)

                    worksheet.write_string(row, col + 5, str(sum['counter']), main_data)
                    worksheet.write_string(row, col + 6, str(sum['total_before_taxes']), main_data)
                    worksheet.write_string(row, col + 7, str(sum['trip_distance']), main_data)
                    worksheet.write_string(row, col + 8, str(sum['extra_distance']), main_data)
                    worksheet.write_string(row, col + 9, str(sum['total_distance']), main_data)
                    # worksheet.write_string(row, col + 10, str(all_total), main_data)
                    worksheet.write_string(row, col + 11, str(sum['total_fuel_amount']), main_data)
                    worksheet.write_string(row, col + 12, str(sum['total_reward_amount']), main_data)
                    worksheet.write_string(row, col + 13, str(sum['total_amount']), main_data)
                    user_name_list.append(id_x)
                    row += 1


                    tot_count = tot_count + sum['counter'] 
                    tot_count_bx = tot_count_bx + sum['total_before_taxes'] 
                    tot_count_trip = tot_count_trip + sum['trip_distance'] 
                    tot_count_extra = tot_count_extra + sum['extra_distance'] 
                    tot_count_tot = tot_count_tot + sum['total_distance'] 
                    tot_count_fuel = tot_count_fuel + sum['total_fuel_amount'] 
                    tot_count_rwrd = tot_count_rwrd + sum['total_reward_amount'] 
                    tot_count_amt = tot_count_amt + sum['total_amount'] 


            row += 1

            loc = 'A' + str(row + 1)
            loc1 = 'B' + str(row + 1)
            loc2 = 'C' + str(row + 1)
            loc3 = 'D' + str(row + 1)
            loc4 = 'E' + str(row + 1)
            loc5 = 'F' + str(row + 1)
            loc6 = 'G' + str(row + 1)
            loc7 = 'H' + str(row + 1)
            loc8 = 'I' + str(row + 1)
            loc9 = 'J' + str(row + 1)
            loc10 = 'K' + str(row + 1)
            loc11 = 'L' + str(row + 1)
            loc12 = 'M' + str(row + 1)
            loc13 = 'N' + str(row + 1)


            worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
            worksheet.write_string(str(loc1), str(" "), main_heading1)
            worksheet.write_string(str(loc2), str(" "), main_heading1)
            worksheet.write_string(str(loc3), str(" "), main_heading1)
            worksheet.write_string(str(loc4), str(" "), main_heading1)
            worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_count)), main_heading1)
            worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_count_bx)), main_heading1)
            worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_count_trip)), main_heading1)
            worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_count_extra)), main_heading1)
            worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_count_tot)), main_heading1)
            # worksheet.write_string(str(loc10), str("{0:.2f}".format(tot_count_tot)), main_heading1)
            worksheet.write_string(str(loc11), str("{0:.2f}".format(tot_count_fuel)), main_heading1)
            worksheet.write_string(str(loc12), str("{0:.2f}".format(tot_count_rwrd)), main_heading1)
            worksheet.write_string(str(loc13), str("{0:.2f}".format(tot_count_amt)), main_heading1)

        if data['report_mode'] == 'Bx Productivity Summary Loading Date Report':

            if data['period_group'] == 'day':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب اليوم", merge_format)

                transport_lines = transport_lines.sort_values(by='order_date')
                unique_date = transport_lines.loading_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write('H4', 'قيمة الديزل', main_heading1)
                worksheet.write('I4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('J4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'extra Distance Amount', main_heading1)
                worksheet.write('H5', 'Total Fuel Expense', main_heading1)
                worksheet.write('I5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('J5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0
                tot_extra_d_amtt = 0

                row = 5
                col = 0

                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")

                # transport_lines = transport_lines.loc[(transport_lines['state'] != 'cancel')]
                transport_lines = transport_lines.loc[(transport_lines['state'].isin(['fuel_voucher', 'receive_pod', 'done']))]
                # if data['state']:
                #     transport_lines = transport_lines.loc[(transport_lines['state'] == data['state'])]



                for rec in unique_date:
                    all_data = transport_lines.loc[(transport_lines['loading_date'] == rec)]
                    all_data = all_data.groupby(['loading_date'], as_index=False).sum()
                    # transport_lines = transport_lines.drop_duplicates(subset='transport_lines', keep="first")

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_extra_d_amt = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0


                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            delivery = self.env['transport.management'].search([('id', '=', line['self_id'])])
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_extra_d_amt = delivery.extra_distance_amount
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                            # print(all_data, 'all_data')





                    worksheet.write_string(row, col + 0, str(line['loading_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 6, str(tot_extra_d_amt), main_data)
                    worksheet.write_string(row, col + 7, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 9, str(tot_amount), main_data)
                    worksheet.write_string(row, col + 9, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_extra_d_amtt = tot_extra_d_amtt + tot_extra_d_amt
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount


                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)
                loc9 = 'J' + str(row + 1)


                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_extra_d_amtt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'weekly':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب الأسبوع", merge_format)

                transport_lines['weekly_date'] = transport_lines['date'].astype(str).str[:7]
                unique_weekly = transport_lines.weekly_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة الديزل', main_heading1)
                worksheet.write('H4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('I4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'Total Fuel Expense', main_heading1)
                worksheet.write('H5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('I5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")

                for rec in unique_weekly:

                    all_data = transport_lines.loc[(transport_lines['weekly_date'] == rec)]
                    all_data = all_data.groupby(['weekly_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['weekly_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 6, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 7, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'month':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب الشهر", merge_format)


                transport_lines = transport_lines.sort_values(by='order_date')
                transport_lines['loading_date'] = transport_lines['loading_date'].astype(str).str[:7]
                unique_month = transport_lines.loading_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write('H4', 'قيمة الديزل', main_heading1)
                worksheet.write('I4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('J4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'extra Distance Amount', main_heading1)
                worksheet.write('H5', 'Total Fuel Expense', main_heading1)
                worksheet.write('I5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('J5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")

                for rec in unique_month:

                    all_data = transport_lines.loc[(transport_lines['loading_date'] == rec)]
                    all_data = all_data.groupby(['loading_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['loading_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    # worksheet.write_string(row, col + 6, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 7, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 9, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)
                loc9 = 'J' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                # worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'quarterly':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب ربع سنوي", merge_format)

                transport_lines['quarterly_date'] = transport_lines['date'].astype(str).str[:4]
                unique_quarterly = transport_lines.quarterly_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة الديزل', main_heading1)
                worksheet.write('H4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('I4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'Total Fuel Expense', main_heading1)
                worksheet.write('H5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('I5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                for rec in unique_quarterly:

                    all_data = transport_lines.loc[(transport_lines['quarterly_date'] == rec)]
                    all_data = all_data.groupby(['quarterly_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['quarterly_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 6, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 7, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'year':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب سنوي", merge_format)

                transport_lines['loading_date'] = transport_lines['loading_date'].astype(str).str[:4]
                unique_year = transport_lines.loading_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write('H4', 'قيمة الديزل', main_heading1)
                worksheet.write('I4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('J4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'extra Distance Amount', main_heading1)
                worksheet.write('H5', 'Total Fuel Expense', main_heading1)
                worksheet.write('I5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('J5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)


                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")

                for rec in unique_year:
                    all_data = transport_lines.loc[(transport_lines['loading_date'] == rec)]
                    all_data = all_data.groupby(['loading_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['loading_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    # worksheet.write_string(row, col + 6, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 7, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 9, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)
                loc9 = 'J' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                # worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_amt)), main_heading1)

        if data['report_mode'] == 'Bx Productivity Summary Arrival Date Report':

            if data['period_group'] == 'day':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب اليوم", merge_format)

                transport_lines = transport_lines.sort_values(by='order_date')
                unique_date = transport_lines.arrival_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write('H4', 'قيمة الديزل', main_heading1)
                worksheet.write('I4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('J4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'extra Distance Amount', main_heading1)
                worksheet.write('H5', 'Total Fuel Expense', main_heading1)
                worksheet.write('I5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('J5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0
                tot_extra_d_amtt = 0

                row = 5
                col = 0

                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")



                for rec in unique_date:

                    all_data = transport_lines.loc[(transport_lines['arrival_date'] == rec)]
                    all_data = all_data.groupby(['arrival_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_extra_d_amt = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            delivery = self.env['transport.management'].search([('id', '=', line['self_id'])])
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_extra_d_amt = delivery.extra_distance_amount
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['arrival_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 6, str(tot_extra_d_amt), main_data)
                    worksheet.write_string(row, col + 7, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 9, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_extra_d_amtt = tot_extra_d_amtt + tot_extra_d_amt
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)
                loc9 = 'J' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_extra_d_amtt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'weekly':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب الأسبوع", merge_format)

                transport_lines['weekly_date'] = transport_lines['date'].astype(str).str[:7]
                unique_weekly = transport_lines.weekly_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة الديزل', main_heading1)
                worksheet.write('H4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('I4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'Total Fuel Expense', main_heading1)
                worksheet.write('H5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('I5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")

                for rec in unique_weekly:

                    all_data = transport_lines.loc[(transport_lines['weekly_date'] == rec)]
                    all_data = all_data.groupby(['weekly_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['weekly_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 6, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 7, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'month':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب الشهر", merge_format)

                transport_lines = transport_lines.sort_values(by='order_date')
                transport_lines['loading_date'] = transport_lines['loading_date'].astype(str).str[:7]
                unique_month = transport_lines.loading_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write('H4', 'قيمة الديزل', main_heading1)
                worksheet.write('I4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('J4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'extra Distance Amount', main_heading1)
                worksheet.write('H5', 'Total Fuel Expense', main_heading1)
                worksheet.write('I5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('J5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")

                for rec in unique_month:

                    all_data = transport_lines.loc[(transport_lines['loading_date'] == rec)]
                    all_data = all_data.groupby(['loading_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['loading_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    # worksheet.write_string(row, col + 6, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 7, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 9, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)
                loc9 = 'J' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                # worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'quarterly':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب ربع سنوي", merge_format)

                transport_lines['quarterly_date'] = transport_lines['date'].astype(str).str[:4]
                unique_quarterly = transport_lines.quarterly_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة الديزل', main_heading1)
                worksheet.write('H4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('I4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'Total Fuel Expense', main_heading1)
                worksheet.write('H5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('I5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                for rec in unique_quarterly:

                    all_data = transport_lines.loc[(transport_lines['quarterly_date'] == rec)]
                    all_data = all_data.groupby(['quarterly_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['quarterly_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 6, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 7, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_amt)), main_heading1)

            if data['period_group'] == 'year':

                worksheet.merge_range('A1:J1', "Bx Productivity Summary Loading Date Report", merge_format)
                worksheet.merge_range('A2:J2', "تقرير اجمالي إيرادات نقل البضاع بحسب سنوي", merge_format)

                transport_lines['loading_date'] = transport_lines['loading_date'].astype(str).str[:4]
                unique_year = transport_lines.loading_date.unique()

                worksheet.write('A4', 'التاريخ', main_heading1)
                worksheet.write('B4', 'رقم الرحلة', main_heading1)
                worksheet.write('C4', 'قيمه اتفاقيات', main_heading1)
                worksheet.write('D4', 'المسافة المقطوعة', main_heading1)
                worksheet.write('E4', 'المسافة الإضافية', main_heading1)
                worksheet.write('F4', 'اجمالي المسافة', main_heading1)
                worksheet.write('G4', 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write('H4', 'قيمة الديزل', main_heading1)
                worksheet.write('I4', 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write('J4', 'اجمالي مصروف الطريق', main_heading1)

                worksheet.write('A5', 'Date', main_heading1)
                worksheet.write('B5', 'Bx Agreement', main_heading1)
                worksheet.write('C5', 'Tot Invoice Amount Before Tax', main_heading1)
                worksheet.write('D5', 'Trip Distance', main_heading1)
                worksheet.write('E5', 'Extra Distance', main_heading1)
                worksheet.write('F5', 'Total Distance', main_heading1)
                worksheet.write('G5', 'extra Distance Amount', main_heading1)
                worksheet.write('H5', 'Total Fuel Expense', main_heading1)
                worksheet.write('I5', 'Total Reward amount Backend', main_heading1)
                worksheet.write('J5', 'Total Amt', main_heading1)

                worksheet.set_column('A:AB', 15)

                tot_bx = 0
                tot_invc_amt = 0
                tot_trip_amt = 0
                tot_extra_amt = 0
                tot_distance_amt = 0
                tot_fuel_amt = 0
                tot_rewrd_amt = 0
                tot_amt = 0

                row = 5
                col = 0
                transport_lines = transport_lines.drop_duplicates(subset='self_id', keep="first")

                for rec in unique_year:
                    all_data = transport_lines.loc[(transport_lines['loading_date'] == rec)]
                    all_data = all_data.groupby(['loading_date'], as_index=False).sum()

                    all_amt = 0
                    posted_numz = 0
                    tot_trip = 0
                    tot_extra = 0
                    tot_distance = 0
                    tot_fuel_amount = 0
                    tot_reward_amount = 0
                    tot_amount = 0

                    if len(all_data) > 0:
                        for index, line in all_data.iterrows():
                            all_amt = line['total_before_taxes']
                            posted_numz = line['counter']
                            tot_trip = line['trip_distance']
                            tot_extra = line['extra_distance']
                            tot_distance = line['total_distance']
                            tot_fuel_amount = line['total_fuel_amount']
                            tot_reward_amount = line['total_reward_amount']
                            tot_amount = line['total_amount']

                    worksheet.write_string(row, col + 0, str(line['loading_date']), main_data)
                    worksheet.write_string(row, col + 1, str(posted_numz), main_data)
                    worksheet.write_string(row, col + 2, str(all_amt), main_data)
                    worksheet.write_string(row, col + 3, str(tot_trip), main_data)
                    worksheet.write_string(row, col + 4, str(tot_extra), main_data)
                    worksheet.write_string(row, col + 5, str(tot_distance), main_data)
                    # worksheet.write_string(row, col + 6, str(tot_distance), main_data)
                    worksheet.write_string(row, col + 7, str(tot_fuel_amount), main_data)
                    worksheet.write_string(row, col + 8, str(tot_reward_amount), main_data)
                    worksheet.write_string(row, col + 9, str(tot_amount), main_data)

                    tot_bx = tot_bx + posted_numz
                    tot_invc_amt = tot_invc_amt + all_amt
                    tot_trip_amt = tot_trip_amt + tot_trip
                    tot_extra_amt = tot_extra_amt + tot_extra
                    tot_distance_amt = tot_distance_amt + tot_distance
                    tot_fuel_amt = tot_fuel_amt + tot_fuel_amount
                    tot_rewrd_amt = tot_rewrd_amt + tot_reward_amount
                    tot_amt = tot_amt + tot_amount

                    row += 1

                loc = 'A' + str(row + 1)
                loc1 = 'B' + str(row + 1)
                loc2 = 'C' + str(row + 1)
                loc3 = 'D' + str(row + 1)
                loc4 = 'E' + str(row + 1)
                loc5 = 'F' + str(row + 1)
                loc6 = 'G' + str(row + 1)
                loc7 = 'H' + str(row + 1)
                loc8 = 'I' + str(row + 1)
                loc9 = 'J' + str(row + 1)

                worksheet.write_string(str(loc), str("Grand Total"), main_heading1)
                worksheet.write_string(str(loc1), str("{0:.2f}".format(tot_bx)), main_heading1)
                worksheet.write_string(str(loc2), str("{0:.2f}".format(tot_invc_amt)), main_heading1)
                worksheet.write_string(str(loc3), str("{0:.2f}".format(tot_trip_amt)), main_heading1)
                worksheet.write_string(str(loc4), str("{0:.2f}".format(tot_extra_amt)), main_heading1)
                worksheet.write_string(str(loc5), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                # worksheet.write_string(str(loc6), str("{0:.2f}".format(tot_distance_amt)), main_heading1)
                worksheet.write_string(str(loc7), str("{0:.2f}".format(tot_fuel_amt)), main_heading1)
                worksheet.write_string(str(loc8), str("{0:.2f}".format(tot_rewrd_amt)), main_heading1)
                worksheet.write_string(str(loc9), str("{0:.2f}".format(tot_amt)), main_heading1)








