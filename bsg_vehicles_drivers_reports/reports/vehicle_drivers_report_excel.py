from odoo import models
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
import math


class VehicleDriversReportExcel(models.AbstractModel):
    _name = 'report.bsg_vehicles_drivers_reports.driver_report_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        employee_table = "hr_employee"
        self.env.cr.execute("select id,driver_code,name,employee_state,"
                            "leave_start_date,last_return_date,driver_rewards,"
                            "mobile_phone,country_id,bsg_licence_no,bsg_exp_date FROM " + employee_table + " WHERE is_driver=True and active=True")
        result = self._cr.fetchall()
        driver_data = pd.DataFrame(list(result))
        driver_data = driver_data.rename(columns={0:'employee_id',1:'driver_code',2:'employee_name',3:'employee_state',
                                                  4:'leave_start_date',5:'last_return_date',
                                                  6:'driver_rewards',7:'mobile_phone',8:'employee_country_id',
                                                  9:'emp_licence_no',10:'emp_licence_expiry'})
        employee_contract = "hr_contract"
        self.env.cr.execute("select employee_id,date_start,analytic_account_id FROM "+ employee_contract+" WHERE state='open'")
        result = self._cr.fetchall()
        bsg_contract_frame = pd.DataFrame(list(result))
        bsg_contract_frame = bsg_contract_frame.rename(columns={0: 'contract_employee_id',1: 'employee_join_date',2:'contract_analytic_account_id'})

        contract_analytic_account = "account_analytic_account"
        self.env.cr.execute(
            "select id,display_name FROM " + contract_analytic_account + " ")
        analytic_account_result = self._cr.fetchall()
        analytic_account_frame = pd.DataFrame(list(analytic_account_result))
        analytic_account_frame = analytic_account_frame.rename(
            columns={0: 'analytic_account_id', 1: 'analytic_account_name'})
        bsg_contract_frame = pd.merge(bsg_contract_frame, analytic_account_frame, how='left', left_on='contract_analytic_account_id',
                               right_on='analytic_account_id')

        driver_data = pd.merge(driver_data, bsg_contract_frame, how='left', left_on='employee_id',
                                   right_on='contract_employee_id')

        employee_iqama = "hr_iqama"
        self.env.cr.execute("select bsg_iqama_name,bsg_employee,bsg_expirydate FROM " + employee_iqama + "")
        result = self._cr.fetchall()
        bsg_iqama_frame = pd.DataFrame(list(result))
        bsg_iqama_frame = bsg_iqama_frame.rename(columns={0: 'bsg_iqama_name', 1: 'bsg_employee',2:'bsg_iqama_expiry'})
        driver_data = pd.merge(driver_data, bsg_iqama_frame, how='left', left_on='employee_id',
                               right_on='bsg_employee')
        employee_country = "res_country"
        self.env.cr.execute("select id,name FROM " + employee_country + "")
        result = self._cr.fetchall()
        bsg_country_frame = pd.DataFrame(list(result))
        bsg_country_frame = bsg_country_frame.rename(
            columns={0:'country_id',1:'country_name'})
        driver_data = pd.merge(driver_data,bsg_country_frame, how='left', left_on='employee_country_id',
                               right_on='country_id')
        employee_nid = "hr_nationality"
        self.env.cr.execute("select bsg_nationality_name,bsg_employee,bsg_expirydate FROM " + employee_nid + "")
        result = self._cr.fetchall()
        bsg_nid_frame = pd.DataFrame(list(result))
        bsg_nid_frame = bsg_nid_frame.rename(
            columns={0: 'bsg_nationality_name', 1: 'bsg_nid_employee',2:'bsg_nid_expiry'})
        driver_data = pd.merge(driver_data, bsg_nid_frame, how='left', left_on='employee_id',
                               right_on='bsg_nid_employee')
        employee_passport = "hr_passport"
        self.env.cr.execute("select bsg_passport_number,bsg_employee_id,bsg_expirydate FROM " + employee_passport + "")
        result = self._cr.fetchall()
        bsg_passport_frame = pd.DataFrame(list(result))
        bsg_passport_frame = bsg_passport_frame.rename(
            columns={0: 'bsg_passport_number', 1: 'bsg_passport_employee', 2: 'bsg_passport_expiry'})
        driver_data = pd.merge(driver_data,bsg_passport_frame, how='left', left_on='employee_id',
                               right_on='bsg_passport_employee')
        fleet_vehicle = "fleet_vehicle"
        self.env.cr.execute("select id, bsg_driver,taq_number,model_id,"
                            "vehicle_status,vehicle_type,model_year,"
                            "estmaira_serial_no,vehicle_group_name,state_id FROM " + fleet_vehicle + "")
        result = self._cr.fetchall()
        fleet_vehicle_frame = pd.DataFrame(list(result))
        fleet_vehicle_frame = fleet_vehicle_frame.rename(
            columns={0:'fleet_vehicle_id',1: 'bsg_driver', 2: 'taq_number', 3: 'vehicle_model_id',4:'vehicle_status',
                     5:'vehicle_type',6:'model_year',7:'estmaira_serial_no',8:'vehicle_group_id',9:'vehicle_state_id'})
        fleet_vehicle_model = "fleet_vehicle_model"
        self.env.cr.execute("select id,name,brand_id FROM " + fleet_vehicle_model + "")
        result = self._cr.fetchall()
        fleet_vehicle_model_frame = pd.DataFrame(list(result))
        fleet_vehicle_model_frame = fleet_vehicle_model_frame.rename(
            columns={0: 'model_id', 1: 'model_name', 2: 'model_make_id'})
        fleet_vehicle_model_brand = "fleet_vehicle_model_brand"
        self.env.cr.execute("select id,name FROM " + fleet_vehicle_model_brand + "")
        result = self._cr.fetchall()
        fleet_vehicle_make_frame = pd.DataFrame(list(result))
        fleet_vehicle_make_frame = fleet_vehicle_make_frame.rename(
            columns={0: 'make_id', 1: 'make_name'})
        fleet_vehicle_model_frame = pd.merge(fleet_vehicle_model_frame, fleet_vehicle_make_frame, how='left', left_on='model_make_id',
                               right_on='make_id')
        fleet_vehicle_frame = pd.merge(fleet_vehicle_frame, fleet_vehicle_model_frame, how='left',left_on='vehicle_model_id',
                                       right_on='model_id')
        vehicle_status = "bsg_vehicle_status"
        self.env.cr.execute("select id,vehicle_status_name FROM " + vehicle_status + "")
        result = self._cr.fetchall()
        vehicle_status_frame = pd.DataFrame(list(result))
        vehicle_status_frame = vehicle_status_frame.rename(
            columns={0: 'vehicle_status_id', 1: 'vehicle_status_name'})
        fleet_vehicle_frame = pd.merge(fleet_vehicle_frame, vehicle_status_frame, how='left',left_on='vehicle_status',
                                       right_on='vehicle_status_id')
        vehicle_type = "bsg_vehicle_type_table"
        self.env.cr.execute("select id,vehicle_type_name,domain_name FROM " + vehicle_type + "")
        result = self._cr.fetchall()
        vehicle_type_frame = pd.DataFrame(list(result))
        vehicle_type_frame = vehicle_type_frame.rename(
            columns={0: 'vehicle_type_id', 1: 'vehicle_type_name',2:'vehicle_type_domain_id'})
        vehicle_type_domain = "vehicle_type_domain"
        self.env.cr.execute("select id,name FROM " + vehicle_type_domain + "")
        result = self._cr.fetchall()
        vehicle_type_domain_frame = pd.DataFrame(list(result))
        vehicle_type_domain_frame = vehicle_type_domain_frame.rename(
            columns={0: 'domain_id', 1: 'domain_name'})
        vehicle_type_frame = pd.merge(vehicle_type_frame, vehicle_type_domain_frame, how='left', left_on='vehicle_type_domain_id',
                                       right_on='domain_id')

        fleet_vehicle_frame = pd.merge(fleet_vehicle_frame, vehicle_type_frame, how='left', left_on='vehicle_type',
                                       right_on='vehicle_type_id')
        driver_data = pd.merge(driver_data, fleet_vehicle_frame, how='left', left_on='employee_id',
                               right_on='bsg_driver')
        if docs.vehicle_make:
            driver_data = driver_data.loc[(driver_data['make_id'].isin(docs.vehicle_make.ids))]
        if docs.vehicle_group:
            driver_data = driver_data.loc[(driver_data['vehicle_group_id'].isin(docs.vehicle_group.ids))]
        if docs.vehicle_sticker_no:
            driver_data = driver_data.loc[(driver_data['fleet_vehicle_id'].isin(docs.vehicle_sticker_no.ids))]
        if docs.driver_link == 'linked' and docs.driver_name:
            driver_data = driver_data.loc[(driver_data['bsg_driver'].isin(docs.driver_name.ids))]
        if docs.driver_link == 'linked' and not docs.driver_name:
            driver_data = driver_data.loc[(driver_data['bsg_driver'].notnull())]
        if docs.driver_link == 'unlinked':
            driver_data = driver_data.loc[(driver_data['bsg_driver'].isnull())]
        if docs.model_year:
            year_list = []
            for year in docs.model_year:
                if year:
                    year_list.append(year.car_year_name)
            driver_data = driver_data.loc[(driver_data['model_year'].isin(year_list))]
        if docs.vehicle_state:
            driver_data = driver_data.loc[(driver_data['vehicle_state_id'].isin(docs.vehicle_state.ids))]
        if docs.vehicle_type:
            driver_data = driver_data.loc[(driver_data['vehicle_type'].isin(docs.vehicle_type.ids))]
        if docs.domain_name:
            driver_data = driver_data.loc[(driver_data['domain_id'].isin(docs.domain_name.ids))]
        if docs.expiry_date_on == 'emp_iqama':
            if docs.expire_date_condition == 'is_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'] == (docs.expiry_date))]
            if docs.expire_date_condition == 'is_not_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'] != (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'] > (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'] < (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after_or_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'] >= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before_or_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_between':
                driver_data = driver_data.loc[
                    (driver_data['bsg_iqama_expiry'] >= (docs.expiry_date)) & (driver_data['bsg_iqama_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_set':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'].notnull())]
            if docs.expire_date_condition == 'is_not_set':
                driver_data = driver_data.loc[(driver_data['bsg_iqama_expiry'].isnull())]
        if docs.expiry_date_on == 'national_id':
            if docs.expire_date_condition == 'is_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'] == (docs.expiry_date))]
            if docs.expire_date_condition == 'is_not_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'] != (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'] > (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'] < (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after_or_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'] >= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before_or_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_between':
                driver_data = driver_data.loc[
                    (driver_data['bsg_nid_expiry'] >= (docs.expiry_date)) & (driver_data['bsg_nid_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_set':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'].notnull())]
            if docs.expire_date_condition == 'is_not_set':
                driver_data = driver_data.loc[(driver_data['bsg_nid_expiry'].isnull())]
        if docs.expiry_date_on == 'passport':
            if docs.expire_date_condition == 'is_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'] == (docs.expiry_date))]
            if docs.expire_date_condition == 'is_not_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'] != (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'] > (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'] < (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after_or_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'] >= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before_or_equal_to':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_between':
                driver_data = driver_data.loc[
                    (driver_data['bsg_passport_expiry'] >= (docs.expiry_date)) & (driver_data['bsg_passport_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_set':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'].notnull())]
            if docs.expire_date_condition == 'is_not_set':
                driver_data = driver_data.loc[(driver_data['bsg_passport_expiry'].isnull())]
        if docs.expiry_date_on == 'emp_licence':
            if docs.expire_date_condition == 'is_equal_to':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'] == (docs.expiry_date))]
            if docs.expire_date_condition == 'is_not_equal_to':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'] != (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'] > (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'] < (docs.expiry_date))]
            if docs.expire_date_condition == 'is_after_or_equal_to':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'] >= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_before_or_equal_to':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_between':
                driver_data = driver_data.loc[
                    (driver_data['emp_licence_expiry'] >= (docs.expiry_date)) & (driver_data['emp_licence_expiry'] <= (docs.expiry_date))]
            if docs.expire_date_condition == 'is_set':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'].notnull())]
            if docs.expire_date_condition == 'is_not_set':
                driver_data = driver_data.loc[(driver_data['emp_licence_expiry'].isnull())]
        driver_data = driver_data.sort_values(by=['driver_code'])
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
        if docs.grouping_by == 'all':
            self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report"
            sheet.merge_range('A1:Q1', 'تقرير السائقين', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicles Drivers Report', main_heading3)
            row += 2
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col+1, 'Employee Name', main_heading2)
            sheet.write(row, col+2, 'Date of Join', main_heading2)
            sheet.write(row, col+3, 'Emploee Status', main_heading2)
            sheet.write(row, col+4, 'Nationality', main_heading2)
            sheet.write(row, col+5, 'Start Leaves Date', main_heading2)
            sheet.write(row, col+6, 'Return Leaves Date', main_heading2)
            sheet.write(row, col+7, 'Driver Reward', main_heading2)
            sheet.write(row, col+8, 'Iqama No.', main_heading2)
            sheet.write(row, col+9, 'Iqama Expiry date', main_heading2)
            sheet.write(row, col+10 , 'Iqama Hijri Expiry date', main_heading2)
            sheet.write(row, col+11, 'Remainder Iqama expiry days', main_heading2)
            sheet.write(row, col+12, 'National ID', main_heading2)
            sheet.write(row, col+13, 'National Expiry date', main_heading2)
            sheet.write(row, col+14, 'National Hijri Expiry date', main_heading2)
            sheet.write(row, col+15, 'Remainder National expiry days', main_heading2)
            sheet.write(row, col+16, 'Passport Number', main_heading2)
            sheet.write(row, col+17, 'Passport Expiry date', main_heading2)
            sheet.write(row, col+18, 'Passport Hijri Expiry date', main_heading2)
            sheet.write(row, col+19, 'Remainder Passport expiry days ', main_heading2)
            sheet.write(row, col+20, 'Employee Licence No.', main_heading2)
            sheet.write(row, col+21, 'Employee Licence Expiry', main_heading2)
            sheet.write(row, col+22, 'Employee Licence Hijri Expiry Date', main_heading2)
            sheet.write(row, col+23, 'Remainder Licence expiry days', main_heading2)
            sheet.write(row, col+24, ' Mobile No.', main_heading2)
            sheet.write(row, col+25, 'Linked with Vehicle', main_heading2)
            sheet.write(row, col+26, 'Sticker No.', main_heading2)
            sheet.write(row, col+27, 'Vehicle Make', main_heading2)
            sheet.write(row, col+28, 'Vehicle Model', main_heading2)
            sheet.write(row, col+29, 'Vehicle Status', main_heading2)
            sheet.write(row, col+30, 'Vehicle Type', main_heading2)
            sheet.write(row, col+31, 'Domain Name', main_heading2)
            sheet.write(row, col+32, 'Manufacturing Year', main_heading2)
            sheet.write(row, col+33, 'Istmara Serial No.', main_heading2)
            sheet.write(row, col+34, 'Analytic Account', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col+1, 'اسم الموظف', main_heading2)
            sheet.write(row, col+2, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col+3, 'حالة الموظف', main_heading2)
            sheet.write(row, col+4, 'الجنسية', main_heading2)
            sheet.write(row, col+5, ' تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col+6, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col+7, 'نوع الحافز  ', main_heading2)
            sheet.write(row, col+8, 'رقم الاقامه ', main_heading2)
            sheet.write(row, col+9, 'تاريخ انتهاء الإقامة ', main_heading2)
            sheet.write(row, col+10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
            sheet.write(row, col+11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
            sheet.write(row, col+12, 'رقم الهوية', main_heading2)
            sheet.write(row, col+13, 'تاريخ انتهاء الهوية', main_heading2)
            sheet.write(row, col+14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
            sheet.write(row, col+15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
            sheet.write(row, col+16, 'رقم الجواز', main_heading2)
            sheet.write(row, col+17, 'تاريخ انتهاء الجواز', main_heading2)
            sheet.write(row, col+18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
            sheet.write(row, col+19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
            sheet.write(row, col+20, 'رقم رخصة الموظف', main_heading2)
            sheet.write(row, col+21, 'انتهاء رخصة الموظف', main_heading2)
            sheet.write(row, col+22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
            sheet.write(row, col+23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
            sheet.write(row, col+24, 'رقم الجوال  ', main_heading2)
            sheet.write(row, col+25, 'مربوط بشاحنة', main_heading2)
            sheet.write(row, col+26, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col+27, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col+28, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col+29, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col+30, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col+31, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col+32, 'سنة الصنع', main_heading2)
            sheet.write(row, col+33, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col+34, 'حساب تحليلي', main_heading2)
            row += 1
            driver_data_all = driver_data.fillna(0)
            for index,value in driver_data_all.iterrows():
                if value['driver_code']:
                    sheet.write_string(row, col,str(value['driver_code']), main_heading)
                if value['employee_name']:
                    sheet.write_string(row, col + 1,str(value['employee_name']), main_heading)
                if value['employee_join_date']:
                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                if value['employee_state']:
                    if value['employee_state'] == 'on_job':
                        sheet.write_string(row, col + 3,'On Job', main_heading)
                    if value['employee_state'] == 'on_leave':
                        sheet.write_string(row, col + 3,'On Leave', main_heading)
                    if value['employee_state'] == 'return_from_holiday':
                        sheet.write_string(row, col + 3,'Return From Holiday', main_heading)
                    if value['employee_state'] == 'resignation':
                        sheet.write_string(row, col + 3,'Resignation', main_heading)
                    if value['employee_state'] == 'suspended':
                        sheet.write_string(row, col + 3,'Suspended', main_heading)
                    if value['employee_state'] == 'service_expired':
                        sheet.write_string(row, col + 3,'Service Expired', main_heading)
                    if value['employee_state'] == 'contract_terminated':
                        sheet.write_string(row, col + 3,'Contract Terminated', main_heading)
                    if value['employee_state'] == 'ending_contract_during_trial_period':
                        sheet.write_string(row, col + 3,'Ending Contract During Trial Period', main_heading)
                if value['country_name']:
                    sheet.write_string(row, col + 4,str(value['country_name']), main_heading)
                if value['leave_start_date']:
                    sheet.write_string(row, col + 5,str(value['leave_start_date']), main_heading)
                if value['last_return_date']:
                    sheet.write_string(row, col + 6,str(value['last_return_date']), main_heading)
                if value['driver_rewards']:
                    if value['driver_rewards'] == 'by_delivery':
                        sheet.write_string(row, col + 7,'By Delivery A', main_heading)
                    if value['driver_rewards'] == 'by_delivery_b':
                        sheet.write_string(row, col + 7,'By Delivery B', main_heading)
                    if value['driver_rewards'] == 'by_revenue':
                        sheet.write_string(row, col + 7,'By Revenue', main_heading)
                    if value['driver_rewards'] == 'not_applicable':
                        sheet.write_string(row, col + 7,'Not Applicable', main_heading)
                if value['bsg_iqama_name']:
                    sheet.write_string(row, col + 8,str(value['bsg_iqama_name']), main_heading)
                if value['bsg_iqama_expiry']:
                    days=0
                    delta =  value['bsg_iqama_expiry'] - date.today()
                    days = int(delta.days)
                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                    sheet.write_string(row, col + 11,str(days), main_heading)
                if value['bsg_nationality_name']:
                    sheet.write_string(row, col + 12,str(value['bsg_nationality_name']), main_heading)
                if value['bsg_nid_expiry']:
                    days = 0
                    delta =  value['bsg_nid_expiry'] - date.today()
                    days = int(delta.days)
                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                    sheet.write_string(row, col + 13,str(value['bsg_nid_expiry']), main_heading)
                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                    sheet.write_string(row, col + 15, str(days), main_heading)
                if value['bsg_passport_number']:
                    sheet.write_string(row, col + 16,str(value['bsg_passport_number']), main_heading)
                if value['bsg_passport_expiry']:
                    days = 0
                    delta = value['bsg_passport_expiry'] - date.today()
                    days = int(delta.days)
                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                    sheet.write_string(row, col + 17,str(value['bsg_passport_expiry']), main_heading)
                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                    sheet.write_string(row, col + 19, str(days), main_heading)
                if value['emp_licence_no']:
                    sheet.write(row, col + 20,str(value['emp_licence_no']), main_heading)
                if value['emp_licence_expiry']:
                    days = 0
                    delta = value['emp_licence_expiry'] - date.today()
                    days = int(delta.days)
                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                    sheet.write(row, col + 21,str(value['emp_licence_expiry']), main_heading)
                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                    sheet.write(row, col + 23, str(days), main_heading)
                if value['mobile_phone']:
                    sheet.write_string(row, col + 24,str(value['mobile_phone']), main_heading)
                if value['bsg_driver']:
                    sheet.write_string(row, col + 25,'Yes', main_heading)
                if value['taq_number']:
                    sheet.write_string(row, col + 26,str(value['taq_number']), main_heading)
                if value['make_name']:
                    sheet.write_string(row, col + 27,str(value['make_name']), main_heading)
                if value['model_name']:
                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                    sheet.write_string(row, col + 28,str(display_name), main_heading)
                if value['vehicle_status_name']:
                    sheet.write_string(row, col + 29,str(value['vehicle_status_name']), main_heading)
                if value['vehicle_type_name']:
                    sheet.write_string(row, col + 30,str(value['vehicle_type_name']), main_heading)
                if value['domain_name']:
                    sheet.write_string(row, col + 31,str([value['domain_name']]), main_heading)
                if value['model_year']:
                    sheet.write_string(row, col + 32,str(value['model_year']), main_heading)
                if value['estmaira_serial_no']:
                    sheet.write_string(row, col + 33,str(value['estmaira_serial_no']), main_heading)
                if value['analytic_account_name']:
                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                row+=1
        if docs.grouping_by == 'by_nationality':
            self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Nationality"
            sheet.merge_range('A1:Q1', 'تقرير السائقين التجميع بحسب الجنسية', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Grouping by Nationality', main_heading3)
            row += 2
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Name', main_heading2)
            sheet.write(row, col + 2, 'Date of Join', main_heading2)
            sheet.write(row, col + 3, 'Emploee Status', main_heading2)
            sheet.write(row, col + 4, 'Start Leaves Date', main_heading2)
            sheet.write(row, col + 5, 'Return Leaves Date', main_heading2)
            sheet.write(row, col + 6, 'Driver Reward', main_heading2)
            sheet.write(row, col + 7, 'Iqama No.', main_heading2)
            sheet.write(row, col + 8, 'Iqama Expiry date', main_heading2)
            sheet.write(row, col + 9, 'Iqama Hijri Expiry date', main_heading2)
            sheet.write(row, col + 10, 'Remainder Iqama expiry days', main_heading2)
            sheet.write(row, col + 11, 'National ID', main_heading2)
            sheet.write(row, col + 12, 'National Expiry date', main_heading2)
            sheet.write(row, col + 13, 'National Hijri Expiry date', main_heading2)
            sheet.write(row, col + 14, 'Remainder National expiry days', main_heading2)
            sheet.write(row, col + 15, 'Passport Number', main_heading2)
            sheet.write(row, col + 16, 'Passport Expiry date', main_heading2)
            sheet.write(row, col + 17, 'Passport Hijri Expiry date', main_heading2)
            sheet.write(row, col + 18, 'Remainder Passport expiry days ', main_heading2)
            sheet.write(row, col + 19, 'Employee Licence No.', main_heading2)
            sheet.write(row, col + 20, 'Employee Licence Expiry', main_heading2)
            sheet.write(row, col + 21, 'Employee Licence Hijri Expiry Date', main_heading2)
            sheet.write(row, col + 22, 'Remainder Licence expiry days', main_heading2)
            sheet.write(row, col + 23, ' Mobile No.', main_heading2)
            sheet.write(row, col + 24, 'Linked with Vehicle', main_heading2)
            sheet.write(row, col + 25, 'Sticker No.', main_heading2)
            sheet.write(row, col + 26, 'Vehicle Make', main_heading2)
            sheet.write(row, col + 27, 'Vehicle Model', main_heading2)
            sheet.write(row, col + 28, 'Vehicle Status', main_heading2)
            sheet.write(row, col + 29, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 30, 'Domain Name', main_heading2)
            sheet.write(row, col + 31, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 32, 'Istmara Serial No.', main_heading2)
            sheet.write(row, col + 33, 'Analytic Account', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, ' تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 5, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 6, 'نوع الحافز  ', main_heading2)
            sheet.write(row, col + 7, 'رقم الاقامه ', main_heading2)
            sheet.write(row, col + 8, 'تاريخ انتهاء الإقامة ', main_heading2)
            sheet.write(row, col + 9, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
            sheet.write(row, col + 10, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
            sheet.write(row, col + 11, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 12, 'تاريخ انتهاء الهوية', main_heading2)
            sheet.write(row, col + 13, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
            sheet.write(row, col + 14, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
            sheet.write(row, col + 15, 'رقم الجواز', main_heading2)
            sheet.write(row, col + 16, 'تاريخ انتهاء الجواز', main_heading2)
            sheet.write(row, col + 17, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
            sheet.write(row, col + 18, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
            sheet.write(row, col + 19, 'رقم رخصة الموظف', main_heading2)
            sheet.write(row, col + 20, 'انتهاء رخصة الموظف', main_heading2)
            sheet.write(row, col + 21, 'انتهاء رخصة الموظف بالهجري', main_heading2)
            sheet.write(row, col + 22, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
            sheet.write(row, col + 23, 'رقم الجوال  ', main_heading2)
            sheet.write(row, col + 24, 'مربوط بشاحنة', main_heading2)
            sheet.write(row, col + 25, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 26, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 27, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 28, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 29, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 30, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 31, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 32, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 33, 'حساب تحليلي', main_heading2)
            row += 1
            nationality_list=[]
            driver_data = driver_data.sort_values(by=['country_name','driver_code'])
            driver_data_nationality = driver_data.fillna(0)
            grand_total=0
            for index, value in driver_data_nationality.iterrows():
                if value['country_name'] not in nationality_list:
                    nationality_list.append(value['country_name'])
            for nationality in nationality_list:
                if nationality:
                    total=0
                    sheet.write(row, col, 'Nationality', main_heading2)
                    sheet.write_string(row, col + 1, str(nationality), main_heading)
                    sheet.write(row, col + 2, 'الجنسية', main_heading2)
                    row += 1
                    for index, value in driver_data_nationality.iterrows():
                        if value['country_name'] == nationality:
                            if value['driver_code']:
                                sheet.write_string(row, col, str(value['driver_code']), main_heading)
                            if value['employee_name']:
                                sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                            if value['employee_join_date']:
                                sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                            if value['employee_state']:
                                if value['employee_state'] == 'on_job':
                                    sheet.write_string(row, col + 3, 'On Job', main_heading)
                                if value['employee_state'] == 'on_leave':
                                    sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                if value['employee_state'] == 'return_from_holiday':
                                    sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                if value['employee_state'] == 'resignation':
                                    sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                if value['employee_state'] == 'suspended':
                                    sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                if value['employee_state'] == 'service_expired':
                                    sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                if value['employee_state'] == 'contract_terminated':
                                    sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                if value['employee_state'] == 'ending_contract_during_trial_period':
                                    sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                       main_heading)
                            if value['leave_start_date']:
                                sheet.write_string(row, col + 4, str(value['leave_start_date']), main_heading)
                            if value['last_return_date']:
                                sheet.write_string(row, col + 5, str(value['last_return_date']), main_heading)
                            if value['driver_rewards']:
                                if value['driver_rewards'] == 'by_delivery':
                                    sheet.write_string(row, col + 6, 'By Delivery A', main_heading)
                                if value['driver_rewards'] == 'by_delivery_b':
                                    sheet.write_string(row, col + 6, 'By Delivery B', main_heading)
                                if value['driver_rewards'] == 'by_revenue':
                                    sheet.write_string(row, col + 6, 'By Revenue', main_heading)
                                if value['driver_rewards'] == 'not_applicable':
                                    sheet.write_string(row, col + 6, 'Not Applicable', main_heading)
                            if value['bsg_iqama_name']:
                                sheet.write_string(row, col + 7, str(value['bsg_iqama_name']), main_heading)
                            if value['bsg_iqama_expiry']:
                                days = 0
                                delta =  value['bsg_iqama_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                sheet.write_string(row, col + 8, str(value['bsg_iqama_expiry']), main_heading)
                                sheet.write_string(row, col + 9, str(hijri_iqama_exp_date), main_heading)
                                sheet.write_string(row, col + 10, str(days), main_heading)
                            if value['bsg_nationality_name']:
                                sheet.write_string(row, col + 11, str(value['bsg_nationality_name']), main_heading)
                            if value['bsg_nid_expiry']:
                                days = 0
                                delta =  value['bsg_nid_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                sheet.write_string(row, col + 12, str(value['bsg_nid_expiry']), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_nid_exp_date), main_heading)
                                sheet.write_string(row, col + 14, str(days), main_heading)
                            if value['bsg_passport_number']:
                                sheet.write_string(row, col + 15, str(value['bsg_passport_number']), main_heading)
                            if value['bsg_passport_expiry']:
                                days = 0
                                delta = value['bsg_passport_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                sheet.write_string(row, col + 16, str(value['bsg_passport_expiry']), main_heading)
                                sheet.write_string(row, col + 17, str(hijri_passport_exp_date), main_heading)
                                sheet.write_string(row, col + 18, str(days), main_heading)
                            if value['emp_licence_no']:
                                sheet.write(row, col + 19, str(value['emp_licence_no']), main_heading)
                            if value['emp_licence_expiry']:
                                days = 0
                                delta = value['emp_licence_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                sheet.write(row, col + 20, str(value['emp_licence_expiry']), main_heading)
                                sheet.write(row, col + 21, str(hijri_licence_exp_date), main_heading)
                                sheet.write(row, col + 22, str(days), main_heading)
                            if value['mobile_phone']:
                                sheet.write_string(row, col + 23, str(value['mobile_phone']), main_heading)
                            if value['bsg_driver']:
                                sheet.write_string(row, col + 24, 'Yes', main_heading)
                            if value['taq_number']:
                                sheet.write_string(row, col + 25, str(value['taq_number']), main_heading)
                            if value['make_name']:
                                sheet.write_string(row, col + 26, str(value['make_name']), main_heading)
                            if value['model_name']:
                                display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                sheet.write_string(row, col + 27, str(display_name), main_heading)
                            if value['vehicle_status_name']:
                                sheet.write_string(row, col + 28, str(value['vehicle_status_name']), main_heading)
                            if value['vehicle_type_name']:
                                sheet.write_string(row, col + 29, str(value['vehicle_type_name']), main_heading)
                            if value['domain_name']:
                                sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                            if value['model_year']:
                                sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                            if value['estmaira_serial_no']:
                                sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                            if value['analytic_account_name']:
                                sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                            row += 1
                            total+=1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
            nationality_null = driver_data_nationality.loc[(driver_data['country_name'] == 0)]
            if not nationality_null.empty:
                total = 0
                sheet.write(row, col, 'Nationality', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'الجنسية', main_heading2)
                row += 1
                for index, value in nationality_null.iterrows():
                    if value['driver_code']:
                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                    if value['employee_name']:
                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                    if value['employee_join_date']:
                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                    if value['employee_state']:
                        if value['employee_state'] == 'on_job':
                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                        if value['employee_state'] == 'on_leave':
                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                        if value['employee_state'] == 'return_from_holiday':
                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                        if value['employee_state'] == 'resignation':
                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                        if value['employee_state'] == 'suspended':
                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                        if value['employee_state'] == 'service_expired':
                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                        if value['employee_state'] == 'contract_terminated':
                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                        if value['employee_state'] == 'ending_contract_during_trial_period':
                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                               main_heading)
                    if value['leave_start_date']:
                        sheet.write_string(row, col + 4, str(value['leave_start_date']), main_heading)
                    if value['last_return_date']:
                        sheet.write_string(row, col + 5, str(value['last_return_date']), main_heading)
                    if value['driver_rewards']:
                        if value['driver_rewards'] == 'by_delivery':
                            sheet.write_string(row, col + 6, 'By Delivery A', main_heading)
                        if value['driver_rewards'] == 'by_delivery_b':
                            sheet.write_string(row, col + 6, 'By Delivery B', main_heading)
                        if value['driver_rewards'] == 'by_revenue':
                            sheet.write_string(row, col + 6, 'By Revenue', main_heading)
                        if value['driver_rewards'] == 'not_applicable':
                            sheet.write_string(row, col + 6, 'Not Applicable', main_heading)
                    if value['bsg_iqama_name']:
                        sheet.write_string(row, col + 7, str(value['bsg_iqama_name']), main_heading)
                    if value['bsg_iqama_expiry']:
                        days = 0
                        delta =  value['bsg_iqama_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                        sheet.write_string(row, col + 8, str(value['bsg_iqama_expiry']), main_heading)
                        sheet.write_string(row, col + 9, str(hijri_iqama_exp_date), main_heading)
                        sheet.write_string(row, col + 10, str(days), main_heading)
                    if value['bsg_nationality_name']:
                        sheet.write_string(row, col + 11, str(value['bsg_nationality_name']), main_heading)
                    if value['bsg_nid_expiry']:
                        days = 0
                        delta =  value['bsg_nid_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                        sheet.write_string(row, col + 12, str(value['bsg_nid_expiry']), main_heading)
                        sheet.write_string(row, col + 13, str(hijri_nid_exp_date), main_heading)
                        sheet.write_string(row, col + 14, str(days), main_heading)
                    if value['bsg_passport_number']:
                        sheet.write_string(row, col + 15, str(value['bsg_passport_number']), main_heading)
                    if value['bsg_passport_expiry']:
                        days = 0
                        delta = value['bsg_passport_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                        sheet.write_string(row, col + 16, str(value['bsg_passport_expiry']), main_heading)
                        sheet.write_string(row, col + 17, str(hijri_passport_exp_date), main_heading)
                        sheet.write_string(row, col + 18, str(days), main_heading)
                    if value['emp_licence_no']:
                        sheet.write(row, col + 19, str(value['emp_licence_no']), main_heading)
                    if value['emp_licence_expiry']:
                        days = 0
                        delta = value['emp_licence_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                        sheet.write(row, col + 20, str(value['emp_licence_expiry']), main_heading)
                        sheet.write(row, col + 21, str(hijri_licence_exp_date), main_heading)
                        sheet.write(row, col + 22, str(days), main_heading)
                    if value['mobile_phone']:
                        sheet.write_string(row, col + 23, str(value['mobile_phone']), main_heading)
                    if value['bsg_driver']:
                        sheet.write_string(row, col + 24, 'Yes', main_heading)
                    if value['taq_number']:
                        sheet.write_string(row, col + 25, str(value['taq_number']), main_heading)
                    if value['make_name']:
                        sheet.write_string(row, col + 26, str(value['make_name']), main_heading)
                    if value['model_name']:
                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                        sheet.write_string(row, col + 27, str(display_name), main_heading)
                    if value['vehicle_status_name']:
                        sheet.write_string(row, col + 28, str(value['vehicle_status_name']), main_heading)
                    if value['vehicle_type_name']:
                        sheet.write_string(row, col + 29, str(value['vehicle_type_name']), main_heading)
                    if value['domain_name']:
                        sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                    if value['model_year']:
                        sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                    if value['estmaira_serial_no']:
                        sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                    if value['analytic_account_name']:
                        sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                    row += 1
                    total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_employee_status':
            self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Employee Status"
            sheet.merge_range('A1:Q1', 'تقرير السائقين التجميع بحسب حالة الموظف', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Employee Status', main_heading3)
            row += 2
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Name', main_heading2)
            sheet.write(row, col + 2, 'Date of Join', main_heading2)
            sheet.write(row, col + 3, 'Nationality', main_heading2)
            sheet.write(row, col + 4, 'Start Leaves Date', main_heading2)
            sheet.write(row, col + 5, 'Return Leaves Date', main_heading2)
            sheet.write(row, col + 6, 'Driver Reward', main_heading2)
            sheet.write(row, col + 7, 'Iqama No.', main_heading2)
            sheet.write(row, col + 8, 'Iqama Expiry date', main_heading2)
            sheet.write(row, col + 9, 'Iqama Hijri Expiry date', main_heading2)
            sheet.write(row, col + 10, 'Remainder Iqama expiry days', main_heading2)
            sheet.write(row, col + 11, 'National ID', main_heading2)
            sheet.write(row, col + 12, 'National Expiry date', main_heading2)
            sheet.write(row, col + 13, 'National Hijri Expiry date', main_heading2)
            sheet.write(row, col + 14, 'Remainder National expiry days', main_heading2)
            sheet.write(row, col + 15, 'Passport Number', main_heading2)
            sheet.write(row, col + 16, 'Passport Expiry date', main_heading2)
            sheet.write(row, col + 17, 'Passport Hijri Expiry date', main_heading2)
            sheet.write(row, col + 18, 'Remainder Passport expiry days ', main_heading2)
            sheet.write(row, col + 19, 'Employee Licence No.', main_heading2)
            sheet.write(row, col + 20, 'Employee Licence Expiry', main_heading2)
            sheet.write(row, col + 21, 'Employee Licence Hijri Expiry Date', main_heading2)
            sheet.write(row, col + 22, 'Remainder Licence expiry days', main_heading2)
            sheet.write(row, col + 23, ' Mobile No.', main_heading2)
            sheet.write(row, col + 24, 'Linked with Vehicle', main_heading2)
            sheet.write(row, col + 25, 'Sticker No.', main_heading2)
            sheet.write(row, col + 26, 'Vehicle Make', main_heading2)
            sheet.write(row, col + 27, 'Vehicle Model', main_heading2)
            sheet.write(row, col + 28, 'Vehicle Status', main_heading2)
            sheet.write(row, col + 29, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 30, 'Domain Name', main_heading2)
            sheet.write(row, col + 31, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 32, 'Istmara Serial No.', main_heading2)
            sheet.write(row, col + 33, 'Analytic Account', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 3, 'الجنسية', main_heading2)
            sheet.write(row, col + 4, ' تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 5, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 6, 'نوع الحافز  ', main_heading2)
            sheet.write(row, col + 7, 'رقم الاقامه ', main_heading2)
            sheet.write(row, col + 8, 'تاريخ انتهاء الإقامة ', main_heading2)
            sheet.write(row, col + 9, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
            sheet.write(row, col + 10, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
            sheet.write(row, col + 11, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 12, 'تاريخ انتهاء الهوية', main_heading2)
            sheet.write(row, col + 13, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
            sheet.write(row, col + 14, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
            sheet.write(row, col + 15, 'رقم الجواز', main_heading2)
            sheet.write(row, col + 16, 'تاريخ انتهاء الجواز', main_heading2)
            sheet.write(row, col + 17, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
            sheet.write(row, col + 18, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
            sheet.write(row, col + 19, 'رقم رخصة الموظف', main_heading2)
            sheet.write(row, col + 20, 'انتهاء رخصة الموظف', main_heading2)
            sheet.write(row, col + 21, 'انتهاء رخصة الموظف بالهجري', main_heading2)
            sheet.write(row, col + 22, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
            sheet.write(row, col + 23, 'رقم الجوال  ', main_heading2)
            sheet.write(row, col + 24, 'مربوط بشاحنة', main_heading2)
            sheet.write(row, col + 25, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 26, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 27, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 28, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 29, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 30, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 31, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 32, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 33, 'حساب تحليلي', main_heading2)
            row += 1
            emp_status_list=[]
            grand_total=0
            driver_data = driver_data.sort_values(by=['employee_state','driver_code'])
            driver_data_emp_status = driver_data.fillna(0)
            for index, value in driver_data_emp_status.iterrows():
                if value['employee_state'] not in emp_status_list:
                    emp_status_list.append(value['employee_state'])
            for employee_status in emp_status_list:
                if employee_status:
                    total=0
                    sheet.write(row, col, 'Emploee Status', main_heading2)
                    sheet.write_string(row, col + 1, str(employee_status), main_heading)
                    sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                    row += 1
                    for index, value in driver_data_emp_status.iterrows():
                        if value['employee_state'] == employee_status:
                            if value['driver_code']:
                                sheet.write_string(row, col, str(value['driver_code']), main_heading)
                            if value['employee_name']:
                                sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                            if value['employee_join_date']:
                                sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                            if value['country_name']:
                                sheet.write_string(row, col + 3, str(value['country_name']), main_heading)
                            if value['leave_start_date']:
                                sheet.write_string(row, col + 4, str(value['leave_start_date']), main_heading)
                            if value['last_return_date']:
                                sheet.write_string(row, col + 5, str(value['last_return_date']), main_heading)
                            if value['driver_rewards']:
                                if value['driver_rewards'] == 'by_delivery':
                                    sheet.write_string(row, col + 6, 'By Delivery A', main_heading)
                                if value['driver_rewards'] == 'by_delivery_b':
                                    sheet.write_string(row, col + 6, 'By Delivery B', main_heading)
                                if value['driver_rewards'] == 'by_revenue':
                                    sheet.write_string(row, col + 6, 'By Revenue', main_heading)
                                if value['driver_rewards'] == 'not_applicable':
                                    sheet.write_string(row, col + 6, 'Not Applicable', main_heading)
                            if value['bsg_iqama_name']:
                                sheet.write_string(row, col + 7, str(value['bsg_iqama_name']), main_heading)
                            if value['bsg_iqama_expiry']:
                                days = 0
                                delta =  value['bsg_iqama_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                sheet.write_string(row, col + 8, str(value['bsg_iqama_expiry']), main_heading)
                                sheet.write_string(row, col + 9, str(hijri_iqama_exp_date), main_heading)
                                sheet.write_string(row, col + 10, str(days), main_heading)
                            if value['bsg_nationality_name']:
                                sheet.write_string(row, col + 11, str(value['bsg_nationality_name']), main_heading)
                            if value['bsg_nid_expiry']:
                                days = 0
                                delta =  value['bsg_nid_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                sheet.write_string(row, col + 12, str(value['bsg_nid_expiry']), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_nid_exp_date), main_heading)
                                sheet.write_string(row, col + 14, str(days), main_heading)
                            if value['bsg_passport_number']:
                                sheet.write_string(row, col + 15, str(value['bsg_passport_number']), main_heading)
                            if value['bsg_passport_expiry']:
                                days = 0
                                delta = value['bsg_passport_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                sheet.write_string(row, col + 16, str(value['bsg_passport_expiry']), main_heading)
                                sheet.write_string(row, col + 17, str(hijri_passport_exp_date), main_heading)
                                sheet.write_string(row, col + 18, str(days), main_heading)
                            if value['emp_licence_no']:
                                sheet.write(row, col + 19, str(value['emp_licence_no']), main_heading)
                            if value['emp_licence_expiry']:
                                days = 0
                                delta = value['emp_licence_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                sheet.write(row, col + 20, str(value['emp_licence_expiry']), main_heading)
                                sheet.write(row, col + 21, str(hijri_licence_exp_date), main_heading)
                                sheet.write(row, col + 22, str(days), main_heading)
                            if value['mobile_phone']:
                                sheet.write_string(row, col + 23, str(value['mobile_phone']), main_heading)
                            if value['bsg_driver']:
                                sheet.write_string(row, col + 24, 'Yes', main_heading)
                            if value['taq_number']:
                                sheet.write_string(row, col + 25, str(value['taq_number']), main_heading)
                            if value['make_name']:
                                sheet.write_string(row, col + 26, str(value['make_name']), main_heading)
                            if value['model_name']:
                                display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                sheet.write_string(row, col + 27, str(display_name), main_heading)
                            if value['vehicle_status_name']:
                                sheet.write_string(row, col + 28, str(value['vehicle_status_name']), main_heading)
                            if value['vehicle_type_name']:
                                sheet.write_string(row, col + 29, str(value['vehicle_type_name']), main_heading)
                            if value['domain_name']:
                                sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                            if value['model_year']:
                                sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                            if value['estmaira_serial_no']:
                                sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                            if value['analytic_account_name']:
                                sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                            row += 1
                            total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
            driver_data_emp_status = driver_data.fillna(0)
            emp_state_null = driver_data_emp_status.loc[(driver_data['employee_state'] == 0)]
            if not emp_state_null.empty:
                total = 0
                sheet.write(row, col, 'Employee Status', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'حالة الموظف', main_heading2)
                row += 1
                for index, value in emp_state_null.iterrows():
                    if value['driver_code']:
                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                    if value['employee_name']:
                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                    if value['employee_join_date']:
                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                    if value['country_name']:
                        sheet.write_string(row, col + 3, str(value['country_name']), main_heading)
                    if value['leave_start_date']:
                        sheet.write_string(row, col + 4, str(value['leave_start_date']), main_heading)
                    if value['last_return_date']:
                        sheet.write_string(row, col + 5, str(value['last_return_date']), main_heading)
                    if value['driver_rewards']:
                        if value['driver_rewards'] == 'by_delivery':
                            sheet.write_string(row, col + 6, 'By Delivery A', main_heading)
                        if value['driver_rewards'] == 'by_delivery_b':
                            sheet.write_string(row, col + 6, 'By Delivery B', main_heading)
                        if value['driver_rewards'] == 'by_revenue':
                            sheet.write_string(row, col + 6, 'By Revenue', main_heading)
                        if value['driver_rewards'] == 'not_applicable':
                            sheet.write_string(row, col + 6, 'Not Applicable', main_heading)
                    if value['bsg_iqama_name']:
                        sheet.write_string(row, col + 7, str(value['bsg_iqama_name']), main_heading)
                    if value['bsg_iqama_expiry']:
                        days = 0
                        delta =  value['bsg_iqama_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                        sheet.write_string(row, col + 8, str(value['bsg_iqama_expiry']), main_heading)
                        sheet.write_string(row, col + 9, str(hijri_iqama_exp_date), main_heading)
                        sheet.write_string(row, col + 10, str(days), main_heading)
                    if value['bsg_nationality_name']:
                        sheet.write_string(row, col + 11, str(value['bsg_nationality_name']), main_heading)
                    if value['bsg_nid_expiry']:
                        days = 0
                        delta =  value['bsg_nid_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                        sheet.write_string(row, col + 12, str(value['bsg_nid_expiry']), main_heading)
                        sheet.write_string(row, col + 13, str(hijri_nid_exp_date), main_heading)
                        sheet.write_string(row, col + 14, str(days), main_heading)
                    if value['bsg_passport_number']:
                        sheet.write_string(row, col + 15, str(value['bsg_passport_number']), main_heading)
                    if value['bsg_passport_expiry']:
                        days = 0
                        delta = value['bsg_passport_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                        sheet.write_string(row, col + 16, str(value['bsg_passport_expiry']), main_heading)
                        sheet.write_string(row, col + 17, str(hijri_passport_exp_date), main_heading)
                        sheet.write_string(row, col + 18, str(days), main_heading)
                    if value['emp_licence_no']:
                        sheet.write(row, col + 19, str(value['emp_licence_no']), main_heading)
                    if value['emp_licence_expiry']:
                        days = 0
                        delta = value['emp_licence_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                        sheet.write(row, col + 20, str(value['emp_licence_expiry']), main_heading)
                        sheet.write(row, col + 21, str(hijri_licence_exp_date), main_heading)
                        sheet.write(row, col + 22, str(days), main_heading)
                    if value['mobile_phone']:
                        sheet.write_string(row, col + 23, str(value['mobile_phone']), main_heading)
                    if value['bsg_driver']:
                        sheet.write_string(row, col + 24, 'Yes', main_heading)
                    if value['taq_number']:
                        sheet.write_string(row, col + 25, str(value['taq_number']), main_heading)
                    if value['make_name']:
                        sheet.write_string(row, col + 26, str(value['make_name']), main_heading)
                    if value['model_name']:
                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                        sheet.write_string(row, col + 27, str(display_name), main_heading)
                    if value['vehicle_status_name']:
                        sheet.write_string(row, col + 28, str(value['vehicle_status_name']), main_heading)
                    if value['vehicle_type_name']:
                        sheet.write_string(row, col + 29, str(value['vehicle_type_name']), main_heading)
                    if value['domain_name']:
                        sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                    if value['model_year']:
                        sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                    if value['estmaira_serial_no']:
                        sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                    if value['analytic_account_name']:
                        sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                    row += 1
                    total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_vehicle_make':
            self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Vehicle Make"
            sheet.merge_range('A1:Q1', 'تقرير السائقين التجميع بحسب ماركة الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Vehicle Make', main_heading3)
            row += 2
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Name', main_heading2)
            sheet.write(row, col + 2, 'Date of Join', main_heading2)
            sheet.write(row, col + 3, 'Emploee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality', main_heading2)
            sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
            sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
            sheet.write(row, col + 7, 'Driver Reward', main_heading2)
            sheet.write(row, col + 8, 'Iqama No.', main_heading2)
            sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
            sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
            sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
            sheet.write(row, col + 12, 'National ID', main_heading2)
            sheet.write(row, col + 13, 'National Expiry date', main_heading2)
            sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
            sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
            sheet.write(row, col + 16, 'Passport Number', main_heading2)
            sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
            sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
            sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
            sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
            sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
            sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
            sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
            sheet.write(row, col + 24, ' Mobile No.', main_heading2)
            sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
            sheet.write(row, col + 26, 'Sticker No.', main_heading2)
            sheet.write(row, col + 27, 'Vehicle Model', main_heading2)
            sheet.write(row, col + 28, 'Vehicle Status', main_heading2)
            sheet.write(row, col + 29, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 30, 'Domain Name', main_heading2)
            sheet.write(row, col + 31, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 32, 'Istmara Serial No.', main_heading2)
            sheet.write(row, col + 33, 'Analytic Account', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
            sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
            sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
            sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
            sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
            sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
            sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
            sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
            sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
            sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
            sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
            sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
            sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
            sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
            sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
            sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
            sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
            sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
            sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 27, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 28, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 29, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 30, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 31, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 32, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 33, 'حساب تحليلي', main_heading2)
            row += 1
            vehicle_make_list=[]
            grand_total=0
            driver_data = driver_data.sort_values(by=['make_name','driver_code'])
            driver_data_make = driver_data.fillna(0)
            for index, value in driver_data_make.iterrows():
                if value['make_name'] not in vehicle_make_list:
                    vehicle_make_list.append(value['make_name'])
            for vehicle_make in vehicle_make_list:
                if vehicle_make:
                    total=0
                    sheet.write(row, col, 'Vehicle Make', main_heading2)
                    sheet.write_string(row, col + 1, str(vehicle_make), main_heading)
                    sheet.write(row, col + 2, 'ماركة الشاحنة', main_heading2)
                    row += 1
                    for index, value in driver_data_make.iterrows():
                        if value['make_name'] == vehicle_make:
                            if value['driver_code']:
                                sheet.write_string(row, col, str(value['driver_code']), main_heading)
                            if value['employee_name']:
                                sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                            if value['employee_join_date']:
                                sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                            if value['employee_state']:
                                if value['employee_state'] == 'on_job':
                                    sheet.write_string(row, col + 3, 'On Job', main_heading)
                                if value['employee_state'] == 'on_leave':
                                    sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                if value['employee_state'] == 'return_from_holiday':
                                    sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                if value['employee_state'] == 'resignation':
                                    sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                if value['employee_state'] == 'suspended':
                                    sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                if value['employee_state'] == 'service_expired':
                                    sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                if value['employee_state'] == 'contract_terminated':
                                    sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                if value['employee_state'] == 'ending_contract_during_trial_period':
                                    sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                       main_heading)
                            if value['country_name']:
                                sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                            if value['leave_start_date']:
                                sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                            if value['last_return_date']:
                                sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                            if value['driver_rewards']:
                                if value['driver_rewards'] == 'by_delivery':
                                    sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                if value['driver_rewards'] == 'by_delivery_b':
                                    sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                if value['driver_rewards'] == 'by_revenue':
                                    sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                if value['driver_rewards'] == 'not_applicable':
                                    sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                            if value['bsg_iqama_name']:
                                sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                            if value['bsg_iqama_expiry']:
                                days = 0
                                delta =  value['bsg_iqama_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                sheet.write_string(row, col + 11, str(days), main_heading)
                            if value['bsg_nationality_name']:
                                sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                            if value['bsg_nid_expiry']:
                                days = 0
                                delta =  value['bsg_nid_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                sheet.write_string(row, col + 15, str(days), main_heading)
                            if value['bsg_passport_number']:
                                sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                            if value['bsg_passport_expiry']:
                                days = 0
                                delta = value['bsg_passport_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                sheet.write_string(row, col + 19, str(days), main_heading)
                            if value['emp_licence_no']:
                                sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                            if value['emp_licence_expiry']:
                                days = 0
                                delta = value['emp_licence_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                sheet.write(row, col + 23, str(days), main_heading)
                            if value['mobile_phone']:
                                sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                            if value['bsg_driver']:
                                sheet.write_string(row, col + 25, 'Yes', main_heading)
                            if value['taq_number']:
                                sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                            if value['model_name']:
                                display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                sheet.write_string(row, col + 27, str(display_name), main_heading)
                            if value['vehicle_status_name']:
                                sheet.write_string(row, col + 28, str(value['vehicle_status_name']), main_heading)
                            if value['vehicle_type_name']:
                                sheet.write_string(row, col + 29, str(value['vehicle_type_name']), main_heading)
                            if value['domain_name']:
                                sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                            if value['model_year']:
                                sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                            if value['estmaira_serial_no']:
                                sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                            if value['analytic_account_name']:
                                sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                            row += 1
                            total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
            driver_data_make = driver_data.fillna(0)
            vehicle_make_null = driver_data_make.loc[(driver_data_make['make_name'] == 0)]
            if not vehicle_make_null.empty:
                total = 0
                sheet.write(row, col, 'Vehicle Make', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'ماركة الشاحنة', main_heading2)
                row += 1
                for index, value in vehicle_make_null.iterrows():
                    if value['driver_code']:
                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                    if value['employee_name']:
                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                    if value['employee_join_date']:
                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                    if value['employee_state']:
                        if value['employee_state'] == 'on_job':
                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                        if value['employee_state'] == 'on_leave':
                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                        if value['employee_state'] == 'return_from_holiday':
                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                        if value['employee_state'] == 'resignation':
                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                        if value['employee_state'] == 'suspended':
                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                        if value['employee_state'] == 'service_expired':
                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                        if value['employee_state'] == 'contract_terminated':
                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                        if value['employee_state'] == 'ending_contract_during_trial_period':
                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                               main_heading)
                    if value['country_name']:
                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                    if value['leave_start_date']:
                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                    if value['last_return_date']:
                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                    if value['driver_rewards']:
                        if value['driver_rewards'] == 'by_delivery':
                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                        if value['driver_rewards'] == 'by_delivery_b':
                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                        if value['driver_rewards'] == 'by_revenue':
                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                        if value['driver_rewards'] == 'not_applicable':
                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                    if value['bsg_iqama_name']:
                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                    if value['bsg_iqama_expiry']:
                        days = 0
                        delta =  value['bsg_iqama_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                        sheet.write_string(row, col + 11, str(days), main_heading)
                    if value['bsg_nationality_name']:
                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                    if value['bsg_nid_expiry']:
                        days = 0
                        delta =  value['bsg_nid_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                        sheet.write_string(row, col + 15, str(days), main_heading)
                    if value['bsg_passport_number']:
                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                    if value['bsg_passport_expiry']:
                        days = 0
                        delta = value['bsg_passport_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                        sheet.write_string(row, col + 19, str(days), main_heading)
                    if value['emp_licence_no']:
                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                    if value['emp_licence_expiry']:
                        days = 0
                        delta = value['emp_licence_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                        sheet.write(row, col + 23, str(days), main_heading)
                    if value['mobile_phone']:
                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                    if value['bsg_driver']:
                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                    if value['taq_number']:
                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                    if value['model_name']:
                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                        sheet.write_string(row, col + 27, str(display_name), main_heading)
                    if value['vehicle_status_name']:
                        sheet.write_string(row, col + 28, str(value['vehicle_status_name']), main_heading)
                    if value['vehicle_type_name']:
                        sheet.write_string(row, col + 29, str(value['vehicle_type_name']), main_heading)
                    if value['domain_name']:
                        sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                    if value['model_year']:
                        sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                    if value['estmaira_serial_no']:
                        sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                    if value['analytic_account_name']:
                        sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                    row += 1
                    total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_vehicle_type_name':
            self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Vehicle Type"
            sheet.merge_range('A1:Q1', 'تقرير السائقين التجميع بحسب نشاط الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Vehicle Type', main_heading3)
            row += 2
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Name', main_heading2)
            sheet.write(row, col + 2, 'Date of Join', main_heading2)
            sheet.write(row, col + 3, 'Emploee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality', main_heading2)
            sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
            sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
            sheet.write(row, col + 7, 'Driver Reward', main_heading2)
            sheet.write(row, col + 8, 'Iqama No.', main_heading2)
            sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
            sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
            sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
            sheet.write(row, col + 12, 'National ID', main_heading2)
            sheet.write(row, col + 13, 'National Expiry date', main_heading2)
            sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
            sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
            sheet.write(row, col + 16, 'Passport Number', main_heading2)
            sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
            sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
            sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
            sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
            sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
            sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
            sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
            sheet.write(row, col + 24, ' Mobile No.', main_heading2)
            sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
            sheet.write(row, col + 26, 'Sticker No.', main_heading2)
            sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
            sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
            sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
            sheet.write(row, col + 30, 'Domain Name', main_heading2)
            sheet.write(row, col + 31, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 32, 'Istmara Serial No.', main_heading2)
            sheet.write(row, col + 33, 'Analytic Account', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
            sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
            sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
            sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
            sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
            sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
            sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
            sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
            sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
            sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
            sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
            sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
            sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
            sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
            sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
            sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
            sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
            sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
            sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 30, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 31, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 32, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 33, 'حساب تحليلي', main_heading2)
            row += 1
            vehicle_type_list=[]
            grand_total=0
            driver_data = driver_data.sort_values(by=['vehicle_type_name','driver_code'])
            driver_data_vehicle_type = driver_data.fillna(0)
            for index, value in driver_data_vehicle_type.iterrows():
                if value['vehicle_type_name'] not in vehicle_type_list:
                    vehicle_type_list.append(value['vehicle_type_name'])
            for vehicle_type in vehicle_type_list:
                if vehicle_type:
                    total=0
                    sheet.write(row, col, 'Vehicle Type', main_heading2)
                    sheet.write_string(row, col + 1, str(vehicle_type), main_heading)
                    sheet.write(row, col + 2, 'نشاط الشاحنة', main_heading2)
                    row += 1
                    for index, value in driver_data_vehicle_type.iterrows():
                        if value['vehicle_type_name'] == vehicle_type:
                            if value['driver_code']:
                                sheet.write_string(row, col, str(value['driver_code']), main_heading)
                            if value['employee_name']:
                                sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                            if value['employee_join_date']:
                                sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                            if value['employee_state']:
                                if value['employee_state'] == 'on_job':
                                    sheet.write_string(row, col + 3, 'On Job', main_heading)
                                if value['employee_state'] == 'on_leave':
                                    sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                if value['employee_state'] == 'return_from_holiday':
                                    sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                if value['employee_state'] == 'resignation':
                                    sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                if value['employee_state'] == 'suspended':
                                    sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                if value['employee_state'] == 'service_expired':
                                    sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                if value['employee_state'] == 'contract_terminated':
                                    sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                if value['employee_state'] == 'ending_contract_during_trial_period':
                                    sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                       main_heading)
                            if value['country_name']:
                                sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                            if value['leave_start_date']:
                                sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                            if value['last_return_date']:
                                sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                            if value['driver_rewards']:
                                if value['driver_rewards'] == 'by_delivery':
                                    sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                if value['driver_rewards'] == 'by_delivery_b':
                                    sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                if value['driver_rewards'] == 'by_revenue':
                                    sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                if value['driver_rewards'] == 'not_applicable':
                                    sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                            if value['bsg_iqama_name']:
                                sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                            if value['bsg_iqama_expiry']:
                                days = 0
                                delta =  value['bsg_iqama_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                sheet.write_string(row, col + 11, str(days), main_heading)
                            if value['bsg_nationality_name']:
                                sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                            if value['bsg_nid_expiry']:
                                days = 0
                                delta =  value['bsg_nid_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                sheet.write_string(row, col + 15, str(days), main_heading)
                            if value['bsg_passport_number']:
                                sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                            if value['bsg_passport_expiry']:
                                days = 0
                                delta = value['bsg_passport_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                sheet.write_string(row, col + 19, str(days), main_heading)
                            if value['emp_licence_no']:
                                sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                            if value['emp_licence_expiry']:
                                days = 0
                                delta = value['emp_licence_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                sheet.write(row, col + 23, str(days), main_heading)
                            if value['mobile_phone']:
                                sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                            if value['bsg_driver']:
                                sheet.write_string(row, col + 25, 'Yes', main_heading)
                            if value['taq_number']:
                                sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                            if value['make_name']:
                                sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                            if value['model_name']:
                                display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                sheet.write_string(row, col + 28, str(display_name), main_heading)
                            if value['vehicle_status_name']:
                                sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                            if value['domain_name']:
                                sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                            if value['model_year']:
                                sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                            if value['estmaira_serial_no']:
                                sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                            if value['analytic_account_name']:
                                sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                            row += 1
                            total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
            driver_data_vehicle_type = driver_data.fillna(0)
            vehicle_type_null = driver_data_vehicle_type.loc[(driver_data['vehicle_type_name'] == 0)]
            if not vehicle_type_null.empty:
                total = 0
                sheet.write(row, col, 'Vehicle Type', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'نشاط الشاحنة', main_heading2)
                row += 1
                for index, value in vehicle_type_null.iterrows():
                    if value['driver_code']:
                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                    if value['employee_name']:
                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                    if value['employee_join_date']:
                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                    if value['employee_state']:
                        if value['employee_state'] == 'on_job':
                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                        if value['employee_state'] == 'on_leave':
                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                        if value['employee_state'] == 'return_from_holiday':
                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                        if value['employee_state'] == 'resignation':
                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                        if value['employee_state'] == 'suspended':
                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                        if value['employee_state'] == 'service_expired':
                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                        if value['employee_state'] == 'contract_terminated':
                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                        if value['employee_state'] == 'ending_contract_during_trial_period':
                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                               main_heading)
                    if value['country_name']:
                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                    if value['leave_start_date']:
                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                    if value['last_return_date']:
                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                    if value['driver_rewards']:
                        if value['driver_rewards'] == 'by_delivery':
                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                        if value['driver_rewards'] == 'by_delivery_b':
                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                        if value['driver_rewards'] == 'by_revenue':
                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                        if value['driver_rewards'] == 'not_applicable':
                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                    if value['bsg_iqama_name']:
                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                    if value['bsg_iqama_expiry']:
                        days = 0
                        delta =  value['bsg_iqama_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                        sheet.write_string(row, col + 11, str(days), main_heading)
                    if value['bsg_nationality_name']:
                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                    if value['bsg_nid_expiry']:
                        days = 0
                        delta =  value['bsg_nid_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                        sheet.write_string(row, col + 15, str(days), main_heading)
                    if value['bsg_passport_number']:
                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                    if value['bsg_passport_expiry']:
                        days = 0
                        delta = value['bsg_passport_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                        sheet.write_string(row, col + 19, str(days), main_heading)
                    if value['emp_licence_no']:
                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                    if value['emp_licence_expiry']:
                        days = 0
                        delta = value['emp_licence_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                        sheet.write(row, col + 23, str(days), main_heading)
                    if value['mobile_phone']:
                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                    if value['bsg_driver']:
                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                    if value['taq_number']:
                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                    if value['make_name']:
                        sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                    if value['model_name']:
                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                        sheet.write_string(row, col + 28, str(display_name), main_heading)
                    if value['vehicle_status_name']:
                        sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                    if value['domain_name']:
                        sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                    if value['model_year']:
                        sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                    if value['estmaira_serial_no']:
                        sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                    if value['analytic_account_name']:
                        sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                    row += 1
                    total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_domain_name':
            self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Vehicle Domain Name"
            sheet.merge_range('A1:Q1', 'تقرير السائقين التجميع بحسب قطاع الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Vehicle Domain Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Name', main_heading2)
            sheet.write(row, col + 2, 'Date of Join', main_heading2)
            sheet.write(row, col + 3, 'Emploee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality', main_heading2)
            sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
            sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
            sheet.write(row, col + 7, 'Driver Reward', main_heading2)
            sheet.write(row, col + 8, 'Iqama No.', main_heading2)
            sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
            sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
            sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
            sheet.write(row, col + 12, 'National ID', main_heading2)
            sheet.write(row, col + 13, 'National Expiry date', main_heading2)
            sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
            sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
            sheet.write(row, col + 16, 'Passport Number', main_heading2)
            sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
            sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
            sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
            sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
            sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
            sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
            sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
            sheet.write(row, col + 24, ' Mobile No.', main_heading2)
            sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
            sheet.write(row, col + 26, 'Sticker No.', main_heading2)
            sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
            sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
            sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
            sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 31, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 32, 'Istmara Serial No.', main_heading2)
            sheet.write(row, col + 33, 'Analytic Account', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
            sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
            sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
            sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
            sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
            sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
            sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
            sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
            sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
            sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
            sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
            sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
            sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
            sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
            sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
            sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
            sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
            sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
            sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 31, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 32, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 33, 'حساب تحليلي', main_heading2)
            row += 1
            vehicle_domain_list=[]
            grand_total=0
            driver_data = driver_data.sort_values(by=['domain_name','driver_code'])
            driver_data_domain = driver_data.fillna(0)
            for index, value in driver_data_domain.iterrows():
                if value['domain_name'] not in vehicle_domain_list:
                    vehicle_domain_list.append(value['domain_name'])
            for vehicle_domain in vehicle_domain_list:
                if vehicle_domain:
                    total=0
                    sheet.write(row, col, 'Domain Name', main_heading2)
                    sheet.write_string(row, col + 1, str(vehicle_domain), main_heading)
                    sheet.write(row, col + 2, 'قطاع الشاحنة', main_heading2)
                    row += 1
                    for index, value in driver_data_domain.iterrows():
                        if value['domain_name'] == vehicle_domain:
                            if value['driver_code']:
                                sheet.write_string(row, col, str(value['driver_code']), main_heading)
                            if value['employee_name']:
                                sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                            if value['employee_join_date']:
                                sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                            if value['employee_state']:
                                if value['employee_state'] == 'on_job':
                                    sheet.write_string(row, col + 3, 'On Job', main_heading)
                                if value['employee_state'] == 'on_leave':
                                    sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                if value['employee_state'] == 'return_from_holiday':
                                    sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                if value['employee_state'] == 'resignation':
                                    sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                if value['employee_state'] == 'suspended':
                                    sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                if value['employee_state'] == 'service_expired':
                                    sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                if value['employee_state'] == 'contract_terminated':
                                    sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                if value['employee_state'] == 'ending_contract_during_trial_period':
                                    sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                       main_heading)
                            if value['country_name']:
                                sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                            if value['leave_start_date']:
                                sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                            if value['last_return_date']:
                                sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                            if value['driver_rewards']:
                                if value['driver_rewards'] == 'by_delivery':
                                    sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                if value['driver_rewards'] == 'by_delivery_b':
                                    sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                if value['driver_rewards'] == 'by_revenue':
                                    sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                if value['driver_rewards'] == 'not_applicable':
                                    sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                            if value['bsg_iqama_name']:
                                sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                            if value['bsg_iqama_expiry']:
                                days = 0
                                delta =  value['bsg_iqama_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                sheet.write_string(row, col + 11, str(days), main_heading)
                            if value['bsg_nationality_name']:
                                sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                            if value['bsg_nid_expiry']:
                                days = 0
                                delta =  value['bsg_nid_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                sheet.write_string(row, col + 15, str(days), main_heading)
                            if value['bsg_passport_number']:
                                sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                            if value['bsg_passport_expiry']:
                                days = 0
                                delta = value['bsg_passport_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                sheet.write_string(row, col + 19, str(days), main_heading)
                            if value['emp_licence_no']:
                                sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                            if value['emp_licence_expiry']:
                                days = 0
                                delta = value['emp_licence_expiry'] - date.today()
                                days = int(delta.days)
                                hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                sheet.write(row, col + 23, str(days), main_heading)
                            if value['mobile_phone']:
                                sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                            if value['bsg_driver']:
                                sheet.write_string(row, col + 25, 'Yes', main_heading)
                            if value['taq_number']:
                                sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                            if value['make_name']:
                                sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                            if value['model_name']:
                                display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                sheet.write_string(row, col + 28, str(display_name), main_heading)
                            if value['vehicle_status_name']:
                                sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                            if value['vehicle_type_name']:
                                sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                            if value['model_year']:
                                sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                            if value['estmaira_serial_no']:
                                sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                            if value['analytic_account_name']:
                                sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                            row += 1
                            total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
            driver_data_domain = driver_data.fillna(0)
            vehicle_domain_null = driver_data_domain.loc[(driver_data['domain_name'] == 0)]
            if not vehicle_domain_null.empty:
                total = 0
                sheet.write(row, col, 'Domain Name', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'قطاع الشاحنة', main_heading2)
                row += 1
                for index, value in vehicle_domain_null.iterrows():
                    if value['driver_code']:
                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                    if value['employee_name']:
                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                    if value['employee_join_date']:
                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                    if value['employee_state']:
                        if value['employee_state'] == 'on_job':
                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                        if value['employee_state'] == 'on_leave':
                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                        if value['employee_state'] == 'return_from_holiday':
                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                        if value['employee_state'] == 'resignation':
                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                        if value['employee_state'] == 'suspended':
                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                        if value['employee_state'] == 'service_expired':
                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                        if value['employee_state'] == 'contract_terminated':
                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                        if value['employee_state'] == 'ending_contract_during_trial_period':
                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                               main_heading)
                    if value['country_name']:
                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                    if value['leave_start_date']:
                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                    if value['last_return_date']:
                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                    if value['driver_rewards']:
                        if value['driver_rewards'] == 'by_delivery':
                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                        if value['driver_rewards'] == 'by_delivery_b':
                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                        if value['driver_rewards'] == 'by_revenue':
                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                        if value['driver_rewards'] == 'not_applicable':
                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                    if value['bsg_iqama_name']:
                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                    if value['bsg_iqama_expiry']:
                        days = 0
                        delta =  value['bsg_iqama_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                        sheet.write_string(row, col + 11, str(days), main_heading)
                    if value['bsg_nationality_name']:
                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                    if value['bsg_nid_expiry']:
                        days = 0
                        delta =  value['bsg_nid_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                        sheet.write_string(row, col + 15, str(days), main_heading)
                    if value['bsg_passport_number']:
                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                    if value['bsg_passport_expiry']:
                        days = 0
                        delta = value['bsg_passport_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                        sheet.write_string(row, col + 19, str(days), main_heading)
                    if value['emp_licence_no']:
                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                    if value['emp_licence_expiry']:
                        days = 0
                        delta = value['emp_licence_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                        sheet.write(row, col + 23, str(days), main_heading)
                    if value['mobile_phone']:
                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                    if value['bsg_driver']:
                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                    if value['taq_number']:
                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                    if value['make_name']:
                        sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                    if value['model_name']:
                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                        sheet.write_string(row, col + 28, str(display_name), main_heading)
                    if value['vehicle_status_name']:
                        sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                    if value['vehicle_type_name']:
                        sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                    if value['model_year']:
                        sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                    if value['estmaira_serial_no']:
                        sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                    if value['analytic_account_name']:
                        sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                    row += 1
                    total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_link_name':
            self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Driver Link"
            sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب رابط السائق', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Driver Link', main_heading3)
            row += 2
            sheet.write(row, col, 'Employee ID', main_heading2)
            sheet.write(row, col + 1, 'Employee Name', main_heading2)
            sheet.write(row, col + 2, 'Date of Join', main_heading2)
            sheet.write(row, col + 3, 'Emploee Status', main_heading2)
            sheet.write(row, col + 4, 'Nationality', main_heading2)
            sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
            sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
            sheet.write(row, col + 7, 'Driver Reward', main_heading2)
            sheet.write(row, col + 8, 'Iqama No.', main_heading2)
            sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
            sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
            sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
            sheet.write(row, col + 12, 'National ID', main_heading2)
            sheet.write(row, col + 13, 'National Expiry date', main_heading2)
            sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
            sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
            sheet.write(row, col + 16, 'Passport Number', main_heading2)
            sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
            sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
            sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
            sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
            sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
            sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
            sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
            sheet.write(row, col + 24, ' Mobile No.', main_heading2)
            sheet.write(row, col + 25, 'Sticker No.', main_heading2)
            sheet.write(row, col + 26, 'Vehicle Make', main_heading2)
            sheet.write(row, col + 27, 'Vehicle Model', main_heading2)
            sheet.write(row, col + 28, 'Vehicle Status', main_heading2)
            sheet.write(row, col + 29, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 30, 'Domain Name', main_heading2)
            sheet.write(row, col + 31, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 32, 'Istmara Serial No.', main_heading2)
            sheet.write(row, col + 33, 'Analytic Account', main_heading2)
            row += 1
            sheet.write(row, col, 'كود الموظف', main_heading2)
            sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
            sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
            sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
            sheet.write(row, col + 4, 'الجنسية', main_heading2)
            sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
            sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
            sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
            sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
            sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
            sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
            sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
            sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
            sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
            sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
            sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
            sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
            sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
            sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
            sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
            sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
            sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
            sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
            sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
            sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
            sheet.write(row, col + 25, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 26, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 27, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 28, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 29, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 30, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 31, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 32, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 33, 'حساب تحليلي', main_heading2)
            row += 1
            grand_total=0
            driver_data_link = driver_data.fillna(0)
            driver_linked = driver_data_link.loc[(driver_data_link['bsg_driver'] != 0)]
            driver_unlinked = driver_data_link.loc[(driver_data_link['bsg_driver'] == 0)]
            if not driver_linked.empty:
                total = 0
                sheet.write(row, col, 'Driver Link', main_heading2)
                sheet.write_string(row, col + 1, 'Linked', main_heading)
                sheet.write(row, col + 2, 'رابط السائق', main_heading2)
                row += 1
                for index, value in driver_linked.iterrows():
                    if value['driver_code']:
                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                    if value['employee_name']:
                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                    if value['employee_join_date']:
                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                    if value['employee_state']:
                        if value['employee_state'] == 'on_job':
                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                        if value['employee_state'] == 'on_leave':
                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                        if value['employee_state'] == 'return_from_holiday':
                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                        if value['employee_state'] == 'resignation':
                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                        if value['employee_state'] == 'suspended':
                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                        if value['employee_state'] == 'service_expired':
                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                        if value['employee_state'] == 'contract_terminated':
                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                        if value['employee_state'] == 'ending_contract_during_trial_period':
                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                               main_heading)
                    if value['country_name']:
                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                    if value['leave_start_date']:
                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                    if value['last_return_date']:
                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                    if value['driver_rewards']:
                        if value['driver_rewards'] == 'by_delivery':
                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                        if value['driver_rewards'] == 'by_delivery_b':
                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                        if value['driver_rewards'] == 'by_revenue':
                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                        if value['driver_rewards'] == 'not_applicable':
                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                    if value['bsg_iqama_name']:
                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                    if value['bsg_iqama_expiry']:
                        days = 0
                        delta =  value['bsg_iqama_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                        sheet.write_string(row, col + 11, str(days), main_heading)
                    if value['bsg_nationality_name']:
                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                    if value['bsg_nid_expiry']:
                        days = 0
                        delta =  value['bsg_nid_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                        sheet.write_string(row, col + 15, str(days), main_heading)
                    if value['bsg_passport_number']:
                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                    if value['bsg_passport_expiry']:
                        days = 0
                        delta = value['bsg_passport_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                        sheet.write_string(row, col + 19, str(days), main_heading)
                    if value['emp_licence_no']:
                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                    if value['emp_licence_expiry']:
                        days = 0
                        delta = value['emp_licence_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                        sheet.write(row, col + 23, str(days), main_heading)
                    if value['mobile_phone']:
                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                    if value['taq_number']:
                        sheet.write_string(row, col + 25, str(value['taq_number']), main_heading)
                    if value['make_name']:
                        sheet.write_string(row, col + 26, str(value['make_name']), main_heading)
                    if value['model_name']:
                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                        sheet.write_string(row, col + 27, str(display_name), main_heading)
                    if value['vehicle_status_name']:
                        sheet.write_string(row, col + 28, str(value['vehicle_status_name']), main_heading)
                    if value['vehicle_type_name']:
                        sheet.write_string(row, col + 29, str(value['vehicle_type_name']), main_heading)
                    if value['domain_name']:
                        sheet.write_string(row, col + 30, str([value['domain_name']]), main_heading)
                    if value['model_year']:
                        sheet.write_string(row, col + 31, str(value['model_year']), main_heading)
                    if value['estmaira_serial_no']:
                        sheet.write_string(row, col + 32, str(value['estmaira_serial_no']), main_heading)
                    if value['analytic_account_name']:
                        sheet.write_string(row, col + 33, str(value['analytic_account_name']), main_heading)
                    row += 1
                    total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            if not driver_unlinked.empty:
                total = 0
                sheet.write(row, col, 'Driver Link', main_heading2)
                sheet.write_string(row, col + 1, 'Unlinked', main_heading)
                sheet.write(row, col + 2, 'رابط السائق', main_heading2)
                row += 1
                for index, value in driver_unlinked.iterrows():
                    if value['driver_code']:
                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                    if value['employee_name']:
                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                    if value['employee_join_date']:
                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                    if value['employee_state']:
                        if value['employee_state'] == 'on_job':
                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                        if value['employee_state'] == 'on_leave':
                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                        if value['employee_state'] == 'return_from_holiday':
                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                        if value['employee_state'] == 'resignation':
                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                        if value['employee_state'] == 'suspended':
                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                        if value['employee_state'] == 'service_expired':
                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                        if value['employee_state'] == 'contract_terminated':
                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                        if value['employee_state'] == 'ending_contract_during_trial_period':
                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                               main_heading)
                    if value['country_name']:
                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                    if value['leave_start_date']:
                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                    if value['last_return_date']:
                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                    if value['driver_rewards']:
                        if value['driver_rewards'] == 'by_delivery':
                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                        if value['driver_rewards'] == 'by_delivery_b':
                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                        if value['driver_rewards'] == 'by_revenue':
                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                        if value['driver_rewards'] == 'not_applicable':
                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                    if value['bsg_iqama_name']:
                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                    if value['bsg_iqama_expiry']:
                        days = 0
                        delta =  value['bsg_iqama_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                        sheet.write_string(row, col + 11, str(days), main_heading)
                    if value['bsg_nationality_name']:
                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                    if value['bsg_nid_expiry']:
                        days = 0
                        delta =  value['bsg_nid_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                        sheet.write_string(row, col + 15, str(days), main_heading)
                    if value['bsg_passport_number']:
                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                    if value['bsg_passport_expiry']:
                        days = 0
                        delta = value['bsg_passport_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                        sheet.write_string(row, col + 19, str(days), main_heading)
                    if value['emp_licence_no']:
                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                    if value['emp_licence_expiry']:
                        days = 0
                        delta = value['emp_licence_expiry'] - date.today()
                        days = int(delta.days)
                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                        sheet.write(row, col + 23, str(days), main_heading)
                    if value['mobile_phone']:
                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                    if value['bsg_driver']:
                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                    if value['taq_number']:
                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                    if value['make_name']:
                        sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                    if value['model_name']:
                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                        sheet.write_string(row, col + 28, str(display_name), main_heading)
                    if value['vehicle_status_name']:
                        sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                    if value['vehicle_type_name']:
                        sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                    if value['domain_name']:
                        sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                    if value['model_year']:
                        sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                    if value['estmaira_serial_no']:
                        sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                    if value['analytic_account_name']:
                        sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                    row += 1
                    total += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_iqama_expiry':
            driver_data['bsg_iqama_expiry']= pd.to_datetime(driver_data['bsg_iqama_expiry'])
            driver_data = driver_data.sort_values(by=['bsg_iqama_expiry','driver_code'])
            driver_data['bsg_iqama_expiry'] = pd.to_datetime(driver_data['bsg_iqama_expiry']).dt.date
            driver_data_iqama = driver_data.fillna(0)
            if not docs.period_grouping_by:
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Iqama Expiry Period Group By Date"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب مجموعة فترة انتهاء الإقامة حسب التاريخ', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Iqama Expiry Period Group By Date', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                date_list=[]
                grand_total=0
                for index, value in driver_data_iqama.iterrows():
                    if value['bsg_iqama_expiry'] not in date_list:
                        date_list.append(value['bsg_iqama_expiry'])
                for iqama_exp_date in date_list:
                    if iqama_exp_date:
                        total=0
                        sheet.write(row, col,'Date', main_heading2)
                        sheet.write_string(row, col + 1,str(iqama_exp_date), main_heading)
                        sheet.write(row, col + 2, 'تاريخ', main_heading2)
                        row += 1
                        for index, value in driver_data_iqama.iterrows():
                            if value['bsg_iqama_expiry'] == iqama_exp_date:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                iqama_expiry_null = driver_data_iqama.loc[(driver_data_iqama['bsg_iqama_expiry']==0)]
                if not iqama_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Date', main_heading2)
                    sheet.write_string(row, col + 1,'Undefined', main_heading)
                    sheet.write(row, col + 2, 'تاريخ', main_heading2)
                    row += 1
                    for index, value in iqama_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'day':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Iqama Expiry Period Group By Day"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الإقامة مجموعة حسب اليوم', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Iqama Expiry Period Group By Day', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                days_list = []
                grand_total = 0
                day_name = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
                for index, value in driver_data_iqama.iterrows():
                    if value['bsg_iqama_expiry']:
                        day = value['bsg_iqama_expiry'].weekday()
                        if day_name[day] not in days_list:
                            days_list.append(day_name[day])
                if days_list:
                    for day_id in days_list:
                        if day_id:
                            total = 0
                            sheet.write(row, col, 'Day', main_heading2)
                            sheet.write_string(row, col + 1, str(day_id), main_heading)
                            sheet.write(row, col + 2, 'يوم', main_heading2)
                            row += 1
                            for index, value in driver_data_iqama.iterrows():
                                if value['bsg_iqama_expiry']:
                                    day_val = value['bsg_iqama_expiry'].weekday()
                                    if day_name[day_val] == day_id:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                iqama_expiry_null = driver_data_iqama.loc[(driver_data_iqama['bsg_iqama_expiry'] == 0)]
                if not iqama_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Day', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'يوم', main_heading2)
                    row += 1
                    for index, value in iqama_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'weekly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Iqama Expiry Period Group By Week"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب مجموعة فترة انتهاء الإقامة حسب الأسبوع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Iqama Expiry Period Group By Week', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                week_list = []
                grand_total = 0
                for index, value in driver_data_iqama.iterrows():
                    if value['bsg_iqama_expiry']:
                        year = value['bsg_iqama_expiry'].year
                        week = value['bsg_iqama_expiry'].strftime("%V")
                        year_week = "year %s Week %s" % (year, week)
                        if year_week not in week_list:
                            week_list.append(year_week)
                for week in week_list:
                    if week:
                        total = 0
                        sheet.write(row, col, 'Week', main_heading2)
                        sheet.write_string(row, col + 1, str(week), main_heading)
                        sheet.write(row, col + 2, 'أسبوع', main_heading2)
                        row += 1
                        for index,value in driver_data_iqama.iterrows():
                            if value['bsg_iqama_expiry']:
                                year_doc = value['bsg_iqama_expiry'].year
                                week_doc = value['bsg_iqama_expiry'].strftime("%V")
                                year_week_doc = "year %s Week %s" % (year_doc, week_doc)
                                if year_week_doc == week:
                                    if value['driver_code']:
                                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                    if value['employee_name']:
                                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                    if value['employee_join_date']:
                                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                    if value['employee_state']:
                                        if value['employee_state'] == 'on_job':
                                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                                        if value['employee_state'] == 'on_leave':
                                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                        if value['employee_state'] == 'return_from_holiday':
                                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                        if value['employee_state'] == 'resignation':
                                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                        if value['employee_state'] == 'suspended':
                                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                        if value['employee_state'] == 'service_expired':
                                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                        if value['employee_state'] == 'contract_terminated':
                                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                        if value['employee_state'] == 'ending_contract_during_trial_period':
                                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                               main_heading)
                                    if value['country_name']:
                                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                    if value['leave_start_date']:
                                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                    if value['last_return_date']:
                                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                    if value['driver_rewards']:
                                        if value['driver_rewards'] == 'by_delivery':
                                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                        if value['driver_rewards'] == 'by_delivery_b':
                                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                        if value['driver_rewards'] == 'by_revenue':
                                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                        if value['driver_rewards'] == 'not_applicable':
                                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                    if value['bsg_iqama_name']:
                                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                    if value['bsg_iqama_expiry']:
                                        days = 0
                                        delta =  value['bsg_iqama_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                        sheet.write_string(row, col + 11, str(days), main_heading)
                                    if value['bsg_nationality_name']:
                                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                           main_heading)
                                    if value['bsg_nid_expiry']:
                                        days = 0
                                        delta =  value['bsg_nid_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                        sheet.write_string(row, col + 15, str(days), main_heading)
                                    if value['bsg_passport_number']:
                                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                           main_heading)
                                    if value['bsg_passport_expiry']:
                                        days = 0
                                        delta = value['bsg_passport_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                           main_heading)
                                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                        sheet.write_string(row, col + 19, str(days), main_heading)
                                    if value['emp_licence_no']:
                                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                    if value['emp_licence_expiry']:
                                        days = 0
                                        delta = value['emp_licence_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                        sheet.write(row, col + 23, str(days), main_heading)
                                    if value['mobile_phone']:
                                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                    if value['bsg_driver']:
                                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                                    if value['taq_number']:
                                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                    if value['make_name']:
                                        sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                    if value['model_name']:
                                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                        sheet.write_string(row, col + 28, str(display_name), main_heading)
                                    if value['vehicle_status_name']:
                                        sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                           main_heading)
                                    if value['vehicle_type_name']:
                                        sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                    if value['domain_name']:
                                        sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                    if value['model_year']:
                                        sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                    if value['estmaira_serial_no']:
                                        sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                           main_heading)
                                    if value['analytic_account_name']:
                                        sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                           main_heading)
                                    row += 1
                                    total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                iqama_expiry_null = driver_data_iqama.loc[(driver_data_iqama['bsg_iqama_expiry'] == 0)]
                if not iqama_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Week', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'أسبوع', main_heading2)
                    row += 1
                    for index, value in iqama_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'month':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Iqama Expiry Period Group By Month"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب مجموعة فترة انتهاء الإقامة حسب الشهر', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Iqama Expiry Period Group By Month', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                months_list = []
                grand_total = 0
                for index,value in driver_data_iqama.iterrows():
                    if value['bsg_iqama_expiry']:
                        if value['bsg_iqama_expiry'].strftime('%B') not in months_list:
                            months_list.append(value['bsg_iqama_expiry'].strftime('%B'))
                for month in months_list:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, str(month), main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index,value in driver_data_iqama.iterrows():
                        if value['bsg_iqama_expiry']:
                            if value['bsg_iqama_expiry'].strftime('%B') == month:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                iqama_expiry_null = driver_data_iqama.loc[(driver_data_iqama['bsg_iqama_expiry'] == 0)]
                if not iqama_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index, value in iqama_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'quarterly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Iqama Expiry Period Group By Quarter"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب مجموعة فترة انتهاء الإقامة حسب الربع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Iqama Expiry Period Group By Quarter', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                driver_data_not_null_exp = driver_data_iqama.loc[(driver_data_iqama['bsg_iqama_expiry']!=0)]
                driver_data_not_null_exp['iqama_exp_month'] = pd.DatetimeIndex(driver_data_not_null_exp['bsg_iqama_expiry']).month
                first_quarter = [1, 2, 3]
                second_quarter = [4, 5, 6]
                third_quarter = [7, 8, 9]
                fourth_quarter = [10,11,12]
                first_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['iqama_exp_month'].isin(first_quarter))]
                second_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['iqama_exp_month'].isin(second_quarter))]
                third_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['iqama_exp_month'].isin(third_quarter))]
                fourth_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['iqama_exp_month'].isin(fourth_quarter))]
                grand_total = 0
                if not first_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'First', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in first_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not second_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Second', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in second_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not third_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Third', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in third_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not fourth_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Fourth', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in fourth_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                iqama_expiry_null = driver_data_iqama.loc[(driver_data_iqama['bsg_iqama_expiry'] == 0)]
                if not iqama_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index, value in iqama_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'year':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Iqama Expiry Period Group By Year"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الإقامة مجموعة حسب السنة', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Iqama Expiry Period Group By Year', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                years_list = []
                grand_total = 0
                for index,value in driver_data_iqama.iterrows():
                    if value['bsg_iqama_expiry']:
                        if value['bsg_iqama_expiry'].year not in years_list:
                            years_list.append(value['bsg_iqama_expiry'].year)
                if years_list:
                    for year in years_list:
                        if year:
                            total = 0
                            sheet.write(row, col, 'Year', main_heading2)
                            sheet.write_string(row, col + 1, str(year), main_heading)
                            sheet.write(row, col + 2, 'عام', main_heading2)
                            row += 1
                            for index,value in driver_data_iqama.iterrows():
                                if value['bsg_iqama_expiry']:
                                    if value['bsg_iqama_expiry'].year == year:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                iqama_expiry_null = driver_data_iqama.loc[(driver_data_iqama['bsg_iqama_expiry'] == 0)]
                if not iqama_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Year', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'عام', main_heading2)
                    row += 1
                    for index, value in iqama_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_nid_expiry':
            driver_data['bsg_nid_expiry'] = pd.to_datetime(driver_data['bsg_nid_expiry'])
            driver_data = driver_data.sort_values(by=['bsg_nid_expiry', 'driver_code'])
            driver_data['bsg_nid_expiry'] = pd.to_datetime(driver_data['bsg_nid_expiry']).dt.date
            driver_data_nid = driver_data.fillna(0)
            if not docs.period_grouping_by:
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By National ID Expiry Period Group By Date"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب الرقم القومي مجموعة فترة انتهاء الصلاحية حسب التاريخ', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By National ID Expiry Period Group By Date', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                date_list=[]
                grand_total=0
                for index, value in driver_data_nid.iterrows():
                    if value['bsg_nid_expiry'] not in date_list:
                        date_list.append(value['bsg_nid_expiry'])
                for nid_exp_date in date_list:
                    if nid_exp_date:
                        total=0
                        sheet.write(row, col,'Date', main_heading2)
                        sheet.write_string(row, col + 1,str(nid_exp_date), main_heading)
                        sheet.write(row, col + 2, 'تاريخ', main_heading2)
                        row += 1
                        for index, value in driver_data_nid.iterrows():
                            if value['bsg_nid_expiry'] == nid_exp_date:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                nid_expiry_null = driver_data_nid.loc[(driver_data_nid['bsg_nid_expiry']==0)]
                if not nid_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Date', main_heading2)
                    sheet.write_string(row, col + 1,'Undefined', main_heading)
                    sheet.write(row, col + 2, 'تاريخ', main_heading2)
                    row += 1
                    for index, value in nid_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'day':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By National ID Expiry Period Group By Day"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الهوية الوطنية مجموعة حسب اليوم', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By National ID Expiry Period Group By Day', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                days_list = []
                grand_total = 0
                day_name = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
                for index, value in driver_data_nid.iterrows():
                    if value['bsg_nid_expiry']:
                        day = value['bsg_nid_expiry'].weekday()
                        if day_name[day] not in days_list:
                            days_list.append(day_name[day])
                if days_list:
                    for day_id in days_list:
                        if day_id:
                            total = 0
                            sheet.write(row, col, 'Day', main_heading2)
                            sheet.write_string(row, col + 1, str(day_id), main_heading)
                            sheet.write(row, col + 2, 'يوم', main_heading2)
                            row += 1
                            for index, value in driver_data_nid.iterrows():
                                if value['bsg_nid_expiry']:
                                    day_val = value['bsg_nid_expiry'].weekday()
                                    if day_name[day_val] == day_id:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                nid_expiry_null = driver_data_nid.loc[(driver_data_nid['bsg_nid_expiry'] == 0)]
                if not nid_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Day', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'يوم', main_heading2)
                    row += 1
                    for index, value in nid_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'weekly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By National ID Period Group By Week"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة الهوية الوطنية مجموعة حسب الأسبوع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By National ID Period Group By Week', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                week_list = []
                grand_total = 0
                for index, value in driver_data_nid.iterrows():
                    if value['bsg_nid_expiry']:
                        year = value['bsg_nid_expiry'].year
                        week = value['bsg_nid_expiry'].strftime("%V")
                        year_week = "year %s Week %s" % (year, week)
                        if year_week not in week_list:
                            week_list.append(year_week)
                for week in week_list:
                    if week:
                        total = 0
                        sheet.write(row, col, 'Week', main_heading2)
                        sheet.write_string(row, col + 1, str(week), main_heading)
                        sheet.write(row, col + 2, 'أسبوع', main_heading2)
                        row += 1
                        for index,value in driver_data_nid.iterrows():
                            if value['bsg_nid_expiry']:
                                year_doc = value['bsg_nid_expiry'].year
                                week_doc = value['bsg_nid_expiry'].strftime("%V")
                                year_week_doc = "year %s Week %s" % (year_doc, week_doc)
                                if year_week_doc == week:
                                    if value['driver_code']:
                                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                    if value['employee_name']:
                                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                    if value['employee_join_date']:
                                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                    if value['employee_state']:
                                        if value['employee_state'] == 'on_job':
                                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                                        if value['employee_state'] == 'on_leave':
                                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                        if value['employee_state'] == 'return_from_holiday':
                                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                        if value['employee_state'] == 'resignation':
                                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                        if value['employee_state'] == 'suspended':
                                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                        if value['employee_state'] == 'service_expired':
                                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                        if value['employee_state'] == 'contract_terminated':
                                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                        if value['employee_state'] == 'ending_contract_during_trial_period':
                                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                               main_heading)
                                    if value['country_name']:
                                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                    if value['leave_start_date']:
                                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                    if value['last_return_date']:
                                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                    if value['driver_rewards']:
                                        if value['driver_rewards'] == 'by_delivery':
                                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                        if value['driver_rewards'] == 'by_delivery_b':
                                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                        if value['driver_rewards'] == 'by_revenue':
                                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                        if value['driver_rewards'] == 'not_applicable':
                                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                    if value['bsg_iqama_name']:
                                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                    if value['bsg_iqama_expiry']:
                                        days = 0
                                        delta =  value['bsg_iqama_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                        sheet.write_string(row, col + 11, str(days), main_heading)
                                    if value['bsg_nationality_name']:
                                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                           main_heading)
                                    if value['bsg_nid_expiry']:
                                        days = 0
                                        delta =  value['bsg_nid_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                        sheet.write_string(row, col + 15, str(days), main_heading)
                                    if value['bsg_passport_number']:
                                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                           main_heading)
                                    if value['bsg_passport_expiry']:
                                        days = 0
                                        delta = value['bsg_passport_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                           main_heading)
                                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                        sheet.write_string(row, col + 19, str(days), main_heading)
                                    if value['emp_licence_no']:
                                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                    if value['emp_licence_expiry']:
                                        days = 0
                                        delta = value['emp_licence_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                        sheet.write(row, col + 23, str(days), main_heading)
                                    if value['mobile_phone']:
                                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                    if value['bsg_driver']:
                                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                                    if value['taq_number']:
                                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                    if value['make_name']:
                                        sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                    if value['model_name']:
                                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                        sheet.write_string(row, col + 28, str(display_name), main_heading)
                                    if value['vehicle_status_name']:
                                        sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                           main_heading)
                                    if value['vehicle_type_name']:
                                        sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                    if value['domain_name']:
                                        sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                    if value['model_year']:
                                        sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                    if value['estmaira_serial_no']:
                                        sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                           main_heading)
                                    if value['analytic_account_name']:
                                        sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                           main_heading)
                                    row += 1
                                    total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                nid_expiry_null = driver_data_nid.loc[(driver_data_nid['bsg_nid_expiry'] == 0)]
                if not nid_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Week', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'أسبوع', main_heading2)
                    row += 1
                    for index, value in nid_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'month':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By National ID Expiry Period Group By Month"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الهوية الوطنية مجموعة حسب الشهر', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By National ID Expiry Period Group By Month', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                months_list = []
                grand_total = 0
                for index,value in driver_data_nid.iterrows():
                    if value['bsg_nid_expiry']:
                        if value['bsg_nid_expiry'].strftime('%B') not in months_list:
                            months_list.append(value['bsg_nid_expiry'].strftime('%B'))
                for month in months_list:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, str(month), main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index,value in driver_data_nid.iterrows():
                        if value['bsg_nid_expiry']:
                            if value['bsg_nid_expiry'].strftime('%B') == month:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                nid_expiry_null = driver_data_nid.loc[(driver_data_nid['bsg_nid_expiry'] == 0)]
                if not nid_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index, value in nid_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'quarterly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By National ID Period Group By Quarter"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة الهوية الوطنية المجموعة حسب الربع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By National ID Period Group By Quarter', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                driver_data_not_null_exp = driver_data_nid.loc[(driver_data_nid['bsg_nid_expiry']!=0)]
                driver_data_not_null_exp['nid_exp_month'] = pd.DatetimeIndex(driver_data_not_null_exp['bsg_nid_expiry']).month
                print(driver_data)
                first_quarter = [1, 2, 3]
                second_quarter = [4, 5, 6]
                third_quarter = [7, 8, 9]
                fourth_quarter = [10,11,12]
                first_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['nid_exp_month'].isin(first_quarter))]
                second_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['nid_exp_month'].isin(second_quarter))]
                third_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['nid_exp_month'].isin(third_quarter))]
                fourth_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['nid_exp_month'].isin(fourth_quarter))]
                grand_total = 0
                if not first_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'First', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in first_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not second_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Second', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in second_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not third_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Third', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in third_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not fourth_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Fourth', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in fourth_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                nid_expiry_null = driver_data_nid.loc[(driver_data_nid['bsg_nid_expiry'] == 0)]
                if not nid_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index, value in nid_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'year':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By National ID Expiry Period Group By Year"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الهوية الوطنية المجموعة حسب السنة', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By National ID Expiry Period Group By Year', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                years_list = []
                grand_total = 0
                for index,value in driver_data_nid.iterrows():
                    if value['bsg_nid_expiry']:
                        if value['bsg_nid_expiry'].year not in years_list:
                            years_list.append(value['bsg_nid_expiry'].year)
                if years_list:
                    for year in years_list:
                        if year:
                            total = 0
                            sheet.write(row, col, 'Year', main_heading2)
                            sheet.write_string(row, col + 1, str(year), main_heading)
                            sheet.write(row, col + 2, 'عام', main_heading2)
                            row += 1
                            for index,value in driver_data_nid.iterrows():
                                if value['bsg_nid_expiry']:
                                    if value['bsg_nid_expiry'].year == year:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                nid_expiry_null = driver_data_nid.loc[(driver_data_nid['bsg_nid_expiry'] == 0)]
                if not nid_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Year', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'عام', main_heading2)
                    row += 1
                    for index, value in nid_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_passport_expiry':
            driver_data['bsg_passport_expiry'] = pd.to_datetime(driver_data['bsg_passport_expiry'])
            driver_data = driver_data.sort_values(by=['bsg_passport_expiry', 'driver_code'])
            driver_data['bsg_passport_expiry'] = pd.to_datetime(driver_data['bsg_passport_expiry']).dt.date
            driver_data_passport = driver_data.fillna(0)
            if not docs.period_grouping_by:
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Passport Expiry Period Group By Date"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب مجموعة فترة انتهاء صلاحية جواز السفر حسب التاريخ', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Passport Expiry Period Group By Date', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                date_list=[]
                grand_total=0
                for index, value in driver_data_passport.iterrows():
                    if value['bsg_passport_expiry'] not in date_list:
                        date_list.append(value['bsg_passport_expiry'])
                for passport_exp_date in date_list:
                    if passport_exp_date:
                        total=0
                        sheet.write(row, col,'Date', main_heading2)
                        sheet.write_string(row, col + 1,str(passport_exp_date), main_heading)
                        sheet.write(row, col + 2, 'تاريخ', main_heading2)
                        row += 1
                        for index, value in driver_data_passport.iterrows():
                            if value['bsg_passport_expiry'] == passport_exp_date:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                passport_expiry_null = driver_data_passport.loc[(driver_data_passport['bsg_passport_expiry']==0)]
                if not passport_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Date', main_heading2)
                    sheet.write_string(row, col + 1,'Undefined', main_heading)
                    sheet.write(row, col + 2, 'تاريخ', main_heading2)
                    row += 1
                    for index, value in passport_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'day':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Passport Expiry Period Group By Day"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء صلاحية جواز السفر مجموعة حسب اليوم', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Passport Expiry Period Group By Day', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                days_list = []
                grand_total = 0
                day_name = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
                for index, value in driver_data_passport.iterrows():
                    if value['bsg_passport_expiry']:
                        day = value['bsg_passport_expiry'].weekday()
                        if day_name[day] not in days_list:
                            days_list.append(day_name[day])
                if days_list:
                    for day_id in days_list:
                        if day_id:
                            total = 0
                            sheet.write(row, col, 'Day', main_heading2)
                            sheet.write_string(row, col + 1, str(day_id), main_heading)
                            sheet.write(row, col + 2, 'يوم', main_heading2)
                            row += 1
                            for index, value in driver_data_passport.iterrows():
                                if value['bsg_passport_expiry']:
                                    day_val = value['bsg_passport_expiry'].weekday()
                                    if day_name[day_val] == day_id:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                passport_expiry_null = driver_data_passport.loc[(driver_data_passport['bsg_passport_expiry'] == 0)]
                if not passport_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Day', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'يوم', main_heading2)
                    row += 1
                    for index, value in passport_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'weekly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Passport Expiry Period Group By Week"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء صلاحية جواز السفر مجموعة حسب الأسبوع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Passport Expiry Period Group By Week', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                week_list = []
                grand_total = 0
                for index, value in driver_data_passport.iterrows():
                    if value['bsg_passport_expiry']:
                        year = value['bsg_passport_expiry'].year
                        week = value['bsg_passport_expiry'].strftime("%V")
                        year_week = "year %s Week %s" % (year, week)
                        if year_week not in week_list:
                            week_list.append(year_week)
                for week in week_list:
                    if week:
                        total = 0
                        sheet.write(row, col, 'Week', main_heading2)
                        sheet.write_string(row, col + 1, str(week), main_heading)
                        sheet.write(row, col + 2, 'أسبوع', main_heading2)
                        row += 1
                        for index,value in driver_data_passport.iterrows():
                            if value['bsg_passport_expiry']:
                                year_doc = value['bsg_passport_expiry'].year
                                week_doc = value['bsg_passport_expiry'].strftime("%V")
                                year_week_doc = "year %s Week %s" % (year_doc, week_doc)
                                if year_week_doc == week:
                                    if value['driver_code']:
                                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                    if value['employee_name']:
                                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                    if value['employee_join_date']:
                                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                    if value['employee_state']:
                                        if value['employee_state'] == 'on_job':
                                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                                        if value['employee_state'] == 'on_leave':
                                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                        if value['employee_state'] == 'return_from_holiday':
                                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                        if value['employee_state'] == 'resignation':
                                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                        if value['employee_state'] == 'suspended':
                                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                        if value['employee_state'] == 'service_expired':
                                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                        if value['employee_state'] == 'contract_terminated':
                                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                        if value['employee_state'] == 'ending_contract_during_trial_period':
                                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                               main_heading)
                                    if value['country_name']:
                                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                    if value['leave_start_date']:
                                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                    if value['last_return_date']:
                                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                    if value['driver_rewards']:
                                        if value['driver_rewards'] == 'by_delivery':
                                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                        if value['driver_rewards'] == 'by_delivery_b':
                                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                        if value['driver_rewards'] == 'by_revenue':
                                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                        if value['driver_rewards'] == 'not_applicable':
                                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                    if value['bsg_iqama_name']:
                                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                    if value['bsg_iqama_expiry']:
                                        days = 0
                                        delta =  value['bsg_iqama_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                        sheet.write_string(row, col + 11, str(days), main_heading)
                                    if value['bsg_nationality_name']:
                                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                           main_heading)
                                    if value['bsg_nid_expiry']:
                                        days = 0
                                        delta =  value['bsg_nid_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                        sheet.write_string(row, col + 15, str(days), main_heading)
                                    if value['bsg_passport_number']:
                                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                           main_heading)
                                    if value['bsg_passport_expiry']:
                                        days = 0
                                        delta = value['bsg_passport_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                           main_heading)
                                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                        sheet.write_string(row, col + 19, str(days), main_heading)
                                    if value['emp_licence_no']:
                                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                    if value['emp_licence_expiry']:
                                        days = 0
                                        delta = value['emp_licence_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                        sheet.write(row, col + 23, str(days), main_heading)
                                    if value['mobile_phone']:
                                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                    if value['bsg_driver']:
                                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                                    if value['taq_number']:
                                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                    if value['make_name']:
                                        sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                    if value['model_name']:
                                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                        sheet.write_string(row, col + 28, str(display_name), main_heading)
                                    if value['vehicle_status_name']:
                                        sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                           main_heading)
                                    if value['vehicle_type_name']:
                                        sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                    if value['domain_name']:
                                        sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                    if value['model_year']:
                                        sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                    if value['estmaira_serial_no']:
                                        sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                           main_heading)
                                    if value['analytic_account_name']:
                                        sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                           main_heading)
                                    row += 1
                                    total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                passport_expiry_null = driver_data_passport.loc[(driver_data_passport['bsg_passport_expiry'] == 0)]
                if not passport_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Week', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'أسبوع', main_heading2)
                    row += 1
                    for index, value in passport_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'month':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Passport Expiry Period Group By Month"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء صلاحية جواز السفر حسب الشهر', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Passport Expiry Period Group By Month', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                months_list = []
                grand_total = 0
                for index,value in driver_data_passport.iterrows():
                    if value['bsg_passport_expiry']:
                        if value['bsg_passport_expiry'].strftime('%B') not in months_list:
                            months_list.append(value['bsg_passport_expiry'].strftime('%B'))
                for month in months_list:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, str(month), main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index,value in driver_data_passport.iterrows():
                        if value['bsg_passport_expiry']:
                            if value['bsg_passport_expiry'].strftime('%B') == month:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                passport_expiry_null = driver_data_passport.loc[(driver_data_passport['bsg_passport_expiry'] == 0)]
                if not passport_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index, value in passport_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'quarterly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Passport Expiry Period Group By Quarter"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء صلاحية جواز السفر المجموعة حسب الربع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Passport Expiry Period Group By Quarter', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'National ID', main_heading2)
                sheet.write(row, col + 11, 'National Expiry date', main_heading2)
                sheet.write(row, col + 12, 'Passport Number', main_heading2)
                sheet.write(row, col + 13, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 14, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 15, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 16, ' Mobile No.', main_heading2)
                sheet.write(row, col + 17, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 18, 'Sticker No.', main_heading2)
                sheet.write(row, col + 19, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 20, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 21, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 22, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 23, 'Domain Name', main_heading2)
                sheet.write(row, col + 24, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 25, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 26, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 11, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 12, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 14, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 15, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 16, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 17, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 18, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 19, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 20, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 21, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 22, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 23, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 24, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 25, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 26, 'حساب تحليلي', main_heading2)
                row += 1
                driver_data_not_null_exp = driver_data_passport.loc[(driver_data_passport['bsg_passport_expiry']!=0)]
                driver_data_not_null_exp['passport_expiry_month'] = pd.DatetimeIndex(driver_data_not_null_exp['bsg_passport_expiry']).month
                first_quarter = [1, 2, 3]
                second_quarter = [4, 5, 6]
                third_quarter = [7, 8, 9]
                fourth_quarter = [10,11,12]
                first_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['passport_expiry_month'].isin(first_quarter))]
                second_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['passport_expiry_month'].isin(second_quarter))]
                third_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['passport_expiry_month'].isin(third_quarter))]
                fourth_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['passport_expiry_month'].isin(fourth_quarter))]
                grand_total = 0
                if not first_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'First', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in first_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not second_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Second', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in second_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not third_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Third', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in third_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not fourth_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Fourth', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in fourth_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                passport_expiry_null = driver_data_passport.loc[(driver_data_passport['bsg_passport_expiry'] == 0)]
                if not passport_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index, value in passport_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'year':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Passport Expiry Period Group By Year"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء صلاحية جواز السفر المجموعة حسب السنة', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Passport Expiry Period Group By Year', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                years_list = []
                grand_total = 0
                for index,value in driver_data_passport.iterrows():
                    if value['bsg_passport_expiry']:
                        if value['bsg_passport_expiry'].year not in years_list:
                            years_list.append(value['bsg_passport_expiry'].year)
                if years_list:
                    for year in years_list:
                        if year:
                            total = 0
                            sheet.write(row, col, 'Year', main_heading2)
                            sheet.write_string(row, col + 1, str(year), main_heading)
                            sheet.write(row, col + 2, 'عام', main_heading2)
                            row += 1
                            for index,value in driver_data_passport.iterrows():
                                if value['bsg_passport_expiry']:
                                    if value['bsg_passport_expiry'].year == year:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                passport_expiry_null = driver_data_passport.loc[(driver_data_passport['bsg_passport_expiry'] == 0)]
                if not passport_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Year', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'عام', main_heading2)
                    row += 1
                    for index, value in passport_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_licence_expiry':
            driver_data['emp_licence_expiry'] = pd.to_datetime(driver_data['emp_licence_expiry'])
            driver_data = driver_data.sort_values(by=['emp_licence_expiry', 'driver_code'])
            driver_data['emp_licence_expiry'] = pd.to_datetime(driver_data['emp_licence_expiry']).dt.date
            driver_data_licence = driver_data.fillna(0)
            if not docs.period_grouping_by:
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Licence Expiry Period Group By Date"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب مجموعة فترة انتهاء الترخيص حسب التاريخ', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Licence Expiry Period Group By Date', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                date_list=[]
                grand_total=0
                for index, value in driver_data_licence.iterrows():
                    if value['emp_licence_expiry'] not in date_list:
                        date_list.append(value['emp_licence_expiry'])
                for licence_exp_date in date_list:
                    if licence_exp_date:
                        total=0
                        sheet.write(row, col,'Date', main_heading2)
                        sheet.write_string(row, col + 1,str(licence_exp_date), main_heading)
                        sheet.write(row, col + 2, 'تاريخ', main_heading2)
                        row += 1
                        for index, value in driver_data_licence.iterrows():
                            if value['emp_licence_expiry'] == licence_exp_date:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                licence_expiry_null = driver_data_licence.loc[(driver_data_licence['emp_licence_expiry']==0)]
                if not licence_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Date', main_heading2)
                    sheet.write_string(row, col + 1,'Undefined', main_heading)
                    sheet.write(row, col + 2, 'تاريخ', main_heading2)
                    row += 1
                    for index, value in licence_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'day':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Licence Expiry Period Group By Day"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الترخيص المجموعة حسب اليوم', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Licence Expiry Period Group By Day', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                days_list = []
                grand_total = 0
                day_name = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
                for index, value in driver_data_licence.iterrows():
                    if value['emp_licence_expiry']:
                        day = value['emp_licence_expiry'].weekday()
                        if day_name[day] not in days_list:
                            days_list.append(day_name[day])
                if days_list:
                    for day_id in days_list:
                        if day_id:
                            total = 0
                            sheet.write(row, col, 'Day', main_heading2)
                            sheet.write_string(row, col + 1, str(day_id), main_heading)
                            sheet.write(row, col + 2, 'يوم', main_heading2)
                            row += 1
                            for index, value in driver_data_licence.iterrows():
                                if value['emp_licence_expiry']:
                                    day_val = value['emp_licence_expiry'].weekday()
                                    if day_name[day_val] == day_id:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                licence_expiry_null = driver_data_licence.loc[(driver_data_licence['emp_licence_expiry'] == 0)]
                if not licence_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Day', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'يوم', main_heading2)
                    row += 1
                    for index, value in licence_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'weekly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Licence Expiry Period Group By Week"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الترخيص مجموعة حسب الأسبوع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Licence Expiry Period Group By Week', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                week_list = []
                grand_total = 0
                for index, value in driver_data_licence.iterrows():
                    if value['emp_licence_expiry']:
                        year = value['emp_licence_expiry'].year
                        week = value['emp_licence_expiry'].strftime("%V")
                        year_week = "year %s Week %s" % (year, week)
                        if year_week not in week_list:
                            week_list.append(year_week)
                for week in week_list:
                    if week:
                        total = 0
                        sheet.write(row, col, 'Week', main_heading2)
                        sheet.write_string(row, col + 1, str(week), main_heading)
                        sheet.write(row, col + 2, 'أسبوع', main_heading2)
                        row += 1
                        for index,value in driver_data_licence.iterrows():
                            if value['emp_licence_expiry']:
                                year_doc = value['emp_licence_expiry'].year
                                week_doc = value['emp_licence_expiry'].strftime("%V")
                                year_week_doc = "year %s Week %s" % (year_doc, week_doc)
                                if year_week_doc == week:
                                    if value['driver_code']:
                                        sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                    if value['employee_name']:
                                        sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                    if value['employee_join_date']:
                                        sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                    if value['employee_state']:
                                        if value['employee_state'] == 'on_job':
                                            sheet.write_string(row, col + 3, 'On Job', main_heading)
                                        if value['employee_state'] == 'on_leave':
                                            sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                        if value['employee_state'] == 'return_from_holiday':
                                            sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                        if value['employee_state'] == 'resignation':
                                            sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                        if value['employee_state'] == 'suspended':
                                            sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                        if value['employee_state'] == 'service_expired':
                                            sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                        if value['employee_state'] == 'contract_terminated':
                                            sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                        if value['employee_state'] == 'ending_contract_during_trial_period':
                                            sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                               main_heading)
                                    if value['country_name']:
                                        sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                    if value['leave_start_date']:
                                        sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                    if value['last_return_date']:
                                        sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                    if value['driver_rewards']:
                                        if value['driver_rewards'] == 'by_delivery':
                                            sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                        if value['driver_rewards'] == 'by_delivery_b':
                                            sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                        if value['driver_rewards'] == 'by_revenue':
                                            sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                        if value['driver_rewards'] == 'not_applicable':
                                            sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                    if value['bsg_iqama_name']:
                                        sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                    if value['bsg_iqama_expiry']:
                                        days = 0
                                        delta =  value['bsg_iqama_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                        sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                        sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                        sheet.write_string(row, col + 11, str(days), main_heading)
                                    if value['bsg_nationality_name']:
                                        sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                           main_heading)
                                    if value['bsg_nid_expiry']:
                                        days = 0
                                        delta =  value['bsg_nid_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                        sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                        sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                        sheet.write_string(row, col + 15, str(days), main_heading)
                                    if value['bsg_passport_number']:
                                        sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                           main_heading)
                                    if value['bsg_passport_expiry']:
                                        days = 0
                                        delta = value['bsg_passport_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                        sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                           main_heading)
                                        sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                        sheet.write_string(row, col + 19, str(days), main_heading)
                                    if value['emp_licence_no']:
                                        sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                    if value['emp_licence_expiry']:
                                        days = 0
                                        delta = value['emp_licence_expiry'] - date.today()
                                        days = int(delta.days)
                                        hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                        sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                        sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                        sheet.write(row, col + 23, str(days), main_heading)
                                    if value['mobile_phone']:
                                        sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                    if value['bsg_driver']:
                                        sheet.write_string(row, col + 25, 'Yes', main_heading)
                                    if value['taq_number']:
                                        sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                    if value['make_name']:
                                        sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                    if value['model_name']:
                                        display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                        sheet.write_string(row, col + 28, str(display_name), main_heading)
                                    if value['vehicle_status_name']:
                                        sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                           main_heading)
                                    if value['vehicle_type_name']:
                                        sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                    if value['domain_name']:
                                        sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                    if value['model_year']:
                                        sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                    if value['estmaira_serial_no']:
                                        sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                           main_heading)
                                    if value['analytic_account_name']:
                                        sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                           main_heading)
                                    row += 1
                                    total += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        row += 1
                        grand_total += total
                licence_expiry_null = driver_data_licence.loc[(driver_data_licence['emp_licence_expiry'] == 0)]
                if not licence_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Week', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'أسبوع', main_heading2)
                    row += 1
                    for index, value in licence_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'month':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Licence Expiry Period Group By Month"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الترخيص المجموعة حسب الشهر', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Licence Expiry Period Group By Month', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                months_list = []
                grand_total = 0
                for index,value in driver_data_licence.iterrows():
                    if value['emp_licence_expiry']:
                        if value['emp_licence_expiry'].strftime('%B') not in months_list:
                            months_list.append(value['emp_licence_expiry'].strftime('%B'))
                for month in months_list:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, str(month), main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index,value in driver_data_licence.iterrows():
                        if value['emp_licence_expiry']:
                            if value['emp_licence_expiry'].strftime('%B') == month:
                                if value['driver_code']:
                                    sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                if value['employee_name']:
                                    sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                if value['employee_join_date']:
                                    sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                                if value['employee_state']:
                                    if value['employee_state'] == 'on_job':
                                        sheet.write_string(row, col + 3, 'On Job', main_heading)
                                    if value['employee_state'] == 'on_leave':
                                        sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                    if value['employee_state'] == 'return_from_holiday':
                                        sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                    if value['employee_state'] == 'resignation':
                                        sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                    if value['employee_state'] == 'suspended':
                                        sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                    if value['employee_state'] == 'service_expired':
                                        sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                    if value['employee_state'] == 'contract_terminated':
                                        sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                    if value['employee_state'] == 'ending_contract_during_trial_period':
                                        sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                           main_heading)
                                if value['country_name']:
                                    sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                if value['leave_start_date']:
                                    sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                                if value['last_return_date']:
                                    sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                                if value['driver_rewards']:
                                    if value['driver_rewards'] == 'by_delivery':
                                        sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                    if value['driver_rewards'] == 'by_delivery_b':
                                        sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                    if value['driver_rewards'] == 'by_revenue':
                                        sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                    if value['driver_rewards'] == 'not_applicable':
                                        sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                if value['bsg_iqama_name']:
                                    sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                if value['bsg_iqama_expiry']:
                                    days = 0
                                    delta =  value['bsg_iqama_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                    sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                                    sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                    sheet.write_string(row, col + 11, str(days), main_heading)
                                if value['bsg_nationality_name']:
                                    sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                                if value['bsg_nid_expiry']:
                                    days = 0
                                    delta =  value['bsg_nid_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                    sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                                    sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if value['bsg_passport_number']:
                                    sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                                if value['bsg_passport_expiry']:
                                    days = 0
                                    delta = value['bsg_passport_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                                    sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                                    sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                                    sheet.write_string(row, col + 19, str(days), main_heading)
                                if value['emp_licence_no']:
                                    sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                if value['emp_licence_expiry']:
                                    days = 0
                                    delta = value['emp_licence_expiry'] - date.today()
                                    days = int(delta.days)
                                    hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                                    sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                    sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                    sheet.write(row, col + 23, str(days), main_heading)
                                if value['mobile_phone']:
                                    sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                if value['bsg_driver']:
                                    sheet.write_string(row, col + 25, 'Yes', main_heading)
                                if value['taq_number']:
                                    sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                if value['make_name']:
                                    sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                if value['model_name']:
                                    display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                    sheet.write_string(row, col + 28, str(display_name), main_heading)
                                if value['vehicle_status_name']:
                                    sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                                if value['vehicle_type_name']:
                                    sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                                if value['domain_name']:
                                    sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                if value['model_year']:
                                    sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                if value['estmaira_serial_no']:
                                    sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                                if value['analytic_account_name']:
                                    sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                                row += 1
                                total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                licence_expiry_null = driver_data_licence.loc[(driver_data_licence['emp_licence_expiry'] == 0)]
                if not licence_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for index, value in licence_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'quarterly':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Licence Expiry Period Group By Quarter"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الترخيص المجموعة حسب الربع', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Licence Expiry Period Group By Quarter', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                driver_data_not_null_exp = driver_data_licence.loc[(driver_data_licence['emp_licence_expiry']!=0)]
                driver_data_not_null_exp['licence_exp_month'] = pd.DatetimeIndex(driver_data_not_null_exp['emp_licence_expiry']).month
                first_quarter = [1, 2, 3]
                second_quarter = [4, 5, 6]
                third_quarter = [7, 8, 9]
                fourth_quarter = [10,11,12]
                first_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['licence_exp_month'].isin(first_quarter))]
                second_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['licence_exp_month'].isin(second_quarter))]
                third_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['licence_exp_month'].isin(third_quarter))]
                fourth_quarter_ids = driver_data_not_null_exp.loc[(driver_data_not_null_exp['licence_exp_month'].isin(fourth_quarter))]
                grand_total = 0
                if not first_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'First', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in first_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not second_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Second', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in second_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not third_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Third', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in third_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                if not fourth_quarter_ids.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Fourth', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index,value in fourth_quarter_ids.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                licence_expiry_null = driver_data_licence.loc[(driver_data_licence['emp_licence_expiry'] == 0)]
                if not licence_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for index, value in licence_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'year':
                self.env.ref('bsg_vehicles_drivers_reports.vehicle_drivers_report_xlsx_id').report_file = "Vehicles Drivers Report Group By Licence Expiry Period Group By Year"
                sheet.merge_range('A1:Q1', 'مجموعة تقرير سائقي المركبات حسب فترة انتهاء الترخيص المجموعة حسب السنة', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicles Drivers Report Group By Licence Expiry Period Group By Year', main_heading3)
                row += 2
                sheet.write(row, col, 'Employee ID', main_heading2)
                sheet.write(row, col + 1, 'Employee Name', main_heading2)
                sheet.write(row, col + 2, 'Date of Join', main_heading2)
                sheet.write(row, col + 3, 'Emploee Status', main_heading2)
                sheet.write(row, col + 4, 'Nationality', main_heading2)
                sheet.write(row, col + 5, 'Start Leaves Date', main_heading2)
                sheet.write(row, col + 6, 'Return Leaves Date', main_heading2)
                sheet.write(row, col + 7, 'Driver Reward', main_heading2)
                sheet.write(row, col + 8, 'Iqama No.', main_heading2)
                sheet.write(row, col + 9, 'Iqama Expiry date', main_heading2)
                sheet.write(row, col + 10, 'Iqama Hijri Expiry date', main_heading2)
                sheet.write(row, col + 11, 'Remainder Iqama expiry days', main_heading2)
                sheet.write(row, col + 12, 'National ID', main_heading2)
                sheet.write(row, col + 13, 'National Expiry date', main_heading2)
                sheet.write(row, col + 14, 'National Hijri Expiry date', main_heading2)
                sheet.write(row, col + 15, 'Remainder National expiry days', main_heading2)
                sheet.write(row, col + 16, 'Passport Number', main_heading2)
                sheet.write(row, col + 17, 'Passport Expiry date', main_heading2)
                sheet.write(row, col + 18, 'Passport Hijri Expiry date', main_heading2)
                sheet.write(row, col + 19, 'Remainder Passport expiry days ', main_heading2)
                sheet.write(row, col + 20, 'Employee Licence No.', main_heading2)
                sheet.write(row, col + 21, 'Employee Licence Expiry', main_heading2)
                sheet.write(row, col + 22, 'Employee Licence Hijri Expiry Date', main_heading2)
                sheet.write(row, col + 23, 'Remainder Licence expiry days', main_heading2)
                sheet.write(row, col + 24, ' Mobile No.', main_heading2)
                sheet.write(row, col + 25, 'Linked with Vehicle', main_heading2)
                sheet.write(row, col + 26, 'Sticker No.', main_heading2)
                sheet.write(row, col + 27, 'Vehicle Make', main_heading2)
                sheet.write(row, col + 28, 'Vehicle Model', main_heading2)
                sheet.write(row, col + 29, 'Vehicle Status', main_heading2)
                sheet.write(row, col + 30, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 31, 'Domain Name', main_heading2)
                sheet.write(row, col + 32, 'Manufacturing Year', main_heading2)
                sheet.write(row, col + 33, 'Istmara Serial No.', main_heading2)
                sheet.write(row, col + 34, 'Analytic Account', main_heading2)
                row += 1
                sheet.write(row, col, 'كود الموظف', main_heading2)
                sheet.write(row, col + 1, 'اسم الموظف', main_heading2)
                sheet.write(row, col + 2, 'تاريخ التعيين', main_heading2)
                sheet.write(row, col + 3, 'حالة الموظف', main_heading2)
                sheet.write(row, col + 4, 'الجنسية', main_heading2)
                sheet.write(row, col + 5, ' تاريخ بداية الإجازة', main_heading2)
                sheet.write(row, col + 6, 'تاريخ أخر عودة من الإجازة', main_heading2)
                sheet.write(row, col + 7, 'نوع الحافز  ', main_heading2)
                sheet.write(row, col + 8, 'رقم الاقامه ', main_heading2)
                sheet.write(row, col + 9, 'تاريخ انتهاء الإقامة ', main_heading2)
                sheet.write(row, col + 10, 'تاريخ إنتهاؤ الإقامة بالهجري', main_heading2)
                sheet.write(row, col + 11, 'الأيام المتبقية لانتهاء الإقامة', main_heading2)
                sheet.write(row, col + 12, 'رقم الهوية', main_heading2)
                sheet.write(row, col + 13, 'تاريخ انتهاء الهوية', main_heading2)
                sheet.write(row, col + 14, 'تاريخ انتهاء الهوية بالهجري', main_heading2)
                sheet.write(row, col + 15, 'الأيام المتبقية لانتهاء الهوية', main_heading2)
                sheet.write(row, col + 16, 'رقم الجواز', main_heading2)
                sheet.write(row, col + 17, 'تاريخ انتهاء الجواز', main_heading2)
                sheet.write(row, col + 18, 'تاريخ انتهاء جواز السفر الهجري', main_heading2)
                sheet.write(row, col + 19, 'الأيام المتبقية لانتهاء الجواز', main_heading2)
                sheet.write(row, col + 20, 'رقم رخصة الموظف', main_heading2)
                sheet.write(row, col + 21, 'انتهاء رخصة الموظف', main_heading2)
                sheet.write(row, col + 22, 'انتهاء رخصة الموظف بالهجري', main_heading2)
                sheet.write(row, col + 23, 'الأيام المتبقية لانتهاء رخصة القيادة', main_heading2)
                sheet.write(row, col + 24, 'رقم الجوال  ', main_heading2)
                sheet.write(row, col + 25, 'مربوط بشاحنة', main_heading2)
                sheet.write(row, col + 26, 'رقم الشاحنه', main_heading2)
                sheet.write(row, col + 27, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 28, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 29, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 30, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 31, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 32, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 33, 'رقم التسلسلي للاستمارة', main_heading2)
                sheet.write(row, col + 34, 'حساب تحليلي', main_heading2)
                row += 1
                years_list = []
                grand_total = 0
                for index,value in driver_data_licence.iterrows():
                    if value['emp_licence_expiry']:
                        if value['emp_licence_expiry'].year not in years_list:
                            years_list.append(value['emp_licence_expiry'].year)
                if years_list:
                    for year in years_list:
                        if year:
                            total = 0
                            sheet.write(row, col, 'Year', main_heading2)
                            sheet.write_string(row, col + 1, str(year), main_heading)
                            sheet.write(row, col + 2, 'عام', main_heading2)
                            row += 1
                            for index,value in driver_data_licence.iterrows():
                                if value['emp_licence_expiry']:
                                    if value['emp_licence_expiry'].year == year:
                                        if value['driver_code']:
                                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                                        if value['employee_name']:
                                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                                        if value['employee_join_date']:
                                            sheet.write_string(row, col + 2, str(value['employee_join_date']),
                                                               main_heading)
                                        if value['employee_state']:
                                            if value['employee_state'] == 'on_job':
                                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                                            if value['employee_state'] == 'on_leave':
                                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                                            if value['employee_state'] == 'return_from_holiday':
                                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                                            if value['employee_state'] == 'resignation':
                                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                                            if value['employee_state'] == 'suspended':
                                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                                            if value['employee_state'] == 'service_expired':
                                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                                            if value['employee_state'] == 'contract_terminated':
                                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                                   main_heading)
                                        if value['country_name']:
                                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                                        if value['leave_start_date']:
                                            sheet.write_string(row, col + 5, str(value['leave_start_date']),
                                                               main_heading)
                                        if value['last_return_date']:
                                            sheet.write_string(row, col + 6, str(value['last_return_date']),
                                                               main_heading)
                                        if value['driver_rewards']:
                                            if value['driver_rewards'] == 'by_delivery':
                                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                                            if value['driver_rewards'] == 'by_delivery_b':
                                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                                            if value['driver_rewards'] == 'by_revenue':
                                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                                            if value['driver_rewards'] == 'not_applicable':
                                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                                        if value['bsg_iqama_name']:
                                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                                        if value['bsg_iqama_expiry']:
                                            days = 0
                                            delta =  value['bsg_iqama_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                                            sheet.write_string(row, col + 11, str(days), main_heading)
                                        if value['bsg_nationality_name']:
                                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']),
                                                               main_heading)
                                        if value['bsg_nid_expiry']:
                                            days = 0
                                            delta =  value['bsg_nid_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                                            sheet.write_string(row, col + 15, str(days), main_heading)
                                        if value['bsg_passport_number']:
                                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']),
                                                               main_heading)
                                        if value['bsg_passport_expiry']:
                                            days = 0
                                            delta = value['bsg_passport_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_passport_exp_date = HijriDate.get_hijri_date(
                                                value['bsg_passport_expiry'])
                                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']),
                                                               main_heading)
                                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date),
                                                               main_heading)
                                            sheet.write_string(row, col + 19, str(days), main_heading)
                                        if value['emp_licence_no']:
                                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                                        if value['emp_licence_expiry']:
                                            days = 0
                                            delta = value['emp_licence_expiry'] - date.today()
                                            days = int(delta.days)
                                            hijri_licence_exp_date = HijriDate.get_hijri_date(
                                                value['emp_licence_expiry'])
                                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                                            sheet.write(row, col + 23, str(days), main_heading)
                                        if value['mobile_phone']:
                                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                                        if value['bsg_driver']:
                                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                                        if value['taq_number']:
                                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                                        if value['make_name']:
                                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                                        if value['model_name']:
                                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                                        if value['vehicle_status_name']:
                                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']),
                                                               main_heading)
                                        if value['vehicle_type_name']:
                                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']),
                                                               main_heading)
                                        if value['domain_name']:
                                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                                        if value['model_year']:
                                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                                        if value['estmaira_serial_no']:
                                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']),
                                                               main_heading)
                                        if value['analytic_account_name']:
                                            sheet.write_string(row, col + 34, str(value['analytic_account_name']),
                                                               main_heading)
                                        row += 1
                                        total += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            row += 1
                            grand_total += total
                licence_expiry_null = driver_data_licence.loc[(driver_data_licence['emp_licence_expiry'] == 0)]
                if not licence_expiry_null.empty:
                    total = 0
                    sheet.write(row, col, 'Year', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'عام', main_heading2)
                    row += 1
                    for index, value in licence_expiry_null.iterrows():
                        if value['driver_code']:
                            sheet.write_string(row, col, str(value['driver_code']), main_heading)
                        if value['employee_name']:
                            sheet.write_string(row, col + 1, str(value['employee_name']), main_heading)
                        if value['employee_join_date']:
                            sheet.write_string(row, col + 2, str(value['employee_join_date']), main_heading)
                        if value['employee_state']:
                            if value['employee_state'] == 'on_job':
                                sheet.write_string(row, col + 3, 'On Job', main_heading)
                            if value['employee_state'] == 'on_leave':
                                sheet.write_string(row, col + 3, 'On Leave', main_heading)
                            if value['employee_state'] == 'return_from_holiday':
                                sheet.write_string(row, col + 3, 'Return From Holiday', main_heading)
                            if value['employee_state'] == 'resignation':
                                sheet.write_string(row, col + 3, 'Resignation', main_heading)
                            if value['employee_state'] == 'suspended':
                                sheet.write_string(row, col + 3, 'Suspended', main_heading)
                            if value['employee_state'] == 'service_expired':
                                sheet.write_string(row, col + 3, 'Service Expired', main_heading)
                            if value['employee_state'] == 'contract_terminated':
                                sheet.write_string(row, col + 3, 'Contract Terminated', main_heading)
                            if value['employee_state'] == 'ending_contract_during_trial_period':
                                sheet.write_string(row, col + 3, 'Ending Contract During Trial Period',
                                                   main_heading)
                        if value['country_name']:
                            sheet.write_string(row, col + 4, str(value['country_name']), main_heading)
                        if value['leave_start_date']:
                            sheet.write_string(row, col + 5, str(value['leave_start_date']), main_heading)
                        if value['last_return_date']:
                            sheet.write_string(row, col + 6, str(value['last_return_date']), main_heading)
                        if value['driver_rewards']:
                            if value['driver_rewards'] == 'by_delivery':
                                sheet.write_string(row, col + 7, 'By Delivery A', main_heading)
                            if value['driver_rewards'] == 'by_delivery_b':
                                sheet.write_string(row, col + 7, 'By Delivery B', main_heading)
                            if value['driver_rewards'] == 'by_revenue':
                                sheet.write_string(row, col + 7, 'By Revenue', main_heading)
                            if value['driver_rewards'] == 'not_applicable':
                                sheet.write_string(row, col + 7, 'Not Applicable', main_heading)
                        if value['bsg_iqama_name']:
                            sheet.write_string(row, col + 8, str(value['bsg_iqama_name']), main_heading)
                        if value['bsg_iqama_expiry']:
                            days = 0
                            delta =  value['bsg_iqama_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_iqama_exp_date = HijriDate.get_hijri_date(value['bsg_iqama_expiry'])
                            sheet.write_string(row, col + 9, str(value['bsg_iqama_expiry']), main_heading)
                            sheet.write_string(row, col + 10, str(hijri_iqama_exp_date), main_heading)
                            sheet.write_string(row, col + 11, str(days), main_heading)
                        if value['bsg_nationality_name']:
                            sheet.write_string(row, col + 12, str(value['bsg_nationality_name']), main_heading)
                        if value['bsg_nid_expiry']:
                            days = 0
                            delta =  value['bsg_nid_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_nid_exp_date = HijriDate.get_hijri_date(value['bsg_nid_expiry'])
                            sheet.write_string(row, col + 13, str(value['bsg_nid_expiry']), main_heading)
                            sheet.write_string(row, col + 14, str(hijri_nid_exp_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if value['bsg_passport_number']:
                            sheet.write_string(row, col + 16, str(value['bsg_passport_number']), main_heading)
                        if value['bsg_passport_expiry']:
                            days = 0
                            delta = value['bsg_passport_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_passport_exp_date = HijriDate.get_hijri_date(value['bsg_passport_expiry'])
                            sheet.write_string(row, col + 17, str(value['bsg_passport_expiry']), main_heading)
                            sheet.write_string(row, col + 18, str(hijri_passport_exp_date), main_heading)
                            sheet.write_string(row, col + 19, str(days), main_heading)
                        if value['emp_licence_no']:
                            sheet.write(row, col + 20, str(value['emp_licence_no']), main_heading)
                        if value['emp_licence_expiry']:
                            days = 0
                            delta = value['emp_licence_expiry'] - date.today()
                            days = int(delta.days)
                            hijri_licence_exp_date = HijriDate.get_hijri_date(value['emp_licence_expiry'])
                            sheet.write(row, col + 21, str(value['emp_licence_expiry']), main_heading)
                            sheet.write(row, col + 22, str(hijri_licence_exp_date), main_heading)
                            sheet.write(row, col + 23, str(days), main_heading)
                        if value['mobile_phone']:
                            sheet.write_string(row, col + 24, str(value['mobile_phone']), main_heading)
                        if value['bsg_driver']:
                            sheet.write_string(row, col + 25, 'Yes', main_heading)
                        if value['taq_number']:
                            sheet.write_string(row, col + 26, str(value['taq_number']), main_heading)
                        if value['make_name']:
                            sheet.write_string(row, col + 27, str(value['make_name']), main_heading)
                        if value['model_name']:
                            display_name = "%s / %s" % (value['model_name'], value['make_name'])
                            sheet.write_string(row, col + 28, str(display_name), main_heading)
                        if value['vehicle_status_name']:
                            sheet.write_string(row, col + 29, str(value['vehicle_status_name']), main_heading)
                        if value['vehicle_type_name']:
                            sheet.write_string(row, col + 30, str(value['vehicle_type_name']), main_heading)
                        if value['domain_name']:
                            sheet.write_string(row, col + 31, str([value['domain_name']]), main_heading)
                        if value['model_year']:
                            sheet.write_string(row, col + 32, str(value['model_year']), main_heading)
                        if value['estmaira_serial_no']:
                            sheet.write_string(row, col + 33, str(value['estmaira_serial_no']), main_heading)
                        if value['analytic_account_name']:
                            sheet.write_string(row, col + 34, str(value['analytic_account_name']), main_heading)
                        row += 1
                        total += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)