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
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import Warning, ValidationError
from odoo.tools import config
import base64
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import string


class TrialBalanceReportXlsx(models.AbstractModel):
    _name = 'report.bx_information_report.bx_info_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    # @api.multi
    def generate_xlsx_report(self, workbook, input_records, lines):

        data = input_records['form']
        model = self.env.context.get('active_model')
        wiz_data = self.env[model].browse(self.env.context.get('active_id'))

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
        worksheet = workbook.add_worksheet('Bx Information Report')

        row = 2
        col = 0

        if wiz_data.form and wiz_data.to:
            worksheet.write(row, col, 'Period', main_heading1)
            worksheet.write(row, col + 1, 'From', main_heading1)
            worksheet.write_string(row, col + 2, str(wiz_data.form), main_data)
            worksheet.write(row, col + 3, 'TO', main_heading1)
            worksheet.write_string(row, col + 4, str(wiz_data.to), main_data)
            row += 1

        tm_state_cond = ''
        if wiz_data.state:
            worksheet.write(row, col, 'State', main_heading1)
            worksheet.write_string(row, col + 1, wiz_data.state, main_data)
            row += 1
            tm_state = wiz_data.state
            tm_state_cond = f"and tm_table.state = '{tm_state}'"

        filter_customers = ''
        if wiz_data.customer_ids:
            rec_names = wiz_data.customer_ids.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Customer', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            customers = len(wiz_data.customer_ids.ids) == 1 and "(%s)" % wiz_data.customer_ids.ids[0] or str(
                tuple(wiz_data.customer_ids.ids))
            filter_customers = f"and tm_table.customer in  {customers}"

        from_branch_cond = ''
        if wiz_data.branch_ids:
            rec_names = wiz_data.branch_ids.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Branch From', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            from_branches = len(wiz_data.branch_ids.ids) == 1 and "(%s)" % wiz_data.branch_ids.ids[0] or str(
                tuple(wiz_data.branch_ids.ids))
            from_branch_cond = f"and bsg_route_waypoints.loc_branch_id in  {from_branches}"

        to_branch_cond = ''
        if wiz_data.branch_ids_to:
            rec_names = wiz_data.branch_ids_to.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Branch To', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            to_branches = len(wiz_data.branch_ids_to.ids) == 1 and "(%s)" % wiz_data.branch_ids_to.ids[0] or str(
                tuple(wiz_data.branch_ids_to.ids))
            to_branch_cond = f"and tm_table.to_transport in {to_branches}"

        users_cond = ''
        if wiz_data.users:
            rec_names = wiz_data.users.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Users', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            users = len(wiz_data.users.ids) == 1 and "(%s)" % wiz_data.users.ids[0] or str(
                tuple(wiz_data.users.ids))
            users_cond = f"and tm_table.create_uid in {users}"

        vehicles_cond = ''
        if wiz_data.vehicle_ids:
            rec_names = wiz_data.vehicle_ids.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Vehicles', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            vehicles = len(wiz_data.vehicle_ids.ids) == 1 and "(%s)" % wiz_data.vehicle_ids.ids[0] or str(
                tuple(wiz_data.vehicle_ids.ids))
            vehicles_cond = f"and tm_table.transportation_vehicle in {vehicles}"

        payment_method_cond = ''
        if wiz_data.payment_method_ids:
            rec_names = wiz_data.payment_method_ids.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Payment Methods', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            payment_methods = len(wiz_data.payment_method_ids.ids) == 1 and "(%s)" % wiz_data.payment_method_ids.ids[
                0] or str(
                tuple(wiz_data.payment_method_ids.ids))
            payment_method_cond = f"and tm_table.payment_method in {payment_methods}"

        driver_cond = ''
        if wiz_data.driver_ids:
            rec_names = wiz_data.driver_ids.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Drivers', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            drivers = len(wiz_data.driver_ids.ids) == 1 and "(%s)" % wiz_data.driver_ids.ids[0] or str(
                tuple(wiz_data.driver_ids.ids))
            driver_cond = f"and tm_table.transportation_driver in {drivers}"

        domain_cond = ''
        if wiz_data.vehicle_type_domain_ids:
            rec_names = wiz_data.vehicle_type_domain_ids.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Domains', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            domains = len(wiz_data.vehicle_type_domain_ids.ids) == 1 and "(%s)" % wiz_data.vehicle_type_domain_ids.ids[0] or str(
                tuple(wiz_data.vehicle_type_domain_ids.ids))
            domain_cond = f"and tm_table.vehicle_type_domain_id in {domains}"

        vehicle_type_cond = ''
        if wiz_data.vehicle_type_ids:
            rec_names = wiz_data.vehicle_type_ids.mapped('display_name')
            names = ','.join(rec_names)
            worksheet.write(row, col, 'Vehicle Types', main_heading1)
            worksheet.write_string(row, col + 1, names, main_data)
            row += 1
            vehicle_types = len(wiz_data.vehicle_type_ids.ids) == 1 and "(%s)" % wiz_data.vehicle_type_ids.ids[
                0] or str(
                tuple(wiz_data.vehicle_type_ids.ids))
            vehicle_type_cond = f"and tm_table.fleet_type_transport in {vehicle_types}"

        from_bx_cond = ''
        if wiz_data.from_bx:
            worksheet.write(row, col, 'BX From', main_heading1)
            worksheet.write_string(row, col + 1, wiz_data.from_bx.display_name, main_data)
            row += 1
            wiz_from_bx = "%d" % wiz_data.from_bx.id
            from_bx_cond = f"and tm_table.id >= {wiz_from_bx}"

        to_bx_cond = ''
        if wiz_data.to_bx:
            worksheet.write(row, col, 'BX TO', main_heading1)
            worksheet.write_string(row, col + 1, wiz_data.to_bx.display_name, main_data)
            row += 1
            wiz_to_bx = "%d" % wiz_data.to_bx.id
            to_bx_cond = f"and tm_table.id <= {wiz_to_bx}"

        table_name = "transport_management as tm_table"
        self.env.cr.execute(
            "select tm_table.id as tm_id,tm_table.transportation_no as tm_transportation_no,tm_table.order_date as tm_order_date,tm_table.customer as tm_customers,tm_table.form_transport as tm_from_transport\
            ,tm_table.to_transport as tm_to_transport,tm_table.total_before_taxes as tm_total_before_taxes,tm_table.tax_amount as tm_tax_amount,tm_table.total_amount as tm_total_amount\
            ,tm_table.driver_number as tm_driver_no,tm_table.transportation_driver as tm_transportation_driver,tm_table.transportation_vehicle as tm_transportation_vehicle,tm_table.route_id as tm_route_id\
            ,tm_table.display_expense_mthod_id as tm_display_expense_method_id,tm_table.display_expense_type as tm_display_expense_type,tm_table.trip_distance as tm_trip_distance,tm_table.extra_distance as tm_extra_distance\
            ,tm_table.reason as tm_reason,tm_table.total_distance as tm_total_distance,tm_table.total_fuel_amount as tm_total_fuel_amount,tm_table.total_reward_amount as tm_total_reward_amount,tm_table.state as tm_state\
            ,tm_table.create_uid as tm_create_uid,tm_table.invoice_id as tm_invoice_id,tm_table.payment_method as tm_payment_method,tm_table.driver as tm_driver,tm_table.loading_date as tm_loading_date\
            ,tm_table.arrival_date as tm_arrival_date,from_route_waypoint.id as from_route_waypoint_id,from_route_waypoint.loc_branch_id as route_waypoint_from_branch_id,emp_driver.id as emp_driver_id\
            ,emp_driver.driver_rewards as emp_driver_rewards,fuel_exp_amt.id as fuel_exp_amt_id,fuel_exp_amt.full_load_amt as full_load_amt,fuel_exp_amt.amt_full_without_reward as amt_full_wo_reward\
            ,fuel_exp_amt.empty_load_amt as empty_load_amt,fuel_exp_amt.amt_empty_without_reward as amt_empty_wo_reward,partner.id as partner_id,partner.name as partner_name\
            ,from_route_waypoint.route_waypoint_name as from_route_waypoint_name,to_route_waypoint.id as to_route_waypoint_id,to_route_waypoint.route_waypoint_name as to_route_waypoint_name\
            ,emp_transport_driver.id as emp_transport_driver_id,emp_transport_driver.name as emp_transport_driver_name,fleet_vehicle.id as fleet_vehicle_id,fleet_vehicle.taq_number as fleet_vehicle_sticker\
            ,route_table.id as route_tbl_id,route_table.route_name as route_tbl_name,invoice.id as invoice_id,invoice.name as cust_inv_no,tm_table.payment,tm_table.agreement_type as agreement_type\
            ,tm_table.customer_ref as customer_reference,partner_type.name as partner_type_name,cpm.payment_method_name as payment_method_name,tm_table.vehicle_type_domain_id as domain_id,vtd.name as domain_name\
            ,tm_table.fleet_type_transport as vehicle_type_id,vtt.vehicle_type_name as vehicle_type_name  FROM " + table_name + \
            " LEFT JOIN bsg_route_waypoints from_route_waypoint ON tm_table.form_transport=from_route_waypoint.id\
             LEFT JOIN hr_employee emp_driver ON tm_table.driver=emp_driver.id\
             LEFT JOIN bsg_fuel_expense_method fuel_exp_amt ON tm_table.display_expense_mthod_id = fuel_exp_amt.id\
             LEFT JOIN res_partner partner ON tm_table.customer = partner.id\
             LEFT JOIN bsg_route_waypoints to_route_waypoint ON tm_table.to_transport = to_route_waypoint.id\
             LEFT JOIN hr_employee emp_transport_driver ON tm_table.transportation_driver=emp_transport_driver.id\
             LEFT JOIN fleet_vehicle fleet_vehicle ON tm_table.transportation_vehicle=fleet_vehicle.id\
             LEFT JOIN bsg_route route_table ON tm_table.route_id=route_table.id\
             LEFT JOIN account_move invoice ON tm_table.invoice_id=invoice.id\
             LEFT JOIN partner_type ON tm_table.partner_types=partner_type.id\
             LEFT JOIN cargo_payment_method cpm ON tm_table.payment_method=cpm.id\
             LEFT JOIN vehicle_type_domain vtd ON tm_table.vehicle_type_domain_id=vtd.id\
             LEFT JOIN bsg_vehicle_type_table vtt ON tm_table.fleet_type_transport=vtt.id\
             WHERE vtd.name != 'Carrier' and (tm_table.order_date >= '%s') AND (tm_table.order_date <= '%s') %s %s %s %s %s %s %s %s %s %s %s %s" % (
                wiz_data.form, wiz_data.to, tm_state_cond, filter_customers, from_branch_cond, to_branch_cond,
                users_cond,
                vehicles_cond, payment_method_cond, driver_cond, from_bx_cond, to_bx_cond,domain_cond,vehicle_type_cond))

        result = self._cr.fetchall()

        transport_lines = pd.DataFrame(list(result))
        transport_lines = transport_lines.rename(
            columns={0: 'tm_id', 1: 'tm_transportation_no', 2: 'tm_order_date', 3: 'tm_customers',
                     4: 'tm_from_transport',
                     5: 'tm_to_transport', 6: 'tm_total_before_taxes', 7: 'tm_tax_amount', 8: 'tm_total_amount',
                     9: 'tm_driver_no',
                     10: 'tm_transportation_driver', 11: 'tm_transportation_vehicle', 12: 'tm_route_id',
                     13: 'tm_display_expense_method_id',
                     14: 'tm_display_expense_type', 15: 'tm_trip_distance', 16: 'tm_extra_distance', 17: 'tm_reason',
                     18: 'tm_total_distance',
                     19: 'tm_total_fuel_amount', 20: 'tm_total_reward_amount', 21: 'tm_state', 22: 'tm_create_uid',
                     23: 'tm_invoice_id',
                     24: 'tm_payment_method', 25: 'tm_driver', 26: 'tm_loading_date', 27: 'tm_arrival_date',
                     28: 'route_waypoint_id',
                     29: 'route_waypoint_from_branch_id', 30: 'emp_driver_id', 31: 'emp_driver_rewards',
                     32: 'fuel_exp_amt_id', 33: 'full_load_amt',
                     34: 'amt_full_wo_reward', 35: 'empty_load_amt', 36: 'amt_empty_wo_reward', 37: 'partner_id',
                     38: 'partner_name', 39: 'from_route_waypoint_name',
                     40: 'to_route_waypoint_id', 41: 'to_route_waypoint_name', 42: 'emp_transport_driver_id',
                     43: 'emp_transport_driver_name', 44: 'fleet_vehicle_id',
                     45: 'fleet_vehicle_sticker', 46: 'route_tbl_id', 47: 'route_tbl_name', 48: 'invoice_id',
                     49: 'cust_inv_no', 50: 'vendor_payment_id', 51: 'agreement_type', 52: 'customer_reference',
                     53: 'partner_type_name', 54: 'payment_method_name',55:'tm_domain_id',56:'domain_name',57:'vehicle_type_id',
                     58:'vehicle_type_name'})

        letters = list(string.ascii_uppercase)

        if wiz_data.grouping_by == 'all':

            worksheet.merge_range('A1:H1', "Bx Information Report", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col+1, 'التاريخ', main_heading1)
            worksheet.write(row, col+2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col+3, 'اسم العميل', main_heading1)
            worksheet.write(row, col+4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col+5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col+6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col+7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col+8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col+9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col+10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col+11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col+12, 'كود السائق', main_heading1)
            worksheet.write(row, col+13, 'اسم السائق', main_heading1)
            worksheet.write(row, col+14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col+15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col+16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col+17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col+18, 'خط السير', main_heading1)
            worksheet.write(row, col+19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col+20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col+21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col+22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col+23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col+24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col+25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col+26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col+27, 'السبب', main_heading1)
            worksheet.write(row, col+28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col+29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col+30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col+31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col+32, 'الحالة ', main_heading1)
            worksheet.write(row, col+33, 'المستخدم', main_heading1)
            worksheet.write(row, col+34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col+35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col+36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col+37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col+38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col+39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col+40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col+41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col+42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col+43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col+44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col+1, 'Date', main_heading1)
            worksheet.write(row, col+2, 'Partner Type', main_heading1)
            worksheet.write(row, col+3, 'Customer Name', main_heading1)
            worksheet.write(row, col+4, 'Payment Method', main_heading1)
            worksheet.write(row, col+5, 'From Branch', main_heading1)
            worksheet.write(row, col+6, 'To Branch', main_heading1)
            worksheet.write(row, col+7, 'Agreement Type', main_heading1)
            worksheet.write(row, col+8, 'Customer Reference', main_heading1)
            worksheet.write(row, col+9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col+10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col+11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col+12, 'Employee ID', main_heading1)
            worksheet.write(row, col+13, 'Driver Name', main_heading1)
            worksheet.write(row, col+14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col+15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col+16, 'Domain Name', main_heading1)
            worksheet.write(row, col+17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col+18, 'Route Name', main_heading1)
            worksheet.write(row, col+19, 'Loading Date', main_heading1)
            worksheet.write(row, col+20, 'Arrival Date', main_heading1)
            worksheet.write(row, col+21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col+22, 'Truck Load', main_heading1)
            worksheet.write(row, col+23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col+24, 'Trip Distance', main_heading1)
            worksheet.write(row, col+25, 'Extra Distance', main_heading1)
            worksheet.write(row, col+26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col+27, 'Reason', main_heading1)
            worksheet.write(row, col+28, 'Total Distance', main_heading1)
            worksheet.write(row, col+29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col+30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col+31, 'Total Amt', main_heading1)
            worksheet.write(row, col+32, 'State', main_heading1)
            worksheet.write(row, col+33, 'User', main_heading1)
            worksheet.write(row, col+34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col+35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col+36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col+37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col+38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col+39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col+40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col+41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col+42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col+43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col+44, 'Vendor Receipt Voucher', main_heading1)

            row += 1

            worksheet.set_column('A:AB', 20)



            total = 0
            total_invoice_amount_before_tax = 0
            total_tax = 0
            total_invoice_amount = 0
            total_trip_distance = 0
            total_extra_distance = 0
            total_extra_distance_amount = 0
            sum_total_distance = 0
            sum_total_fuel_expense = 0
            sum_total_reward_amount_backend = 0
            sum_total_amount = 0
            transport_lines = transport_lines.fillna(0)
            for index, value in transport_lines.iterrows():
                truck_load = ""
                if value['tm_total_amount'] > 0.00:
                    truck_load = 'full'
                else:
                    truck_load = 'empty'
                extra_distance_amount = 0
                if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value['tm_route_id']:
                    if value['tm_display_expense_type'] in ['km', 'hybrid']:
                        if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery', 'by_delivery_b',
                                                                                           'by_revenue']:
                            extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                        else:
                            extra_distance_amount = round(value['tm_extra_distance'] * value['amt_full_wo_reward'])
                        if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery', 'by_delivery_b',
                                                                                           'by_revenue']:
                            extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                        else:
                            extra_distance_amount = round(value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                loading_date = " "
                if value['tm_loading_date']:
                    df_loading_date = value['tm_loading_date']
                    loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                    loading_date_dt = loading_date_ts.to_pydatetime()
                    loading_date = loading_date_dt + timedelta(hours=3)

                arrival_date = " "
                if value['tm_arrival_date']:
                    df_arrival_date = value['tm_arrival_date']
                    arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                    arrival_date_dt = arrival_date_ts.to_pydatetime()
                    arrival_date = arrival_date_dt + timedelta(hours=3)

                trans_vehicle_id = self.env['fleet.vehicle'].search([('id', '=', int(value['tm_transportation_vehicle']))],
                                                                    limit=1)
                # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                    [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                customer_invoice_number = ""
                inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                if inv_id:
                    customer_invoice_number = inv_id.number

                customer_receipt_voucher = ""
                customer_receipt_voucher_date = ""
                if inv_id.payment_ids:
                    customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                    if inv_id.payment_ids.mapped('payment_date'):
                        customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                customer_credit_notes = ""
                customer_payment_voucher = ""
                refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                    force_company=self.env.user.company_id.id,
                    company_id=self.env.user.company_id.id).search(
                    [('return_customer_tranport_id', '=', int(value['tm_id']))])
                if refund_customer_invoice_ids:
                    customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                    for refund_customer_invoice_id in refund_customer_invoice_ids:
                        if refund_customer_invoice_id.payment_ids:
                            customer_payment_voucher = refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                vendor_payment_voucher = ""
                vendor_bill_no = ""
                vendor_payment_id = self.env['account.payment'].search([('id', '=', int(value['vendor_payment_id']))])
                if vendor_payment_id:
                    vendor_payment_voucher = vendor_payment_id.display_name
                    if vendor_payment_id.invoice_ids:
                        vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                vendor_refund_number = ""
                vendor_receipt_voucher = ""
                refund_invoice_ids = self.env['account.move'].sudo().with_context(
                    force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                    [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                if refund_invoice_ids:
                    vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                    for refund_invoice_id in refund_invoice_ids:
                        if refund_invoice_id.payment_ids:
                            vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                bx_credit_customer_collection = ""
                bx_cc_status=""
                tm_line_ids = self.env['transport.management.line'].sudo().search(
                    [('transport_management', '=', int(value['tm_id']))])
                if tm_line_ids:
                    if tm_line_ids.mapped('bx_credit_collection_ids'):
                        bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                        bx_credit_customer_collection = bx_cc_id.name
                        bx_cc_status = bx_cc_id.state

                worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                total_invoice_amount_before_tax += value['tm_total_before_taxes']
                worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                total_tax += value['tm_tax_amount']
                worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                total_invoice_amount += value['tm_total_amount']
                if value['tm_driver_no']:
                    worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                if value['emp_transport_driver_name']:
                    worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                if value['fleet_vehicle_sticker']:
                    worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                if trans_vehicle_id.model_id.display_name:
                    worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name), main_data)
                if value['domain_name']:
                    worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                if value['vehicle_type_name']:
                    worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                if value['route_tbl_name']:
                    worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                worksheet.write_string(row, col + 19, str(loading_date), main_data)
                worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                if fuel_expense_method_id.display_name:
                    worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                worksheet.write_string(row, col + 22, str(truck_load), main_data)
                if value['tm_display_expense_type']:
                    worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                total_trip_distance += value['tm_trip_distance']
                worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                total_extra_distance += value['tm_extra_distance']
                worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                total_extra_distance_amount += extra_distance_amount
                if value['tm_reason']:
                    worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                sum_total_distance += value['tm_total_distance']
                worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                sum_total_fuel_expense += value['tm_total_fuel_amount']
                worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                sum_total_reward_amount_backend += value['tm_total_reward_amount']
                worksheet.write_number(row, col + 31,
                                       float(
                                           value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                       main_data)
                sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                if not wiz_data.state:
                    if not wiz_data.include_cancel:
                        if value['tm_state'] != 'cancel':
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                    else:
                        worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                else:
                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                row += 1
                total += 1
            worksheet.write(row, col, 'Total', main_heading1)
            worksheet.write_number(row, col + 1, total, main_heading)
            worksheet.write(row, col + 2, 'المجموع', main_heading1)
            worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
            worksheet.write_number(row, col + 10, total_tax, main_heading)
            worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
            worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
            worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
            worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
            worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
            worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
            worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
            worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
            row += 1
        if wiz_data.grouping_by == 'by_branch_from':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Branch From", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_branch_from = transport_lines.groupby(['from_route_waypoint_name'])
            if transport_lines_group_by_branch_from:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_branch_from,df_branch_from in transport_lines_group_by_branch_from:
                    worksheet.write(row, col, 'Branch From', main_heading1)
                    worksheet.write_string(row, col + 1, str(key_branch_from), main_heading)
                    worksheet.write(row, col + 2, 'فرع الشحن', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax=0
                    total_tax=0
                    total_invoice_amount=0
                    total_trip_distance=0
                    total_extra_distance=0
                    total_extra_distance_amount=0
                    sum_total_distance=0
                    sum_total_fuel_expense=0
                    sum_total_reward_amount_backend=0
                    sum_total_amount=0
                    for index, value in df_branch_from.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value['tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search([('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_branch_to':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Branch TO", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_branch_to = transport_lines.groupby(['to_route_waypoint_name'])
            if transport_lines_group_by_branch_to:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_branch_to,df_branch_to in transport_lines_group_by_branch_to:
                    worksheet.write(row, col, 'Branch TO', main_heading1)
                    worksheet.write_string(row, col + 1, str(key_branch_to), main_heading)
                    worksheet.write(row, col + 2, 'فرع الوصول', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_branch_to.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_vehicle':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Vehicle", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_vehicle = transport_lines.groupby(['tm_transportation_vehicle'])
            if transport_lines_group_by_vehicle:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_vehicle,df_vehicle in transport_lines_group_by_vehicle:
                    trans_vehicle_id = self.env['fleet.vehicle'].search([('id', '=', int(key_vehicle))], limit=1)
                    worksheet.write(row, col, 'Vehicle Name', main_heading1)
                    worksheet.write_string(row, col + 1, str(trans_vehicle_id.model_id.display_name), main_heading)
                    worksheet.write(row, col + 2, 'اسم الشاحنة', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_vehicle.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_customer':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Customer", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_customer = transport_lines.groupby(['partner_name'])
            if transport_lines_group_by_customer:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_customer,df_customer in transport_lines_group_by_customer:
                    worksheet.write(row, col, 'Customer Name', main_heading1)
                    worksheet.write_string(row, col + 1,str(key_customer), main_heading)
                    worksheet.write(row, col + 2, 'اسم العميل', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_customer.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_payment_method':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Payment Method", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_payment_method = transport_lines.groupby(['payment_method_name'])
            if transport_lines_group_by_payment_method:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_payment_method, df_payment_method in transport_lines_group_by_payment_method:
                    worksheet.write(row, col, 'Payment Method', main_heading1)
                    worksheet.write_string(row, col + 1, str(key_payment_method), main_heading)
                    worksheet.write(row, col + 2, 'طريقة الدفع', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_payment_method.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_created_by':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Payment Method", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_creator = transport_lines.groupby(['tm_create_uid'])
            if transport_lines_group_by_creator:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_creator, df_creator in transport_lines_group_by_creator:
                    create_uid = self.env['res.users'].search([('id', '=', int(key_creator))], limit=1)
                    worksheet.write(row, col, 'Creator', main_heading1)
                    worksheet.write_string(row, col + 1, str(create_uid.name), main_heading)
                    worksheet.write(row, col + 2, 'المستخدم', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_creator.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_driver_name':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Driver Name", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_driver = transport_lines.groupby(['emp_transport_driver_name'])
            if transport_lines_group_by_driver:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_driver, df_driver in transport_lines_group_by_driver:
                    worksheet.write(row, col, 'Driver Name', main_heading1)
                    worksheet.write_string(row, col + 1, str(key_driver), main_heading)
                    worksheet.write(row, col + 2, 'اسم السائق', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_driver.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_state':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By State", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_state = transport_lines.groupby(['tm_state'])
            if transport_lines_group_by_state:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_state, df_state in transport_lines_group_by_state:
                    worksheet.write(row, col, 'State', main_heading1)
                    worksheet.write_string(row, col + 1, str(key_state), main_heading)
                    worksheet.write(row, col + 2, 'الحالة', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_state.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_domain_name':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Domain Name", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_domain = transport_lines.groupby(['domain_name'])
            if transport_lines_group_by_domain:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_domain, df_domain in transport_lines_group_by_domain:
                    worksheet.write(row, col, 'Domain Name', main_heading1)
                    if key_domain:
                        worksheet.write_string(row, col + 1, str(key_domain), main_heading)
                    else:
                        worksheet.write_string(row, col + 1,"Undefined", main_heading)
                    worksheet.write(row, col + 2, 'اسم النطاق', main_heading1)
                    row += 1
                    total=0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_domain.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                    refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1
        if wiz_data.grouping_by == 'by_vehicle_type':

            worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Vehicle Type", merge_format)

            worksheet.write(row, col, 'رقم الرحلة', main_heading1)
            worksheet.write(row, col + 1, 'التاريخ', main_heading1)
            worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
            worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
            worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
            worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
            worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
            worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
            worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
            worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
            worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
            worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
            worksheet.write(row, col + 12, 'كود السائق', main_heading1)
            worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
            worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
            worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
            worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
            worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
            worksheet.write(row, col + 18, 'خط السير', main_heading1)
            worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
            worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
            worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
            worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
            worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
            worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
            worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
            worksheet.write(row, col + 27, 'السبب', main_heading1)
            worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
            worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
            worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
            worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
            worksheet.write(row, col + 32, 'الحالة ', main_heading1)
            worksheet.write(row, col + 33, 'المستخدم', main_heading1)
            worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
            worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
            worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
            worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
            worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
            worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
            worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
            worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
            worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

            row += 1

            worksheet.write(row, col, 'Bx Agreement', main_heading1)
            worksheet.write(row, col + 1, 'Date', main_heading1)
            worksheet.write(row, col + 2, 'Partner Type', main_heading1)
            worksheet.write(row, col + 3, 'Customer Name', main_heading1)
            worksheet.write(row, col + 4, 'Payment Method', main_heading1)
            worksheet.write(row, col + 5, 'From Branch', main_heading1)
            worksheet.write(row, col + 6, 'To Branch', main_heading1)
            worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
            worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
            worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
            worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
            worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
            worksheet.write(row, col + 12, 'Employee ID', main_heading1)
            worksheet.write(row, col + 13, 'Driver Name', main_heading1)
            worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
            worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
            worksheet.write(row, col + 16, 'Domain Name', main_heading1)
            worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
            worksheet.write(row, col + 18, 'Route Name', main_heading1)
            worksheet.write(row, col + 19, 'Loading Date', main_heading1)
            worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
            worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
            worksheet.write(row, col + 22, 'Truck Load', main_heading1)
            worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
            worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
            worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
            worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
            worksheet.write(row, col + 27, 'Reason', main_heading1)
            worksheet.write(row, col + 28, 'Total Distance', main_heading1)
            worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
            worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
            worksheet.write(row, col + 31, 'Total Amt', main_heading1)
            worksheet.write(row, col + 32, 'State', main_heading1)
            worksheet.write(row, col + 33, 'User', main_heading1)
            worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
            worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
            worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
            worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
            worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
            worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
            worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
            worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
            worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
            worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
            worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

            row += 1
            worksheet.set_column('A:AB', 20)

            transport_lines = transport_lines.fillna(0)
            transport_lines_group_by_vehicle_type = transport_lines.groupby(['vehicle_type_name'])
            if transport_lines_group_by_vehicle_type:
                grand_total = 0
                grand_total_invoice_amount_before_tax = 0
                grand_total_tax = 0
                grand_total_invoice_amount = 0
                grand_total_trip_distance = 0
                grand_total_extra_distance = 0
                grand_total_extra_distance_amount = 0
                grand_sum_total_distance = 0
                grand_sum_total_fuel_expense = 0
                grand_sum_total_reward_amount_backend = 0
                grand_sum_total_amount = 0
                for key_vehicle_type, df_vehicle_type in transport_lines_group_by_vehicle_type:
                    worksheet.write(row, col, 'Vehicle Type Name', main_heading1)
                    if key_vehicle_type:
                        worksheet.write_string(row, col + 1, str(key_vehicle_type), main_heading)
                    else:
                        worksheet.write_string(row, col + 1, "Undefined", main_heading)
                    worksheet.write(row, col + 2, 'نوع السيارة', main_heading1)
                    row += 1
                    total = 0
                    total_invoice_amount_before_tax = 0
                    total_tax = 0
                    total_invoice_amount = 0
                    total_trip_distance = 0
                    total_extra_distance = 0
                    total_extra_distance_amount = 0
                    sum_total_distance = 0
                    sum_total_fuel_expense = 0
                    sum_total_reward_amount_backend = 0
                    sum_total_amount = 0
                    for index, value in df_vehicle_type.iterrows():
                        truck_load = ""
                        if value['tm_total_amount'] > 0.00:
                            truck_load = 'full'
                        else:
                            truck_load = 'empty'

                        extra_distance_amount = 0
                        if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                            'tm_route_id']:
                            if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['full_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                   'by_delivery_b',
                                                                                                   'by_revenue']:
                                    extra_distance_amount = round(value['tm_extra_distance'] * value['empty_load_amt'])
                                else:
                                    extra_distance_amount = round(
                                        value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                        loading_date = " "
                        if value['tm_loading_date']:
                            df_loading_date = value['tm_loading_date']
                            loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                            loading_date_dt = loading_date_ts.to_pydatetime()
                            loading_date = loading_date_dt + timedelta(hours=3)

                        arrival_date = " "
                        if value['tm_arrival_date']:
                            df_arrival_date = value['tm_arrival_date']
                            arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                            arrival_date_dt = arrival_date_ts.to_pydatetime()
                            arrival_date = arrival_date_dt + timedelta(hours=3)

                        trans_vehicle_id = self.env['fleet.vehicle'].search(
                            [('id', '=', int(value['tm_transportation_vehicle']))],
                            limit=1)
                        # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                        create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))], limit=1)
                        fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                            [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                        customer_invoice_number = ""
                        inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                        if inv_id:
                            customer_invoice_number = inv_id.number

                        customer_receipt_voucher = ""
                        customer_receipt_voucher_date = ""
                        if inv_id.payment_ids:
                            customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                            if inv_id.payment_ids.mapped('payment_date'):
                                customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                        customer_credit_notes = ""
                        customer_payment_voucher = ""
                        refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id,
                            company_id=self.env.user.company_id.id).search(
                            [('return_customer_tranport_id', '=', int(value['tm_id']))])
                        if refund_customer_invoice_ids:
                            customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                            for refund_customer_invoice_id in refund_customer_invoice_ids:
                                if refund_customer_invoice_id.payment_ids:
                                    customer_payment_voucher = \
                                        refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                        vendor_payment_voucher = ""
                        vendor_bill_no = ""
                        vendor_payment_id = self.env['account.payment'].search(
                            [('id', '=', int(value['vendor_payment_id']))])
                        if vendor_payment_id:
                            vendor_payment_voucher = vendor_payment_id.display_name
                            if vendor_payment_id.invoice_ids:
                                vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                        vendor_refund_number = ""
                        vendor_receipt_voucher = ""
                        refund_invoice_ids = self.env['account.move'].sudo().with_context(
                            force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search(
                            [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                        if refund_invoice_ids:
                            vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                            for refund_invoice_id in refund_invoice_ids:
                                if refund_invoice_id.payment_ids:
                                    vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                        bx_credit_customer_collection = ""
                        bx_cc_status = ""
                        tm_line_ids = self.env['transport.management.line'].sudo().search(
                            [('transport_management', '=', int(value['tm_id']))])
                        if tm_line_ids:
                            if tm_line_ids.mapped('bx_credit_collection_ids'):
                                bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                bx_credit_customer_collection = bx_cc_id.name
                                bx_cc_status = bx_cc_id.state
                        worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                        worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                        worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                        worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                        worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                        worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                        worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                        worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                        worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                        total_invoice_amount_before_tax += value['tm_total_before_taxes']
                        worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                        total_tax += value['tm_tax_amount']
                        worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                        total_invoice_amount += value['tm_total_amount']
                        if value['tm_driver_no']:
                            worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                        if value['emp_transport_driver_name']:
                            worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']), main_data)
                        if value['fleet_vehicle_sticker']:
                            worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                        if trans_vehicle_id.model_id.display_name:
                            worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                   main_data)
                        if value['domain_name']:
                            worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                        if value['vehicle_type_name']:
                            worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                        if value['route_tbl_name']:
                            worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                        worksheet.write_string(row, col + 19, str(loading_date), main_data)
                        worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                        if fuel_expense_method_id.display_name:
                            worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name), main_data)
                        worksheet.write_string(row, col + 22, str(truck_load), main_data)
                        if value['tm_display_expense_type']:
                            worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                        worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                        total_trip_distance += value['tm_trip_distance']
                        worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                        total_extra_distance += value['tm_extra_distance']
                        worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                        total_extra_distance_amount += extra_distance_amount
                        if value['tm_reason']:
                            worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                        worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                        sum_total_distance += value['tm_total_distance']
                        worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                        sum_total_fuel_expense += value['tm_total_fuel_amount']
                        worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                        sum_total_reward_amount_backend += value['tm_total_reward_amount']
                        worksheet.write_number(row, col + 31,
                                               float(
                                                   value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                               main_data)
                        sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                        if not wiz_data.state:
                            if not wiz_data.include_cancel:
                                if value['tm_state'] != 'cancel':
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        else:
                            worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                        worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                        worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                        worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                        worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                        worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                        worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                        worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                        worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                        worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                        worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                        worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                        worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                        row += 1
                        total += 1
                    worksheet.write(row, col, 'Total', main_heading1)
                    worksheet.write_number(row, col + 1, total, main_heading)
                    grand_total += total
                    worksheet.write(row, col + 2, 'المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                    grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                    worksheet.write_number(row, col + 10, total_tax, main_heading)
                    grand_total_tax += total_tax
                    worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                    grand_total_invoice_amount += total_invoice_amount
                    worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                    grand_total_trip_distance += total_trip_distance
                    worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                    grand_total_extra_distance += total_extra_distance
                    worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                    grand_total_extra_distance_amount += grand_total_extra_distance_amount
                    worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                    grand_sum_total_distance += sum_total_distance
                    worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                    grand_sum_total_fuel_expense += sum_total_fuel_expense
                    worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                    grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                    worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                    grand_sum_total_amount += sum_total_amount
                    row += 1
                worksheet.write(row, col, 'Grand Total', main_heading1)
                worksheet.write_number(row, col + 1, grand_total, main_heading)
                worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                row += 1

        if wiz_data.grouping_by == 'by_period':
            if not wiz_data.period_grouping_by:
                worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Date", merge_format)

                worksheet.write(row, col, 'رقم الرحلة', main_heading1)
                worksheet.write(row, col + 1, 'التاريخ', main_heading1)
                worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
                worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
                worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
                worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
                worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
                worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
                worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
                worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
                worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
                worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
                worksheet.write(row, col + 12, 'كود السائق', main_heading1)
                worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
                worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
                worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
                worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
                worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
                worksheet.write(row, col + 18, 'خط السير', main_heading1)
                worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
                worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
                worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
                worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
                worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
                worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
                worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
                worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write(row, col + 27, 'السبب', main_heading1)
                worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
                worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
                worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
                worksheet.write(row, col + 32, 'الحالة ', main_heading1)
                worksheet.write(row, col + 33, 'المستخدم', main_heading1)
                worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
                worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
                worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
                worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
                worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
                worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
                worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
                worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
                worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
                worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
                worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

                row += 1

                worksheet.write(row, col, 'Bx Agreement', main_heading1)
                worksheet.write(row, col + 1, 'Date', main_heading1)
                worksheet.write(row, col + 2, 'Partner Type', main_heading1)
                worksheet.write(row, col + 3, 'Customer Name', main_heading1)
                worksheet.write(row, col + 4, 'Payment Method', main_heading1)
                worksheet.write(row, col + 5, 'From Branch', main_heading1)
                worksheet.write(row, col + 6, 'To Branch', main_heading1)
                worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
                worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
                worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
                worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
                worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
                worksheet.write(row, col + 12, 'Employee ID', main_heading1)
                worksheet.write(row, col + 13, 'Driver Name', main_heading1)
                worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
                worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
                worksheet.write(row, col + 16, 'Domain Name', main_heading1)
                worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
                worksheet.write(row, col + 18, 'Route Name', main_heading1)
                worksheet.write(row, col + 19, 'Loading Date', main_heading1)
                worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
                worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
                worksheet.write(row, col + 22, 'Truck Load', main_heading1)
                worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
                worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
                worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
                worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
                worksheet.write(row, col + 27, 'Reason', main_heading1)
                worksheet.write(row, col + 28, 'Total Distance', main_heading1)
                worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
                worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
                worksheet.write(row, col + 31, 'Total Amt', main_heading1)
                worksheet.write(row, col + 32, 'State', main_heading1)
                worksheet.write(row, col + 33, 'User', main_heading1)
                worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
                worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
                worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
                worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
                worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
                worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
                worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
                worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
                worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
                worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
                worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

                row += 1
                worksheet.set_column('A:AB', 20)

                transport_lines = transport_lines.fillna(0)
                transport_lines_group_by_date = transport_lines.groupby(['tm_order_date'])
                if transport_lines_group_by_date:
                    grand_total = 0
                    grand_total_invoice_amount_before_tax = 0
                    grand_total_tax = 0
                    grand_total_invoice_amount = 0
                    grand_total_trip_distance = 0
                    grand_total_extra_distance = 0
                    grand_total_extra_distance_amount = 0
                    grand_sum_total_distance = 0
                    grand_sum_total_fuel_expense = 0
                    grand_sum_total_reward_amount_backend = 0
                    grand_sum_total_amount = 0
                    for key_date, df_date in transport_lines_group_by_date:
                        worksheet.write(row, col, 'Date', main_heading1)
                        worksheet.write_string(row, col + 1, str(key_date), main_heading)
                        worksheet.write(row, col + 2, 'التاريخ', main_heading1)
                        row += 1
                        total=0
                        total_invoice_amount_before_tax = 0
                        total_tax = 0
                        total_invoice_amount = 0
                        total_trip_distance = 0
                        total_extra_distance = 0
                        total_extra_distance_amount = 0
                        sum_total_distance = 0
                        sum_total_fuel_expense = 0
                        sum_total_reward_amount_backend = 0
                        sum_total_amount = 0
                        for index, value in df_date.iterrows():
                            truck_load = ""
                            if value['tm_total_amount'] > 0.00:
                                truck_load = 'full'
                            else:
                                truck_load = 'empty'

                            extra_distance_amount = 0
                            if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                                'tm_route_id']:
                                if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                    if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                       'by_delivery_b',
                                                                                                       'by_revenue']:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['full_load_amt'])
                                    else:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                    if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                       'by_delivery_b',
                                                                                                       'by_revenue']:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['empty_load_amt'])
                                    else:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                            loading_date = " "
                            if value['tm_loading_date']:
                                df_loading_date = value['tm_loading_date']
                                loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                                loading_date_dt = loading_date_ts.to_pydatetime()
                                loading_date = loading_date_dt + timedelta(hours=3)

                            arrival_date = " "
                            if value['tm_arrival_date']:
                                df_arrival_date = value['tm_arrival_date']
                                arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                                arrival_date_dt = arrival_date_ts.to_pydatetime()
                                arrival_date = arrival_date_dt + timedelta(hours=3)

                            trans_vehicle_id = self.env['fleet.vehicle'].search(
                                [('id', '=', int(value['tm_transportation_vehicle']))],
                                limit=1)
                            # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                            create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))],
                                                                      limit=1)
                            fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                                [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                            customer_invoice_number = ""
                            inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                            if inv_id:
                                customer_invoice_number = inv_id.number

                            customer_receipt_voucher = ""
                            customer_receipt_voucher_date = ""
                            if inv_id.payment_ids:
                                customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                                if inv_id.payment_ids.mapped('payment_date'):
                                    customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                            customer_credit_notes = ""
                            customer_payment_voucher = ""
                            refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                                force_company=self.env.user.company_id.id,
                                company_id=self.env.user.company_id.id).search(
                                [('return_customer_tranport_id', '=', int(value['tm_id']))])
                            if refund_customer_invoice_ids:
                                customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                                for refund_customer_invoice_id in refund_customer_invoice_ids:
                                    if refund_customer_invoice_id.payment_ids:
                                        customer_payment_voucher = \
                                        refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                            vendor_payment_voucher = ""
                            vendor_bill_no = ""
                            vendor_payment_id = self.env['account.payment'].search(
                                [('id', '=', int(value['vendor_payment_id']))])
                            if vendor_payment_id:
                                vendor_payment_voucher = vendor_payment_id.display_name
                                if vendor_payment_id.invoice_ids:
                                    vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                            vendor_refund_number = ""
                            vendor_receipt_voucher = ""
                            refund_invoice_ids = self.env['account.move'].sudo().with_context(
                                force_company=self.env.user.company_id.id,
                                company_id=self.env.user.company_id.id).search(
                                [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                            if refund_invoice_ids:
                                vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                                for refund_invoice_id in refund_invoice_ids:
                                    if refund_invoice_id.payment_ids:
                                        vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                            bx_credit_customer_collection = ""
                            bx_cc_status = ""
                            tm_line_ids = self.env['transport.management.line'].sudo().search(
                                [('transport_management', '=', int(value['tm_id']))])
                            if tm_line_ids:
                                if tm_line_ids.mapped('bx_credit_collection_ids'):
                                    bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                    bx_credit_customer_collection = bx_cc_id.name
                                    bx_cc_status = bx_cc_id.state
                            worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                            worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                            worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                            worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                            worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                            worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                            worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                            worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                            worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                            worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                            total_invoice_amount_before_tax += value['tm_total_before_taxes']
                            worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                            total_tax += value['tm_tax_amount']
                            worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                            total_invoice_amount += value['tm_total_amount']
                            if value['tm_driver_no']:
                                worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                            if value['emp_transport_driver_name']:
                                worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']),
                                                       main_data)
                            if value['fleet_vehicle_sticker']:
                                worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                            if trans_vehicle_id.model_id.display_name:
                                worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                       main_data)
                            if value['domain_name']:
                                worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                            if value['vehicle_type_name']:
                                worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                            if value['route_tbl_name']:
                                worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                            worksheet.write_string(row, col + 19, str(loading_date), main_data)
                            worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                            if fuel_expense_method_id.display_name:
                                worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name),
                                                       main_data)
                            worksheet.write_string(row, col + 22, str(truck_load), main_data)
                            if value['tm_display_expense_type']:
                                worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                            worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                            total_trip_distance += value['tm_trip_distance']
                            worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                            total_extra_distance += value['tm_extra_distance']
                            worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                            total_extra_distance_amount += extra_distance_amount
                            if value['tm_reason']:
                                worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                            worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                            sum_total_distance += value['tm_total_distance']
                            worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                            sum_total_fuel_expense += value['tm_total_fuel_amount']
                            worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                            sum_total_reward_amount_backend += value['tm_total_reward_amount']
                            worksheet.write_number(row, col + 31,
                                                   float(
                                                       value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                                   main_data)
                            sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                            if not wiz_data.state:
                                if not wiz_data.include_cancel:
                                    if value['tm_state'] != 'cancel':
                                        worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                                else:
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                            worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                            worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                            worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                            worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                            worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                            worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                            worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                            worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                            worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                            worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                            worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                            row += 1
                            total += 1
                        worksheet.write(row, col, 'Total', main_heading1)
                        worksheet.write_number(row, col + 1, total, main_heading)
                        grand_total += total
                        worksheet.write(row, col + 2, 'المجموع', main_heading1)
                        worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                        grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                        worksheet.write_number(row, col + 10, total_tax, main_heading)
                        grand_total_tax += total_tax
                        worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                        grand_total_invoice_amount += total_invoice_amount
                        worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                        grand_total_trip_distance += total_trip_distance
                        worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                        grand_total_extra_distance += total_extra_distance
                        worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                        grand_total_extra_distance_amount += grand_total_extra_distance_amount
                        worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                        grand_sum_total_distance += sum_total_distance
                        worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                        grand_sum_total_fuel_expense += sum_total_fuel_expense
                        worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                        grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                        worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                        grand_sum_total_amount += sum_total_amount
                        row += 1
                    worksheet.write(row, col, 'Grand Total', main_heading1)
                    worksheet.write_number(row, col + 1, grand_total, main_heading)
                    worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                    worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                    worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                    worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                    worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                    worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                    worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                    worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                    worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                    worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                    row += 1
            else:
                worksheet.merge_range('A1:H1', "Bx Information Report Grouping By Date", merge_format)

                worksheet.write(row, col, 'رقم الرحلة', main_heading1)
                worksheet.write(row, col + 1, 'التاريخ', main_heading1)
                worksheet.write(row, col + 2, 'نوع الشريك', main_heading1)
                worksheet.write(row, col + 3, 'اسم العميل', main_heading1)
                worksheet.write(row, col + 4, 'طريقة الدفع', main_heading1)
                worksheet.write(row, col + 5, 'فرع الشحن', main_heading1)
                worksheet.write(row, col + 6, 'فرع الوصول', main_heading1)
                worksheet.write(row, col + 7, 'نوع الاتفاقية', main_heading1)
                worksheet.write(row, col + 8, 'مرجع العميل', main_heading1)
                worksheet.write(row, col + 9, 'قيمة الاتفاقية الضريبة', main_heading1)
                worksheet.write(row, col + 10, 'أجمالي الضريبة', main_heading1)
                worksheet.write(row, col + 11, 'اجمالي الاتفاقية', main_heading1)
                worksheet.write(row, col + 12, 'كود السائق', main_heading1)
                worksheet.write(row, col + 13, 'اسم السائق', main_heading1)
                worksheet.write(row, col + 14, 'استيكر الشاحنة', main_heading1)
                worksheet.write(row, col + 15, 'اسم الشاحنة', main_heading1)
                worksheet.write(row, col + 16, 'اسم النطاق', main_heading1)
                worksheet.write(row, col + 17, 'نوع السيارة', main_heading1)
                worksheet.write(row, col + 18, 'خط السير', main_heading1)
                worksheet.write(row, col + 19, 'تاريخ الانطلاق', main_heading1)
                worksheet.write(row, col + 20, 'تاريخ الوصول', main_heading1)
                worksheet.write(row, col + 21, 'طريقة احتساب مصاريف الطريق ', main_heading1)
                worksheet.write(row, col + 22, ' حمولة الشاحنة', main_heading1)
                worksheet.write(row, col + 23, 'نوع احتساب مصروف الطريق', main_heading1)
                worksheet.write(row, col + 24, 'مسافة خط السير', main_heading1)
                worksheet.write(row, col + 25, 'المسافة الإضافية', main_heading1)
                worksheet.write(row, col + 26, 'قيمة ديزل المسافة الإضافية', main_heading1)
                worksheet.write(row, col + 27, 'السبب', main_heading1)
                worksheet.write(row, col + 28, 'اجمالي المسافة', main_heading1)
                worksheet.write(row, col + 29, 'قيمة الديزل', main_heading1)
                worksheet.write(row, col + 30, 'قيمة مكافأة الحمولة', main_heading1)
                worksheet.write(row, col + 31, 'اجمالي مصروف الطريق', main_heading1)
                worksheet.write(row, col + 32, 'الحالة ', main_heading1)
                worksheet.write(row, col + 33, 'المستخدم', main_heading1)
                worksheet.write(row, col + 34, 'رقم فاتورة العميل', main_heading1)
                worksheet.write(row, col + 35, 'رقم الفاتورة المجمعة للعميل', main_heading1)
                worksheet.write(row, col + 36, 'حالة الفاتورة المجمعة للعميل', main_heading1)
                worksheet.write(row, col + 37, 'رقم سند القبض للعميل', main_heading1)
                worksheet.write(row, col + 38, 'تاريخ سند القبض للعميل', main_heading1)
                worksheet.write(row, col + 39, 'رقم فاتورة المرتجعة للعميل', main_heading1)
                worksheet.write(row, col + 40, ' رقم سند الصرف للعميل', main_heading1)
                worksheet.write(row, col + 41, 'رقم فاتورة المشتريات', main_heading1)
                worksheet.write(row, col + 42, 'رقم سند الصرف للمورد', main_heading1)
                worksheet.write(row, col + 43, 'رقم فاتورة المرتجع للمورد ', main_heading1)
                worksheet.write(row, col + 44, 'رقم سند القبض للمورد', main_heading1)

                row += 1

                worksheet.write(row, col, 'Bx Agreement', main_heading1)
                worksheet.write(row, col + 1, 'Date', main_heading1)
                worksheet.write(row, col + 2, 'Partner Type', main_heading1)
                worksheet.write(row, col + 3, 'Customer Name', main_heading1)
                worksheet.write(row, col + 4, 'Payment Method', main_heading1)
                worksheet.write(row, col + 5, 'From Branch', main_heading1)
                worksheet.write(row, col + 6, 'To Branch', main_heading1)
                worksheet.write(row, col + 7, 'Agreement Type', main_heading1)
                worksheet.write(row, col + 8, 'Customer Reference', main_heading1)
                worksheet.write(row, col + 9, 'Total Invoice Amt Before Tax', main_heading1)
                worksheet.write(row, col + 10, 'Total Tax Amt', main_heading1)
                worksheet.write(row, col + 11, 'Total Invoice Amt', main_heading1)
                worksheet.write(row, col + 12, 'Employee ID', main_heading1)
                worksheet.write(row, col + 13, 'Driver Name', main_heading1)
                worksheet.write(row, col + 14, 'Vehicle Sticker', main_heading1)
                worksheet.write(row, col + 15, 'Vehicle Name', main_heading1)
                worksheet.write(row, col + 16, 'Domain Name', main_heading1)
                worksheet.write(row, col + 17, 'Vehicle Type', main_heading1)
                worksheet.write(row, col + 18, 'Route Name', main_heading1)
                worksheet.write(row, col + 19, 'Loading Date', main_heading1)
                worksheet.write(row, col + 20, 'Arrival Date', main_heading1)
                worksheet.write(row, col + 21, 'Fuel Expense Method', main_heading1)
                worksheet.write(row, col + 22, 'Truck Load', main_heading1)
                worksheet.write(row, col + 23, 'Fuel Expense Type', main_heading1)
                worksheet.write(row, col + 24, 'Trip Distance', main_heading1)
                worksheet.write(row, col + 25, 'Extra Distance', main_heading1)
                worksheet.write(row, col + 26, 'Extra Distance Amt', main_heading1)
                worksheet.write(row, col + 27, 'Reason', main_heading1)
                worksheet.write(row, col + 28, 'Total Distance', main_heading1)
                worksheet.write(row, col + 29, 'Total Fuel Expense', main_heading1)
                worksheet.write(row, col + 30, 'Total Reward amount Backend', main_heading1)
                worksheet.write(row, col + 31, 'Total Amt', main_heading1)
                worksheet.write(row, col + 32, 'State', main_heading1)
                worksheet.write(row, col + 33, 'User', main_heading1)
                worksheet.write(row, col + 34, 'Customer Invoice No', main_heading1)
                worksheet.write(row, col + 35, 'Customer Credit Collection No', main_heading1)
                worksheet.write(row, col + 36, 'Customer Credit Collection No Status', main_heading1)
                worksheet.write(row, col + 37, 'Customer Receipt Voucher', main_heading1)
                worksheet.write(row, col + 38, 'Customer Receipt Voucher Date', main_heading1)
                worksheet.write(row, col + 39, 'Customer Credit Notes ', main_heading1)
                worksheet.write(row, col + 40, 'Customer payment Voucher', main_heading1)
                worksheet.write(row, col + 41, 'Vendor bill No', main_heading1)
                worksheet.write(row, col + 42, 'Vendor Payment Voucher No', main_heading1)
                worksheet.write(row, col + 43, 'Vendor Refund No. ', main_heading1)
                worksheet.write(row, col + 44, 'Vendor Receipt Voucher', main_heading1)

                row += 1
                worksheet.set_column('A:AB', 20)

                transport_lines = transport_lines.fillna(0)
                transport_lines_group_by_date = transport_lines.groupby(['tm_order_date'])
                if transport_lines_group_by_date:
                    grand_total = 0
                    grand_total_invoice_amount_before_tax = 0
                    grand_total_tax = 0
                    grand_total_invoice_amount = 0
                    grand_total_trip_distance = 0
                    grand_total_extra_distance = 0
                    grand_total_extra_distance_amount = 0
                    grand_sum_total_distance = 0
                    grand_sum_total_fuel_expense = 0
                    grand_sum_total_reward_amount_backend = 0
                    grand_sum_total_amount = 0
                    for key_date, df_date in transport_lines_group_by_date:
                        worksheet.write(row, col, 'Date', main_heading1)
                        worksheet.write_string(row, col + 1, str(key_date), main_heading)
                        worksheet.write(row, col + 2, 'التاريخ', main_heading1)
                        row += 1
                        total=0
                        total_invoice_amount_before_tax = 0
                        total_tax = 0
                        total_invoice_amount = 0
                        total_trip_distance = 0
                        total_extra_distance = 0
                        total_extra_distance_amount = 0
                        sum_total_distance = 0
                        sum_total_fuel_expense = 0
                        sum_total_reward_amount_backend = 0
                        sum_total_amount = 0
                        for index, value in df_date.iterrows():
                            truck_load = ""
                            if value['tm_total_amount'] > 0.00:
                                truck_load = 'full'
                            else:
                                truck_load = 'empty'

                            extra_distance_amount = 0
                            if value['tm_extra_distance'] and value['tm_display_expense_method_id'] and value[
                                'tm_route_id']:
                                if value['tm_display_expense_type'] in ['km', 'hybrid']:
                                    if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                       'by_delivery_b',
                                                                                                       'by_revenue']:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['full_load_amt'])
                                    else:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['amt_full_wo_reward'])
                                    if value['emp_driver_rewards'] and value['emp_driver_rewards'] in ['by_delivery',
                                                                                                       'by_delivery_b',
                                                                                                       'by_revenue']:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['empty_load_amt'])
                                    else:
                                        extra_distance_amount = round(
                                            value['tm_extra_distance'] * value['amt_empty_wo_reward'])

                            loading_date = " "
                            if value['tm_loading_date']:
                                df_loading_date = value['tm_loading_date']
                                loading_date_ts = pd._libs.tslibs.Timestamp(df_loading_date)
                                loading_date_dt = loading_date_ts.to_pydatetime()
                                loading_date = loading_date_dt + timedelta(hours=3)

                            arrival_date = " "
                            if value['tm_arrival_date']:
                                df_arrival_date = value['tm_arrival_date']
                                arrival_date_ts = pd._libs.tslibs.Timestamp(df_arrival_date)
                                arrival_date_dt = arrival_date_ts.to_pydatetime()
                                arrival_date = arrival_date_dt + timedelta(hours=3)

                            trans_vehicle_id = self.env['fleet.vehicle'].search(
                                [('id', '=', int(value['tm_transportation_vehicle']))],
                                limit=1)
                            # route_id = self.env['bsg_route'].search([('id','=',int(value['tm_route_id']))],limit=1)
                            create_uid = self.env['res.users'].search([('id', '=', int(value['tm_create_uid']))],
                                                                      limit=1)
                            fuel_expense_method_id = self.env['bsg.fuel.expense.method'].search(
                                [('id', '=', int(value['tm_display_expense_method_id']))], limit=1)

                            customer_invoice_number = ""
                            inv_id = self.env['account.move'].search([('id', '=', int(value['invoice_id']))])
                            if inv_id:
                                customer_invoice_number = inv_id.number

                            customer_receipt_voucher = ""
                            customer_receipt_voucher_date = ""
                            if inv_id.payment_ids:
                                customer_receipt_voucher = inv_id.payment_ids.mapped('display_name')[0]
                                if inv_id.payment_ids.mapped('payment_date'):
                                    customer_receipt_voucher_date = inv_id.payment_ids.mapped('payment_date')[0]

                            customer_credit_notes = ""
                            customer_payment_voucher = ""
                            refund_customer_invoice_ids = self.env['account.move'].sudo().with_context(
                                force_company=self.env.user.company_id.id,
                                company_id=self.env.user.company_id.id).search(
                                [('return_customer_tranport_id', '=', int(value['tm_id']))])
                            if refund_customer_invoice_ids:
                                customer_credit_notes = refund_customer_invoice_ids.mapped('display_name')[0]
                                for refund_customer_invoice_id in refund_customer_invoice_ids:
                                    if refund_customer_invoice_id.payment_ids:
                                        customer_payment_voucher = \
                                        refund_customer_invoice_id.payment_ids.mapped('display_name')[0]

                            vendor_payment_voucher = ""
                            vendor_bill_no = ""
                            vendor_payment_id = self.env['account.payment'].search(
                                [('id', '=', int(value['vendor_payment_id']))])
                            if vendor_payment_id:
                                vendor_payment_voucher = vendor_payment_id.display_name
                                if vendor_payment_id.invoice_ids:
                                    vendor_bill_no = vendor_payment_id.invoice_ids.mapped('display_name')[0]

                            vendor_refund_number = ""
                            vendor_receipt_voucher = ""
                            refund_invoice_ids = self.env['account.move'].sudo().with_context(
                                force_company=self.env.user.company_id.id,
                                company_id=self.env.user.company_id.id).search(
                                [('return_vendor_tranport_id', '=', int(value['tm_id']))])
                            if refund_invoice_ids:
                                vendor_refund_number = refund_invoice_ids.mapped('display_name')[0]
                                for refund_invoice_id in refund_invoice_ids:
                                    if refund_invoice_id.payment_ids:
                                        vendor_receipt_voucher = refund_invoice_id.payment_ids.mapped('display_name')[0]

                            bx_credit_customer_collection = ""
                            bx_cc_status = ""
                            tm_line_ids = self.env['transport.management.line'].sudo().search(
                                [('transport_management', '=', int(value['tm_id']))])
                            if tm_line_ids:
                                if tm_line_ids.mapped('bx_credit_collection_ids'):
                                    bx_cc_id = tm_line_ids.mapped('bx_credit_collection_ids')[0]
                                    bx_credit_customer_collection = bx_cc_id.name
                                    bx_cc_status = bx_cc_id.state
                            worksheet.write_string(row, col + 0, str(value['tm_transportation_no']), main_data)
                            worksheet.write_string(row, col + 1, str(value['tm_order_date']), main_data)
                            worksheet.write_string(row, col + 2, str(value['partner_type_name']), main_data)
                            worksheet.write_string(row, col + 3, str(value['partner_name']), main_data)
                            worksheet.write_string(row, col + 4, str(value['payment_method_name']), main_data)
                            worksheet.write_string(row, col + 5, str(value['from_route_waypoint_name']), main_data)
                            worksheet.write_string(row, col + 6, str(value['to_route_waypoint_name']), main_data)
                            worksheet.write_string(row, col + 7, str(value['agreement_type']), main_data)
                            worksheet.write_string(row, col + 8, str(value['customer_reference']), main_data)
                            worksheet.write_number(row, col + 9, float(value['tm_total_before_taxes']), main_data)
                            total_invoice_amount_before_tax += value['tm_total_before_taxes']
                            worksheet.write_number(row, col + 10, float(value['tm_tax_amount']), main_data)
                            total_tax += value['tm_tax_amount']
                            worksheet.write_number(row, col + 11, float(value['tm_total_amount']), main_data)
                            total_invoice_amount += value['tm_total_amount']
                            if value['tm_driver_no']:
                                worksheet.write_string(row, col + 12, str(value['tm_driver_no']), main_data)
                            if value['emp_transport_driver_name']:
                                worksheet.write_string(row, col + 13, str(value['emp_transport_driver_name']),
                                                       main_data)
                            if value['fleet_vehicle_sticker']:
                                worksheet.write_string(row, col + 14, str(value['fleet_vehicle_sticker']), main_data)
                            if trans_vehicle_id.model_id.display_name:
                                worksheet.write_string(row, col + 15, str(trans_vehicle_id.model_id.display_name),
                                                       main_data)
                            if value['domain_name']:
                                worksheet.write_string(row, col + 16, str(value['domain_name']), main_data)
                            if value['vehicle_type_name']:
                                worksheet.write_string(row, col + 17, str(value['vehicle_type_name']), main_data)
                            if value['route_tbl_name']:
                                worksheet.write_string(row, col + 18, str(value['route_tbl_name']), main_data)
                            worksheet.write_string(row, col + 19, str(loading_date), main_data)
                            worksheet.write_string(row, col + 20, str(arrival_date), main_data)
                            if fuel_expense_method_id.display_name:
                                worksheet.write_string(row, col + 21, str(fuel_expense_method_id.display_name),
                                                       main_data)
                            worksheet.write_string(row, col + 22, str(truck_load), main_data)
                            if value['tm_display_expense_type']:
                                worksheet.write_string(row, col + 23, str(value['tm_display_expense_type']), main_data)
                            worksheet.write_number(row, col + 24, float(value['tm_trip_distance']), main_data)
                            total_trip_distance += value['tm_trip_distance']
                            worksheet.write_number(row, col + 25, float(value['tm_extra_distance']), main_data)
                            total_extra_distance += value['tm_extra_distance']
                            worksheet.write_number(row, col + 26, float(extra_distance_amount), main_data)
                            total_extra_distance_amount += extra_distance_amount
                            if value['tm_reason']:
                                worksheet.write_string(row, col + 27, str(value['tm_reason']), main_data)
                            worksheet.write_number(row, col + 28, float(value['tm_total_distance']), main_data)
                            sum_total_distance += value['tm_total_distance']
                            worksheet.write_number(row, col + 29, float(value['tm_total_fuel_amount']), main_data)
                            sum_total_fuel_expense += value['tm_total_fuel_amount']
                            worksheet.write_number(row, col + 30, float(value['tm_total_reward_amount']), main_data)
                            sum_total_reward_amount_backend += value['tm_total_reward_amount']
                            worksheet.write_number(row, col + 31,
                                                   float(
                                                       value['tm_total_reward_amount'] + value['tm_total_fuel_amount']),
                                                   main_data)
                            sum_total_amount += (float(value['tm_total_reward_amount'] + value['tm_total_fuel_amount']))
                            if not wiz_data.state:
                                if not wiz_data.include_cancel:
                                    if value['tm_state'] != 'cancel':
                                        worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                                else:
                                    worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            else:
                                worksheet.write_string(row, col + 32, str(value['tm_state']), main_data)
                            worksheet.write_string(row, col + 33, str(create_uid.name), main_data)
                            worksheet.write_string(row, col + 34, str(customer_invoice_number), main_data)
                            worksheet.write_string(row, col + 35, str(bx_credit_customer_collection), main_data)
                            worksheet.write_string(row, col + 36, str(bx_cc_status), main_data)
                            worksheet.write_string(row, col + 37, str(customer_receipt_voucher), main_data)
                            worksheet.write_string(row, col + 38, str(customer_receipt_voucher_date), main_data)
                            worksheet.write_string(row, col + 39, str(customer_credit_notes), main_data)
                            worksheet.write_string(row, col + 40, str(customer_payment_voucher), main_data)
                            worksheet.write_string(row, col + 41, str(vendor_bill_no), main_data)
                            worksheet.write_string(row, col + 42, str(vendor_payment_voucher), main_data)
                            worksheet.write_string(row, col + 43, str(vendor_refund_number), main_data)
                            worksheet.write_string(row, col + 44, str(vendor_receipt_voucher), main_data)
                            row += 1
                            total += 1
                        worksheet.write(row, col, 'Total', main_heading1)
                        worksheet.write_number(row, col + 1, total, main_heading)
                        grand_total += total
                        worksheet.write(row, col + 2, 'المجموع', main_heading1)
                        worksheet.write_number(row, col + 9, total_invoice_amount_before_tax, main_heading)
                        grand_total_invoice_amount_before_tax += total_invoice_amount_before_tax
                        worksheet.write_number(row, col + 10, total_tax, main_heading)
                        grand_total_tax += total_tax
                        worksheet.write_number(row, col + 11, total_invoice_amount, main_heading)
                        grand_total_invoice_amount += total_invoice_amount
                        worksheet.write_number(row, col + 24, total_trip_distance, main_heading)
                        grand_total_trip_distance += total_trip_distance
                        worksheet.write_number(row, col + 25, total_extra_distance, main_heading)
                        grand_total_extra_distance += total_extra_distance
                        worksheet.write_number(row, col + 26, total_extra_distance_amount, main_heading)
                        grand_total_extra_distance_amount += grand_total_extra_distance_amount
                        worksheet.write_number(row, col + 28, sum_total_distance, main_heading)
                        grand_sum_total_distance += sum_total_distance
                        worksheet.write_number(row, col + 29, sum_total_fuel_expense, main_heading)
                        grand_sum_total_fuel_expense += sum_total_fuel_expense
                        worksheet.write_number(row, col + 30, sum_total_reward_amount_backend, main_heading)
                        grand_sum_total_reward_amount_backend += sum_total_reward_amount_backend
                        worksheet.write_number(row, col + 31, sum_total_amount, main_heading)
                        grand_sum_total_amount += sum_total_amount
                        row += 1
                    worksheet.write(row, col, 'Grand Total', main_heading1)
                    worksheet.write_number(row, col + 1, grand_total, main_heading)
                    worksheet.write(row, col + 2, 'المبلغ المجموع', main_heading1)
                    worksheet.write_number(row, col + 9, grand_total_invoice_amount_before_tax, main_heading)
                    worksheet.write_number(row, col + 10, grand_total_tax, main_heading)
                    worksheet.write_number(row, col + 11, grand_total_invoice_amount, main_heading)
                    worksheet.write_number(row, col + 24, grand_total_trip_distance, main_heading)
                    worksheet.write_number(row, col + 25, grand_total_extra_distance, main_heading)
                    worksheet.write_number(row, col + 26, grand_total_extra_distance_amount, main_heading)
                    worksheet.write_number(row, col + 28, grand_sum_total_distance, main_heading)
                    worksheet.write_number(row, col + 29, grand_sum_total_fuel_expense, main_heading)
                    worksheet.write_number(row, col + 30, grand_sum_total_reward_amount_backend, main_heading)
                    worksheet.write_number(row, col + 31, grand_sum_total_amount, main_heading)
                    row += 1