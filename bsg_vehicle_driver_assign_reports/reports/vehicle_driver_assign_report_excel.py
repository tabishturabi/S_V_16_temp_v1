from odoo import models
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd


class VehicleDriverAssignmentReportExcel(models.AbstractModel):
    _name = 'report.bsg_vehicle_driver_assign_reports.driver_assign_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        main_heading = workbook.add_format({
            "bold": 0,
            "border": 1,
            "align": 'left',
            "valign": 'vulatcenter',
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
        sheet = workbook.add_worksheet('Vehicle Driver Assignment Report')
        sheet.set_column('A:Q',15)
        row=3
        col=0


        domain=[]
        if docs.vehicle_make:
            domain += [('model_id.brand_id', 'in', docs.vehicle_make.ids)]
            sheet.write(row, col, 'Vehicle Make', main_heading2)
            rec_names = docs.vehicle_make.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.vehicle_sticker_no:
            domain += [('fleet_vehicle_id', 'in', docs.vehicle_sticker_no.ids)]
            sheet.write(row, col, 'Vehicle Sticker No', main_heading2)
            rec_names = docs.vehicle_sticker_no.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.model_year:
            year_list = []
            for year in docs.model_year:
                if year:
                    year_list.append(year.car_year_name)
            domain += [('fleet_vehicle_id.model_year','in',year_list)]
            if year_list:
                sheet.write(row, col, 'Model Year', main_heading2)
                names = '/'.join(year_list)
                sheet.write_string(row, col + 1, str(names), main_heading)
                row += 1
        if docs.vehicle_state:
            domain += [('fleet_vehicle_id.state_id', 'in', docs.vehicle_state.ids)]
            sheet.write(row, col, 'Vehicle State', main_heading2)
            rec_names = docs.vehicle_state.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.vehicle_status:
            domain += [('truck_status_id', 'in', docs.vehicle_status.ids)]
            sheet.write(row, col, 'Vehicle Status', main_heading2)
            rec_names = docs.vehicle_status.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.vehicle_type:
            domain += [('vehicle_type_id','in',docs.vehicle_type.ids)]
            sheet.write(row, col, 'Vehicle Type', main_heading2)
            rec_names = docs.vehicle_type.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.domain_name:
            domain += [('vehicle_type_id.domain_name','in',docs.domain_name.ids)]
            sheet.write(row, col, 'Domain Name', main_heading2)
            rec_names = docs.domain_name.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.assign_driver_name:
            # domain += [('assign_driver_id','in',docs.assign_driver_name.ids)]
            sheet.write(row, col, 'Assign Driver Name', main_heading2)
            rec_names = docs.assign_driver_name.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.unassign_driver_name:
            # domain += [('unassign_driver_id','in',docs.unassign_driver_name.ids)]
            sheet.write(row, col, 'Unassigned Driver', main_heading2)
            rec_names = docs.unassign_driver_name.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.maintenance_workshop:
            domain += [('maintenence_work','=',docs.maintenance_workshop)]
            sheet.write(row, col, 'Maintenance Workshop', main_heading2)
            sheet.write_string(row, col + 1, str(docs.maintenance_workshop), main_heading)
            row += 1
        if docs.vehicle_group:
            domain += [('fleet_vehicle_id.vehicle_group_name','in',docs.vehicle_group.ids)]
            sheet.write(row, col, 'Vehicle Group', main_heading2)
            rec_names = docs.vehicle_group.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.trailer_group:
            domain += [('fleet_vehicle_id.trailer_id.trailer_asset_group', 'in', docs.trailer_group.ids)]
            sheet.write(row, col, 'Trailer Group', main_heading2)
            rec_names = docs.trailer_group.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.trailer_sticker_no:
            domain += [('fleet_vehicle_id.trailer_id', 'in', docs.trailer_sticker_no.ids)]
            sheet.write(row, col, 'Trailer Sticker No', main_heading2)
            rec_names = docs.trailer_sticker_no.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.creator_user:
            domain += [('create_uid','in',docs.creator_user.ids)]
            sheet.write(row, col, 'Creator User', main_heading2)
            rec_names = docs.creator_user.mapped('display_name')
            names = '/'.join(rec_names)
            sheet.write_string(row, col + 1, str(names), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_equal_to':
            domain += [('assign_date', '=', docs.assignment_date)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is equal to'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_not_equal_to':
            domain += [('assign_date', '!=', docs.assignment_date)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is not equal to'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_after':
            domain += [('assign_date', '>', docs.assignment_date)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is after'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_before':
            domain += [('assign_date', '<', docs.assignment_date)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is before'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_after_or_equal_to':
            domain += [('assign_date', '>=', docs.assignment_date)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is after or equal to'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_before_or_equal_to':
            domain += [('assign_date', '<=', docs.assignment_date)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is before or equal to'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_between':
            domain += [('assign_date', '>', docs.date_from),
                      ('assign_date', '<', docs.date_to)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is between'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_set':
            domain += [('assign_date','!=', None)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is set'), main_heading)
            row += 1
        if docs.assignment_date_condition == 'is_not_set':
            domain += [('assign_date', '=', None)]
            sheet.write(row, col, 'Assignment Date Condition', main_heading2)
            sheet.write_string(row, col + 1, str('Is not set'), main_heading)
            row += 1
        rec_ids = self.env['driver.assign'].search(domain)
        if docs.assign_driver_name or docs.unassign_driver_name:
            rec_ids = rec_ids.filtered(lambda r:(r.assign_driver_id and r.assign_driver_id.id in docs.assign_driver_name.ids) or (r.unassign_driver_id and r.unassign_driver_id.id in docs.unassign_driver_name.ids))


        if docs.grouping_by == 'all':
            self.env.ref('bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Report"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لتسليم الشاحنات', main_heading3)
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Report', main_heading3)
            row+=1
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
            sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
            sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
            sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 28, 'أنشئ بواسطة', main_heading2)
            sheet.write(row, col + 29, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 30, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 31, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 32, 'عدم التسجيل نظام تام', main_heading2)


            row+=1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Sticker No.', main_heading2)
            sheet.write(row, col + 4, 'Maker Name', main_heading2)
            sheet.write(row, col + 5, 'Model Name', main_heading2)
            sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 21, 'Trailer Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 27, 'Comment', main_heading2)
            sheet.write(row, col + 28, 'Created by', main_heading2)
            sheet.write(row, col + 29, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 30, 'Register Date', main_heading2)
            sheet.write(row, col + 31, 'Register Reference', main_heading2)
            sheet.write(row, col + 32, 'Reason', main_heading2)
            row += 1
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.assignment_no:
                        sheet.write_string(row, col,str(rec_id.assignment_no), main_heading)
                    if rec_id.assign_date:
                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                    if rec_id.document_ref:
                        sheet.write_string(row, col + 2,str(rec_id.document_ref), main_heading)
                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number), main_heading)
                    if rec_id.model_id.brand_id.name:
                        sheet.write_string(row, col + 4,str(rec_id.model_id.brand_id.name), main_heading)
                    if rec_id.model_id.name:
                        sheet.write_string(row, col + 5,str(rec_id.model_id.name), main_heading)
                    if rec_id.model_id.display_name:
                        sheet.write_string(row, col + 6,str(rec_id.model_id.display_name), main_heading)
                    if rec_id.vehicle_type_id.vehicle_type_name:
                        sheet.write_string(row, col + 7,str(rec_id.vehicle_type_id.vehicle_type_name), main_heading)
                    if rec_id.vehicle_type_id.domain_name.name:
                        sheet.write_string(row, col + 8,str(rec_id.vehicle_type_id.domain_name.name),main_heading)
                    if rec_id.assign_driver_id.driver_code:
                        sheet.write_string(row, col + 9,str(rec_id.assign_driver_id.driver_code), main_heading)
                    if rec_id.assign_driver_id.name:
                        sheet.write_string(row, col + 10,str(rec_id.assign_driver_id.name), main_heading)
                    if rec_id.unassign_driver_id.driver_code:
                        sheet.write_string(row, col + 11,str(rec_id.unassign_driver_id.driver_code), main_heading)
                    if rec_id.unassign_driver_id.name:
                        sheet.write_string(row, col + 12,str(rec_id.unassign_driver_id.name), main_heading)
                    if rec_id.comme:
                        sheet.write_string(row, col + 13,str(rec_id.comme), main_heading)
                    if rec_id.truck_status_id.vehicle_status_name:
                        sheet.write_string(row, col + 14,str(rec_id.truck_status_id.vehicle_status_name), main_heading)
                    if rec_id.previous_trailer_no.trailer_taq_no:
                        sheet.write_string(row, col + 15,str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                    if rec_id.previous_trailer_no.trailer_er_name:
                        sheet.write_string(row, col + 16,str(rec_id.previous_trailer_no.trailer_er_name), main_heading)
                    if rec_id.previous_trailer_no.trailer_ar_name:
                        sheet.write_string(row, col + 17, str(rec_id.previous_trailer_no.trailer_ar_name), main_heading)
                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                        sheet.write_string(row, col + 18,str(rec_id.previous_trailer_no.trailer_asset_status.asset_status_name), main_heading)
                    if rec_id.pre_location_id.route_waypoint_name:
                        sheet.write_string(row, col + 19,str(rec_id.pre_location_id.route_waypoint_name), main_heading)
                    if rec_id.trailer_id.trailer_taq_no:
                        sheet.write_string(row, col + 20,str(rec_id.trailer_id.trailer_taq_no),main_heading)
                    if rec_id.trailer_names:
                        sheet.write_string(row, col + 21,str(rec_id.trailer_names), main_heading)
                    if rec_id.trailer_id.trailer_ar_name:
                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_ar_name), main_heading)
                    if rec_id.trailer_id.trailer_er_name:
                        sheet.write_string(row, col + 23,str(rec_id.trailer_id.trailer_er_name), main_heading)
                    if rec_id.new_trailer_asset_status.asset_status_name:
                        sheet.write_string(row, col + 24,str(rec_id.new_trailer_asset_status.asset_status_name), main_heading)
                    if rec_id.new_location_id.route_waypoint_name:
                        sheet.write_string(row, col + 25, str(rec_id.new_location_id.route_waypoint_name), main_heading)
                    if rec_id.maintenence_work:
                        sheet.write_string(row, col + 26,str(rec_id.maintenence_work), main_heading)
                    if rec_id.comme:
                        sheet.write_string(row, col + 27,str(rec_id.comme), main_heading)
                    if rec_id.create_uid.name:
                        sheet.write_string(row, col + 28, str(rec_id.create_uid.name), main_heading)
                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                        sheet.write_string(row, col + 29, str(rec_id.x_vehicle_type_id.vehicle_type_name), main_heading)
                    if rec_id.register=='yes':
                        if rec_id.register_date:
                            sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                        if rec_id.register_tamm:
                            sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                    if rec_id.register=='no':
                        if rec_id.description:
                            sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                    row+=1

        if docs.grouping_by == 'by_sticker_no':
            self.env.ref(
                'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Sticker No. Report"
            sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب استيكر الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Sticker No. Report', main_heading3)
            row += 2
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 9, 'أسم السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 11, 'أسم السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 13, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 15, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 17, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 18, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 20, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 23, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 24, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 26, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 27, 'أنشئ بواسطة', main_heading2)
            sheet.write(row, col + 28, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 29, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 30, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 31, 'عدم التسجيل نظام تام', main_heading2)
            row += 1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Maker Name', main_heading2)
            sheet.write(row, col + 4, 'Model Name', main_heading2)
            sheet.write(row, col + 5, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 6, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Domain Name', main_heading2)
            sheet.write(row, col + 8, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Name', main_heading2)
            sheet.write(row, col + 10, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 14, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 19, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 20, 'Trailer Name', main_heading2)
            sheet.write(row, col + 21, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 25, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 26, 'Comment', main_heading2)
            sheet.write(row, col + 27, 'Created by', main_heading2)
            sheet.write(row, col + 28, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 29, 'Register Date', main_heading2)
            sheet.write(row, col + 30, 'Register Reference', main_heading2)
            sheet.write(row, col + 31, 'Reason', main_heading2)
            row += 1
            grand_total = 0
            sticker_no_list=[]
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.fleet_vehicle_id.sudo().taq_number not in sticker_no_list:
                        sticker_no_list.append(rec_id.fleet_vehicle_id.sudo().taq_number)
            if sticker_no_list:
                for sticker_num in sticker_no_list:
                    if sticker_num:
                        filtered_rec_ids = rec_ids.filtered(lambda r : r.fleet_vehicle_id.sudo().taq_number and r.fleet_vehicle_id.sudo().taq_number == sticker_num)
                        if filtered_rec_ids:
                            total = 0
                            sheet.write(row, col, 'Sticker NO.', main_heading2)
                            sheet.write_string(row, col + 1, str(sticker_num), main_heading)
                            sheet.write(row, col + 2, 'استيكر الشاحنه', main_heading2)
                            row += 1
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 3, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 6, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 8, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 13,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 17, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 18,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 23,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 28,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                                    total+=1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
            filtered_rec_ids = rec_ids.filtered(lambda r:not r.fleet_vehicle_id.sudo().taq_number)
            if filtered_rec_ids:
                total = 0
                sheet.write(row, col, 'Sticker NO.', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'استيكر الشاحنه', main_heading2)
                row += 1
                for rec_id in filtered_rec_ids:
                    if rec_id:
                        if rec_id.assignment_no:
                            sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                        if rec_id.assign_date:
                            sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                        if rec_id.document_ref:
                            sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                        if rec_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 3, str(rec_id.model_id.brand_id.name),
                                               main_heading)
                        if rec_id.model_id.name:
                            sheet.write_string(row, col + 4, str(rec_id.model_id.name), main_heading)
                        if rec_id.model_id.display_name:
                            sheet.write_string(row, col + 5, str(rec_id.model_id.display_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 6, str(rec_id.vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.domain_name.name:
                            sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.domain_name.name),
                                               main_heading)
                        if rec_id.assign_driver_id.driver_code:
                            sheet.write_string(row, col + 8, str(rec_id.assign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.assign_driver_id.name:
                            sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.name),
                                               main_heading)
                        if rec_id.unassign_driver_id.driver_code:
                            sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.unassign_driver_id.name:
                            sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                               main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                        if rec_id.truck_status_id.vehicle_status_name:
                            sheet.write_string(row, col + 13,
                                               str(rec_id.truck_status_id.vehicle_status_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_taq_no:
                            sheet.write_string(row, col + 14,
                                               str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                        if rec_id.previous_trailer_no.trailer_er_name:
                            sheet.write_string(row, col + 15,
                                               str(rec_id.previous_trailer_no.trailer_er_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_ar_name:
                            sheet.write_string(row, col + 16,
                                               str(rec_id.previous_trailer_no.trailer_ar_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 17, str(
                                rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.pre_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 18,
                                               str(rec_id.pre_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if rec_id.trailer_names:
                            sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                        if rec_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if rec_id.new_trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 23,
                                               str(rec_id.new_trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.new_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 24,
                                               str(rec_id.new_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.maintenence_work:
                            sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                        if rec_id.create_uid.name:
                            sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                        if rec_id.x_vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 28,
                                               str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.register == 'yes':
                            if rec_id.register_date:
                                sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                            if rec_id.register_tamm:
                                sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                        if rec_id.register == 'no':
                            if rec_id.description:
                                sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_vehicle_type':
            self.env.ref(
                'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Vehicle Type Report"
            sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب نشاط الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Vehicle Type Report', main_heading3)
            row += 2
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
            sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 9, 'أسم السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 11, 'أسم السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 13, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 15, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 17, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 18, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 20, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 23, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 24, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 26, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 27, 'أنشئ بواسطة', main_heading2)
            sheet.write(row, col + 28, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 29, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 30, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 31, 'عدم التسجيل نظام تام', main_heading2)
            row += 1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Sticker No.', main_heading2)
            sheet.write(row, col + 4, 'Maker Name', main_heading2)
            sheet.write(row, col + 5, 'Model Name', main_heading2)
            sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Domain Name', main_heading2)
            sheet.write(row, col + 8, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Name', main_heading2)
            sheet.write(row, col + 10, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 14, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 19, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 20, 'Trailer Name', main_heading2)
            sheet.write(row, col + 21, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 25, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 26, 'Comment', main_heading2)
            sheet.write(row, col + 27, 'Created by', main_heading2)
            sheet.write(row, col + 28, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 29, 'Register Date', main_heading2)
            sheet.write(row, col + 30, 'Register Reference', main_heading2)
            sheet.write(row, col + 31, 'Reason', main_heading2)
            row += 1
            grand_total = 0
            vehicle_type_list = []
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.vehicle_type_id.vehicle_type_name not in vehicle_type_list:
                        vehicle_type_list.append(rec_id.vehicle_type_id.vehicle_type_name)
            if vehicle_type_list:
                for vehicle_type in vehicle_type_list:
                    if vehicle_type:
                        filtered_rec_ids = rec_ids.filtered(
                            lambda r: r.vehicle_type_id.vehicle_type_name and r.vehicle_type_id.vehicle_type_name == vehicle_type)
                        if filtered_rec_ids:
                            total = 0
                            sheet.write(row, col, 'Vehicle Type', main_heading2)
                            sheet.write_string(row, col + 1, str(vehicle_type), main_heading)
                            sheet.write(row, col + 2, 'نشاط الشاحنة', main_heading2)
                            row += 1
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 8, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 13,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 17, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 18,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 23,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 28,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
            filtered_rec_ids = rec_ids.filtered(lambda r:not r.vehicle_type_id.vehicle_type_name)
            if filtered_rec_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Type', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'نشاط الشاحنة', main_heading2)
                row += 1
                for rec_id in filtered_rec_ids:
                    if rec_id:
                        if rec_id.assignment_no:
                            sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                        if rec_id.assign_date:
                            sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                        if rec_id.document_ref:
                            sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                        if rec_id.fleet_vehicle_id.sudo().taq_number:
                            sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                               main_heading)
                        if rec_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                               main_heading)
                        if rec_id.model_id.name:
                            sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                        if rec_id.model_id.display_name:
                            sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.domain_name.name:
                            sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.domain_name.name),
                                               main_heading)
                        if rec_id.assign_driver_id.driver_code:
                            sheet.write_string(row, col + 8, str(rec_id.assign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.assign_driver_id.name:
                            sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.name),
                                               main_heading)
                        if rec_id.unassign_driver_id.driver_code:
                            sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.unassign_driver_id.name:
                            sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                               main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                        if rec_id.truck_status_id.vehicle_status_name:
                            sheet.write_string(row, col + 13,
                                               str(rec_id.truck_status_id.vehicle_status_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_taq_no:
                            sheet.write_string(row, col + 14,
                                               str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                        if rec_id.previous_trailer_no.trailer_er_name:
                            sheet.write_string(row, col + 15,
                                               str(rec_id.previous_trailer_no.trailer_er_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_ar_name:
                            sheet.write_string(row, col + 16,
                                               str(rec_id.previous_trailer_no.trailer_ar_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 17, str(
                                rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.pre_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 18,
                                               str(rec_id.pre_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if rec_id.trailer_names:
                            sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                        if rec_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if rec_id.new_trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 23,
                                               str(rec_id.new_trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.new_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 24,
                                               str(rec_id.new_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.maintenence_work:
                            sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                        if rec_id.create_uid.name:
                            sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                        if rec_id.x_vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 28,
                                               str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.register == 'yes':
                            if rec_id.register_date:
                                sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                            if rec_id.register_tamm:
                                sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                        if rec_id.register == 'no':
                            if rec_id.description:
                                sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_domain_name':
            self.env.ref(
                'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Domain Name Report"
            sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب قطاع الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Domain Name Report', main_heading3)
            row += 2
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
            sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 9, 'أسم السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 11, 'أسم السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 13, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 15, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 17, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 18, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 20, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 23, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 24, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 26, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 27, 'أنشئ بواسطة', main_heading2)
            sheet.write(row, col + 28, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 29, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 30, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 31, 'عدم التسجيل نظام تام', main_heading2)
            row += 1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Sticker No.', main_heading2)
            sheet.write(row, col + 4, 'Maker Name', main_heading2)
            sheet.write(row, col + 5, 'Model Name', main_heading2)
            sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Name', main_heading2)
            sheet.write(row, col + 10, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 14, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 19, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 20, 'Trailer Name', main_heading2)
            sheet.write(row, col + 21, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 25, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 26, 'Comment', main_heading2)
            sheet.write(row, col + 27, 'Created by', main_heading2)
            sheet.write(row, col + 28, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 29, 'Register Date', main_heading2)
            sheet.write(row, col + 30, 'Register Reference', main_heading2)
            sheet.write(row, col + 31, 'Reason', main_heading2)
            row += 1
            grand_total = 0
            vehicle_type_domain_list = []
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.vehicle_type_id.domain_name.name not in vehicle_type_domain_list:
                        vehicle_type_domain_list.append(rec_id.vehicle_type_id.domain_name.name)
            if vehicle_type_domain_list:
                for vehicle_type_domain in vehicle_type_domain_list:
                    if vehicle_type_domain:
                        filtered_rec_ids = rec_ids.filtered(
                            lambda r: r.vehicle_type_id.domain_name.name and r.vehicle_type_id.domain_name.name == vehicle_type_domain)
                        if filtered_rec_ids:
                            total = 0
                            sheet.write(row, col, 'Vehicle Type Domain', main_heading2)
                            sheet.write_string(row, col + 1, str(vehicle_type_domain), main_heading)
                            sheet.write(row, col + 2, 'قطاع الشاحنة', main_heading2)
                            row += 1
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 8, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 13,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 17, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 18,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 23,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 28,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
            filtered_rec_ids = rec_ids.filtered(lambda r:not r.vehicle_type_id.domain_name.name)
            if filtered_rec_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Type Domain', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'قطاع الشاحنة', main_heading2)
                row += 1
                for rec_id in filtered_rec_ids:
                    if rec_id:
                        if rec_id.assignment_no:
                            sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                        if rec_id.assign_date:
                            sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                        if rec_id.document_ref:
                            sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                        if rec_id.fleet_vehicle_id.sudo().taq_number:
                            sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                               main_heading)
                        if rec_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                               main_heading)
                        if rec_id.model_id.name:
                            sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                        if rec_id.model_id.display_name:
                            sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.assign_driver_id.driver_code:
                            sheet.write_string(row, col + 8, str(rec_id.assign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.assign_driver_id.name:
                            sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.name),
                                               main_heading)
                        if rec_id.unassign_driver_id.driver_code:
                            sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.unassign_driver_id.name:
                            sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                               main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                        if rec_id.truck_status_id.vehicle_status_name:
                            sheet.write_string(row, col + 13,
                                               str(rec_id.truck_status_id.vehicle_status_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_taq_no:
                            sheet.write_string(row, col + 14,
                                               str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                        if rec_id.previous_trailer_no.trailer_er_name:
                            sheet.write_string(row, col + 15,
                                               str(rec_id.previous_trailer_no.trailer_er_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_ar_name:
                            sheet.write_string(row, col + 16,
                                               str(rec_id.previous_trailer_no.trailer_ar_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 17, str(
                                rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.pre_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 18,
                                               str(rec_id.pre_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if rec_id.trailer_names:
                            sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                        if rec_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if rec_id.new_trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 23,
                                               str(rec_id.new_trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.new_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 24,
                                               str(rec_id.new_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.maintenence_work:
                            sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                        if rec_id.create_uid.name:
                            sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                        if rec_id.x_vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 28,
                                               str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.register == 'yes':
                            if rec_id.register_date:
                                sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                            if rec_id.register_tamm:
                                sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                        if rec_id.register == 'no':
                            if rec_id.description:
                                sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_trailer_no':
            self.env.ref(
                'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Trailer No. Report"
            sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب استيكر المقطورة المسلم', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Trailer No. Report', main_heading3)
            row += 2
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
            sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
            sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
            sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 28, 'أنشئ بواسطة', main_heading2)
            sheet.write(row, col + 29, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 30, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 31, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 32, 'عدم التسجيل نظام تام', main_heading2)
            row += 1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Sticker No.', main_heading2)
            sheet.write(row, col + 4, 'Maker Name', main_heading2)
            sheet.write(row, col + 5, 'Model Name', main_heading2)
            sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 21, 'Trailer Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 27, 'Comment', main_heading2)
            sheet.write(row, col + 28, 'Created by', main_heading2)
            sheet.write(row, col + 29, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 30, 'Register Date', main_heading2)
            sheet.write(row, col + 31, 'Register Reference', main_heading2)
            sheet.write(row, col + 32, 'Reason', main_heading2)
            row += 1
            grand_total = 0
            trailer_no_list = []
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.fleet_vehicle_id.trailer_id.trailer_taq_no not in trailer_no_list:
                        trailer_no_list.append(rec_id.fleet_vehicle_id.trailer_id.trailer_taq_no)
            if trailer_no_list:
                for trailer_no in trailer_no_list:
                    if trailer_no:
                        filtered_rec_ids = rec_ids.filtered(
                            lambda r:r.fleet_vehicle_id.trailer_id.trailer_taq_no and r.fleet_vehicle_id.trailer_id.trailer_taq_no == trailer_no)
                        if filtered_rec_ids:
                            total = 0
                            sheet.write(row, col, 'Trailer NO.', main_heading2)
                            sheet.write_string(row, col + 1, str(trailer_no), main_heading)
                            sheet.write(row, col + 2, 'رقم المقطورة', main_heading2)
                            row += 1
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 17,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 18, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 19,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 23, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 25,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 26, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 28, str(rec_id.create_uid.name), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 29,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
            filtered_rec_ids = rec_ids.filtered(lambda r:not r.fleet_vehicle_id.trailer_id.trailer_taq_no)
            if filtered_rec_ids:
                total = 0
                sheet.write(row, col, 'Trailer NO.', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'رقم المقطورة', main_heading2)
                row += 1
                for rec_id in filtered_rec_ids:
                    if rec_id:
                        if rec_id.assignment_no:
                            sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                        if rec_id.assign_date:
                            sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                        if rec_id.document_ref:
                            sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                        if rec_id.fleet_vehicle_id.sudo().taq_number:
                            sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                               main_heading)
                        if rec_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                               main_heading)
                        if rec_id.model_id.name:
                            sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                        if rec_id.model_id.display_name:
                            sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.domain_name.name:
                            sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                               main_heading)
                        if rec_id.assign_driver_id.driver_code:
                            sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.assign_driver_id.name:
                            sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                               main_heading)
                        if rec_id.unassign_driver_id.driver_code:
                            sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.unassign_driver_id.name:
                            sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                               main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                        if rec_id.truck_status_id.vehicle_status_name:
                            sheet.write_string(row, col + 14,
                                               str(rec_id.truck_status_id.vehicle_status_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_taq_no:
                            sheet.write_string(row, col + 15,
                                               str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                        if rec_id.previous_trailer_no.trailer_er_name:
                            sheet.write_string(row, col + 16,
                                               str(rec_id.previous_trailer_no.trailer_er_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_ar_name:
                            sheet.write_string(row, col + 17,
                                               str(rec_id.previous_trailer_no.trailer_ar_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 18, str(
                                rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.pre_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 19,
                                               str(rec_id.pre_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if rec_id.trailer_names:
                            sheet.write_string(row, col + 21, str(rec_id.trailer_names), main_heading)
                        if rec_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 23, str(rec_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if rec_id.new_trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 24,
                                               str(rec_id.new_trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.new_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 25,
                                               str(rec_id.new_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.maintenence_work:
                            sheet.write_string(row, col + 26, str(rec_id.maintenence_work), main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                        if rec_id.create_uid.name:
                            sheet.write_string(row, col + 28, str(rec_id.create_uid.name), main_heading)
                        if rec_id.x_vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 29,
                                               str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.register == 'yes':
                            if rec_id.register_date:
                                sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                            if rec_id.register_tamm:
                                sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                        if rec_id.register == 'no':
                            if rec_id.description:
                                sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_assign_driver':
            self.env.ref(
                'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Assign Driver Report"
            sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب السائق المستلم', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Assign Driver Report', main_heading3)
            row += 2
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
            sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 11, 'أسم السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 13, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 15, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 17, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 18, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 20, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 23, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 24, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 26, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 27, 'أنشئ بواسطة', main_heading2)
            sheet.write(row, col + 28, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 29, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 30, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 31, 'عدم التسجيل نظام تام', main_heading2)
            row += 1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Sticker No.', main_heading2)
            sheet.write(row, col + 4, 'Maker Name', main_heading2)
            sheet.write(row, col + 5, 'Model Name', main_heading2)
            sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 10, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 14, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 19, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 20, 'Trailer Name', main_heading2)
            sheet.write(row, col + 21, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 25, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 26, 'Comment', main_heading2)
            sheet.write(row, col + 27, 'Created by', main_heading2)
            sheet.write(row, col + 28, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 29, 'Register Date', main_heading2)
            sheet.write(row, col + 30, 'Register Reference', main_heading2)
            sheet.write(row, col + 31, 'Reason', main_heading2)
            row += 1
            assign_driver_list = []
            grand_total = 0
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.assign_driver_id.name not in assign_driver_list:
                        assign_driver_list.append(rec_id.assign_driver_id.name)
            if assign_driver_list:
                for assign_driver in assign_driver_list:
                    if assign_driver:
                        filtered_rec_ids = rec_ids.filtered(
                            lambda r : r.assign_driver_id.name and r.assign_driver_id.name == assign_driver)
                        if filtered_rec_ids:
                            total = 0
                            sheet.write(row, col, 'Assignment Driver', main_heading2)
                            sheet.write_string(row, col + 1, str(assign_driver), main_heading)
                            sheet.write(row, col + 2, 'السائق المستلم', main_heading2)
                            row += 1
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 13,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 17, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 18,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 23,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 28,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
            filtered_rec_ids = rec_ids.filtered(
                lambda r:not r.assign_driver_id.name)
            if filtered_rec_ids:
                total = 0
                sheet.write(row, col, 'Assignment Driver', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'السائق المستلم', main_heading2)
                row += 1
                for rec_id in filtered_rec_ids:
                    if rec_id:
                        if rec_id.assignment_no:
                            sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                        if rec_id.assign_date:
                            sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                        if rec_id.document_ref:
                            sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                        if rec_id.fleet_vehicle_id.sudo().taq_number:
                            sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                               main_heading)
                        if rec_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                               main_heading)
                        if rec_id.model_id.name:
                            sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                        if rec_id.model_id.display_name:
                            sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.domain_name.name:
                            sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                               main_heading)
                        if rec_id.assign_driver_id.driver_code:
                            sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.unassign_driver_id.driver_code:
                            sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.unassign_driver_id.name:
                            sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                               main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                        if rec_id.truck_status_id.vehicle_status_name:
                            sheet.write_string(row, col + 13,
                                               str(rec_id.truck_status_id.vehicle_status_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_taq_no:
                            sheet.write_string(row, col + 14,
                                               str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                        if rec_id.previous_trailer_no.trailer_er_name:
                            sheet.write_string(row, col + 15,
                                               str(rec_id.previous_trailer_no.trailer_er_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_ar_name:
                            sheet.write_string(row, col + 16,
                                               str(rec_id.previous_trailer_no.trailer_ar_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 17, str(
                                rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.pre_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 18,
                                               str(rec_id.pre_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if rec_id.trailer_names:
                            sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                        if rec_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if rec_id.new_trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 23,
                                               str(rec_id.new_trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.new_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 24,
                                               str(rec_id.new_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.maintenence_work:
                            sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                        if rec_id.create_uid.name:
                            sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                        if rec_id.x_vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 28,
                                               str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.register == 'yes':
                            if rec_id.register_date:
                                sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                            if rec_id.register_tamm:
                                sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                        if rec_id.register == 'no':
                            if rec_id.description:
                                sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_unassign_driver':
            self.env.ref(
                'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Unassign Driver Report"
            sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب السائق المسلم', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Unassign Driver Report', main_heading3)
            row += 2
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
            sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
            sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 13, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 15, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 17, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 18, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 20, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 23, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 24, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 26, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 27, 'أنشئ بواسطة', main_heading2)
            sheet.write(row, col + 28, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 29, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 30, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 31, 'عدم التسجيل نظام تام', main_heading2)
            row += 1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Sticker No.', main_heading2)
            sheet.write(row, col + 4, 'Maker Name', main_heading2)
            sheet.write(row, col + 5, 'Model Name', main_heading2)
            sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 14, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 19, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 20, 'Trailer Name', main_heading2)
            sheet.write(row, col + 21, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 25, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 26, 'Comment', main_heading2)
            sheet.write(row, col + 27, 'Created by', main_heading2)
            sheet.write(row, col + 28, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 29, 'Register Date', main_heading2)
            sheet.write(row, col + 30, 'Register Reference', main_heading2)
            sheet.write(row, col + 31, 'Reason', main_heading2)
            row += 1
            grand_total = 0
            unassign_driver_list = []
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.unassign_driver_id.name not in unassign_driver_list:
                        unassign_driver_list.append(rec_id.unassign_driver_id.name)
            if unassign_driver_list:
                for unassign_driver in unassign_driver_list:
                    if unassign_driver:
                        filtered_rec_ids = rec_ids.filtered(
                            lambda r: r.unassign_driver_id.name and r.unassign_driver_id.name == unassign_driver)
                        if filtered_rec_ids:
                            total = 0
                            sheet.write(row, col, 'Unassignment Driver', main_heading2)
                            sheet.write_string(row, col + 1, str(unassign_driver), main_heading)
                            sheet.write(row, col + 2, 'السائق المسلم', main_heading2)
                            row += 1
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 13,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 17, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 18,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 23,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 28,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
            filtered_rec_ids = rec_ids.filtered(
                lambda r:not r.unassign_driver_id.name)
            if filtered_rec_ids:
                total = 0
                sheet.write(row, col, 'Unassignment Driver', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'السائق المسلم', main_heading2)
                row += 1
                for rec_id in filtered_rec_ids:
                    if rec_id:
                        if rec_id.assignment_no:
                            sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                        if rec_id.assign_date:
                            sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                        if rec_id.document_ref:
                            sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                        if rec_id.fleet_vehicle_id.sudo().taq_number:
                            sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                               main_heading)
                        if rec_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                               main_heading)
                        if rec_id.model_id.name:
                            sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                        if rec_id.model_id.display_name:
                            sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.vehicle_type_id.domain_name.name:
                            sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                               main_heading)
                        if rec_id.assign_driver_id.driver_code:
                            sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.assign_driver_id.name:
                            sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                               main_heading)
                        if rec_id.unassign_driver_id.driver_code:
                            sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                               main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                        if rec_id.truck_status_id.vehicle_status_name:
                            sheet.write_string(row, col + 13,
                                               str(rec_id.truck_status_id.vehicle_status_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_taq_no:
                            sheet.write_string(row, col + 14,
                                               str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                        if rec_id.previous_trailer_no.trailer_er_name:
                            sheet.write_string(row, col + 15,
                                               str(rec_id.previous_trailer_no.trailer_er_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_ar_name:
                            sheet.write_string(row, col + 16,
                                               str(rec_id.previous_trailer_no.trailer_ar_name),
                                               main_heading)
                        if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 17, str(
                                rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.pre_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 18,
                                               str(rec_id.pre_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if rec_id.trailer_names:
                            sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                        if rec_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if rec_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if rec_id.new_trailer_asset_status.asset_status_name:
                            sheet.write_string(row, col + 23,
                                               str(rec_id.new_trailer_asset_status.asset_status_name),
                                               main_heading)
                        if rec_id.new_location_id.route_waypoint_name:
                            sheet.write_string(row, col + 24,
                                               str(rec_id.new_location_id.route_waypoint_name),
                                               main_heading)
                        if rec_id.maintenence_work:
                            sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                        if rec_id.comme:
                            sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                        if rec_id.create_uid.name:
                            sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                        if rec_id.x_vehicle_type_id.vehicle_type_name:
                            sheet.write_string(row, col + 28,
                                               str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                               main_heading)
                        if rec_id.register == 'yes':
                            if rec_id.register_date:
                                sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                            if rec_id.register_tamm:
                                sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                        if rec_id.register == 'no':
                            if rec_id.description:
                                sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'created_by':
            self.env.ref(
                'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Report Group By Creator"
            sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب أنشئ بواسطة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Create User Report', main_heading3)
            row += 2
            sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
            sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
            sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
            sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
            sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
            sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
            sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
            sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
            sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
            sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
            sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
            sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
            sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
            sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
            sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
            sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
            sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
            sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
            sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
            sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
            sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
            sheet.write(row, col + 28, 'نوع النشاط الحالي', main_heading2)
            sheet.write(row, col + 29, 'تاريخ التسجيل', main_heading2)
            sheet.write(row, col + 30, 'مرجع التسجيل', main_heading2)
            sheet.write(row, col + 31, 'عدم التسجيل نظام تام', main_heading2)
            row += 1
            sheet.write(row, col, 'Assignment No.', main_heading2)
            sheet.write(row, col + 1, 'Assignment Date', main_heading2)
            sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
            sheet.write(row, col + 3, 'Sticker No.', main_heading2)
            sheet.write(row, col + 4, 'Maker Name', main_heading2)
            sheet.write(row, col + 5, 'Model Name', main_heading2)
            sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
            sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
            sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
            sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
            sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
            sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
            sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
            sheet.write(row, col + 21, 'Trailer Name', main_heading2)
            sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
            sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
            sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
            sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
            sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
            sheet.write(row, col + 27, 'Comment', main_heading2)
            sheet.write(row, col + 28, 'New Vehicle Type', main_heading2)
            sheet.write(row, col + 29, 'Register Date', main_heading2)
            sheet.write(row, col + 30, 'Register Reference', main_heading2)
            sheet.write(row, col + 31, 'Reason', main_heading2)
            row += 1
            grand_total = 0
            created_by_list = []
            for rec_id in rec_ids:
                if rec_id:
                    if rec_id.create_uid.name not in created_by_list:
                        created_by_list.append(rec_id.create_uid.name)
            if created_by_list:
                for creator_id in created_by_list:
                    if creator_id:
                        filtered_rec_ids = rec_ids.filtered(
                            lambda r: r.create_uid.name and r.create_uid.name == creator_id)
                        if filtered_rec_ids:
                            total = 0
                            sheet.write(row, col, 'Created By', main_heading2)
                            sheet.write_string(row, col + 1, str(creator_id), main_heading)
                            sheet.write(row, col + 2, 'أنشئ بواسطة', main_heading2)
                            row += 1
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 17,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 18, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 19,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 23, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 25,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 26, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 28,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_assignment_date':
            rec_ids_with_no_assign = rec_ids.filtered(lambda r: not r.assign_date)
            if not docs.period_grouping_by:
                self.env.ref(
                    'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Assignment Date Report"
                sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب تاريخ التسليم ', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Assignment Date Report', main_heading3)
                row += 2
                sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 1, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 2, 'استيكر الشاحنه ', main_heading2)
                sheet.write(row, col + 3, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 4, 'موديل الشاحنة', main_heading2)
                sheet.write(row, col + 5, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 6, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 7, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 8, 'كود السائق المستلم', main_heading2)
                sheet.write(row, col + 9, 'أسم السائق المستلم', main_heading2)
                sheet.write(row, col + 10, 'كود السائق المسلم', main_heading2)
                sheet.write(row, col + 11, 'أسم السائق المسلم', main_heading2)
                sheet.write(row, col + 12, 'ملاحظات الشاحنة', main_heading2)
                sheet.write(row, col + 13, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 14, 'استيكر المقطورة المستلم', main_heading2)
                sheet.write(row, col + 15, 'اسم المقطورة المستلم', main_heading2)
                sheet.write(row, col + 16, 'اسم المقطورة المستلم بالعربي', main_heading2)
                sheet.write(row, col + 17, 'حالة المقطورة المستلم', main_heading2)
                sheet.write(row, col + 18, 'الموقع الحالي للمقطورة المستلم', main_heading2)
                sheet.write(row, col + 19, 'رقم استيكر المقطورة المسلم', main_heading2)
                sheet.write(row, col + 20, 'اسم المقطورة المسلم', main_heading2)
                sheet.write(row, col + 21, 'اسم المقطورة المسلم بالعربي', main_heading2)
                sheet.write(row, col + 22, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
                sheet.write(row, col + 23, 'حالة المقطورة المسلم', main_heading2)
                sheet.write(row, col + 24, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
                sheet.write(row, col + 25, 'في ورشة الصيانة', main_heading2)
                sheet.write(row, col + 26, 'ملاحظات المقطورة', main_heading2)
                sheet.write(row, col + 27, 'أنشئ بواسطة', main_heading2)
                sheet.write(row, col + 28, 'نوع النشاط الحالي', main_heading2)
                sheet.write(row, col + 29, 'تاريخ التسجيل', main_heading2)
                sheet.write(row, col + 30, 'مرجع التسجيل', main_heading2)
                sheet.write(row, col + 31, 'عدم التسجيل نظام تام', main_heading2)
                row += 1
                sheet.write(row, col, 'Assignment No.', main_heading2)
                sheet.write(row, col + 1, 'UnAssignment No.', main_heading2)
                sheet.write(row, col + 2, 'Sticker No.', main_heading2)
                sheet.write(row, col + 3, 'Maker Name', main_heading2)
                sheet.write(row, col + 4, 'Model Name', main_heading2)
                sheet.write(row, col + 5, 'Truck/Model/Display Name', main_heading2)
                sheet.write(row, col + 6, 'Vehicle Type Name', main_heading2)
                sheet.write(row, col + 7, 'Vehicle Domain Name', main_heading2)
                sheet.write(row, col + 8, 'Assignment Driver Code', main_heading2)
                sheet.write(row, col + 9, 'Assignment Driver Name', main_heading2)
                sheet.write(row, col + 10, 'Unassignment Driver Code', main_heading2)
                sheet.write(row, col + 11, 'Unassignment Driver Name', main_heading2)
                sheet.write(row, col + 12, 'Vehicle Comment', main_heading2)
                sheet.write(row, col + 13, 'Vehicle Status Name', main_heading2)
                sheet.write(row, col + 14, 'Previous Trailer Sticker No.', main_heading2)
                sheet.write(row, col + 15, 'Previous Trailer Name', main_heading2)
                sheet.write(row, col + 16, 'Previous Trailer Ar Name', main_heading2)
                sheet.write(row, col + 17, 'Previous Trailer Status Name', main_heading2)
                sheet.write(row, col + 18, 'Previous Trailer Location Name', main_heading2)
                sheet.write(row, col + 19, 'New Trailer Linking Sticker No', main_heading2)
                sheet.write(row, col + 20, 'Trailer Name', main_heading2)
                sheet.write(row, col + 21, 'New Trailer Linking Ar Name', main_heading2)
                sheet.write(row, col + 22, 'New Trailer Linking En Name', main_heading2)
                sheet.write(row, col + 23, 'New Trailer Status Name', main_heading2)
                sheet.write(row, col + 24, 'New Trailer Location Name', main_heading2)
                sheet.write(row, col + 25, 'Maintenance Workshop', main_heading2)
                sheet.write(row, col + 26, 'Comment', main_heading2)
                sheet.write(row, col + 27, 'Created by', main_heading2)
                sheet.write(row, col + 28, 'New Vehicle Type', main_heading2)
                sheet.write(row, col + 29, 'Register Date', main_heading2)
                sheet.write(row, col + 30, 'Register Reference', main_heading2)
                sheet.write(row, col + 31, 'Reason', main_heading2)
                row += 1
                date_list = []
                grand_total = 0
                for rec_id in rec_ids:
                    if rec_id:
                        if rec_id.assign_date not in date_list:
                            date_list.append(rec_id.assign_date)
                for date_id in date_list:
                    if date_id:
                        total = 0
                        sheet.write(row, col, 'Date', main_heading2)
                        sheet.write_string(row, col + 1, str(date_id), main_heading)
                        sheet.write(row, col + 2, 'تاريخ', main_heading2)
                        row += 1
                        filtered_rec_ids = rec_ids.filtered(
                            lambda r: r.assign_date and r.assign_date == date_id)
                        for rec_id in filtered_rec_ids:
                            if rec_id:
                                if rec_id.assignment_no:
                                    sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                if rec_id.document_ref:
                                    sheet.write_string(row, col + 1, str(rec_id.document_ref), main_heading)
                                if rec_id.fleet_vehicle_id.sudo().taq_number:
                                    sheet.write_string(row, col + 2, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                       main_heading)
                                if rec_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 3, str(rec_id.model_id.brand_id.name),
                                                       main_heading)
                                if rec_id.model_id.name:
                                    sheet.write_string(row, col + 4, str(rec_id.model_id.name), main_heading)
                                if rec_id.model_id.display_name:
                                    sheet.write_string(row, col + 5, str(rec_id.model_id.display_name),
                                                       main_heading)
                                if rec_id.vehicle_type_id.vehicle_type_name:
                                    sheet.write_string(row, col + 6, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                       main_heading)
                                if rec_id.vehicle_type_id.domain_name.name:
                                    sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.domain_name.name),
                                                       main_heading)
                                if rec_id.assign_driver_id.driver_code:
                                    sheet.write_string(row, col + 8, str(rec_id.assign_driver_id.driver_code),
                                                       main_heading)
                                if rec_id.assign_driver_id.name:
                                    sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.name),
                                                       main_heading)
                                if rec_id.unassign_driver_id.driver_code:
                                    sheet.write_string(row, col + 10, str(rec_id.unassign_driver_id.driver_code),
                                                       main_heading)
                                if rec_id.unassign_driver_id.name:
                                    sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.name),
                                                       main_heading)
                                if rec_id.comme:
                                    sheet.write_string(row, col + 12, str(rec_id.comme), main_heading)
                                if rec_id.truck_status_id.vehicle_status_name:
                                    sheet.write_string(row, col + 13,
                                                       str(rec_id.truck_status_id.vehicle_status_name),
                                                       main_heading)
                                if rec_id.previous_trailer_no.trailer_taq_no:
                                    sheet.write_string(row, col + 14,
                                                       str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                if rec_id.previous_trailer_no.trailer_er_name:
                                    sheet.write_string(row, col + 15,
                                                       str(rec_id.previous_trailer_no.trailer_er_name),
                                                       main_heading)
                                if rec_id.previous_trailer_no.trailer_ar_name:
                                    sheet.write_string(row, col + 16,
                                                       str(rec_id.previous_trailer_no.trailer_ar_name),
                                                       main_heading)
                                if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                    sheet.write_string(row, col + 17, str(
                                        rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                       main_heading)
                                if rec_id.pre_location_id.route_waypoint_name:
                                    sheet.write_string(row, col + 18,
                                                       str(rec_id.pre_location_id.route_waypoint_name),
                                                       main_heading)
                                if rec_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 19, str(rec_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if rec_id.trailer_names:
                                    sheet.write_string(row, col + 20, str(rec_id.trailer_names), main_heading)
                                if rec_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 21, str(rec_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if rec_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if rec_id.new_trailer_asset_status.asset_status_name:
                                    sheet.write_string(row, col + 23,
                                                       str(rec_id.new_trailer_asset_status.asset_status_name),
                                                       main_heading)
                                if rec_id.new_location_id.route_waypoint_name:
                                    sheet.write_string(row, col + 24,
                                                       str(rec_id.new_location_id.route_waypoint_name),
                                                       main_heading)
                                if rec_id.maintenence_work:
                                    sheet.write_string(row, col + 25, str(rec_id.maintenence_work), main_heading)
                                if rec_id.comme:
                                    sheet.write_string(row, col + 26, str(rec_id.comme), main_heading)
                                if rec_id.create_uid.name:
                                    sheet.write_string(row, col + 27, str(rec_id.create_uid.name), main_heading)
                                if rec_id.x_vehicle_type_id.vehicle_type_name:
                                    sheet.write_string(row, col + 28,
                                                       str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                       main_heading)
                                if rec_id.register == 'yes':
                                    if rec_id.register_date:
                                        sheet.write_string(row, col + 29, str(rec_id.register_date), main_heading)
                                    if rec_id.register_tamm:
                                        sheet.write_string(row, col + 30, str(rec_id.register_tamm), main_heading)
                                if rec_id.register == 'no':
                                    if rec_id.description:
                                        sheet.write_string(row, col + 31, str(rec_id.description), main_heading)
                                total += 1
                                row += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        grand_total += total
                        row += 1
                if rec_ids_with_no_assign:
                    total = 0
                    sheet.write(row, col, 'Date', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'تاريخ', main_heading2)
                    row += 1
                    for rec_id in rec_ids_with_no_assign:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names), main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23, str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work), main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name), main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'day':
                self.env.ref(
                    'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Assignment Date ( Day/) Report"
                sheet.merge_range('A1:Q1', 'تقرير تسليم شاحنة تجميع بحسب تاريخ التسليم اليوم/', main_heading3)
                row += 1
                sheet.merge_range('A2:Q2', 'Vehicle Driver Assignment Group by Assignment Date ( Day/) Report', main_heading3)
                row += 2
                sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
                sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
                sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
                sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
                sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
                sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
                sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
                sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
                sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
                sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
                sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
                sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
                sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
                sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
                sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
                sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
                sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
                sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
                sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
                sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
                sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
                sheet.write(row, col + 28, 'أنشئ بواسطة', main_heading2)
                sheet.write(row, col + 29, 'نوع النشاط الحالي', main_heading2)
                sheet.write(row, col + 30, 'تاريخ التسجيل', main_heading2)
                sheet.write(row, col + 31, 'مرجع التسجيل', main_heading2)
                sheet.write(row, col + 32, 'عدم التسجيل نظام تام', main_heading2)
                row += 1
                sheet.write(row, col, 'Assignment No.', main_heading2)
                sheet.write(row, col + 1, 'Assignment Date', main_heading2)
                sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
                sheet.write(row, col + 3, 'Sticker No.', main_heading2)
                sheet.write(row, col + 4, 'Maker Name', main_heading2)
                sheet.write(row, col + 5, 'Model Name', main_heading2)
                sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
                sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
                sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
                sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
                sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
                sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
                sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
                sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
                sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
                sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
                sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
                sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
                sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
                sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
                sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
                sheet.write(row, col + 21, 'Trailer Name', main_heading2)
                sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
                sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
                sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
                sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
                sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
                sheet.write(row, col + 27, 'Comment', main_heading2)
                sheet.write(row, col + 28, 'Created by', main_heading2)
                sheet.write(row, col + 29, 'New Vehicle Type', main_heading2)
                sheet.write(row, col + 30, 'Register Date', main_heading2)
                sheet.write(row, col + 31, 'Register Reference', main_heading2)
                sheet.write(row, col + 32, 'Reason', main_heading2)
                row += 1
                days_list = []
                grand_total = 0
                day_name = ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
                for rec_id in rec_ids:
                    if rec_id.assign_date:
                        day = rec_id.assign_date.weekday()
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
                            filtered_rec_ids = rec_ids.filtered(lambda r :r.assign_date and day_name[r.assign_date.weekday()]==day_id)
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 17,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 18, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 19,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_names), main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 23, str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 24,
                                                           str(rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 25,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 26, str(rec_id.maintenence_work), main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 28, str(rec_id.create_uid.name), main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 29,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
                if rec_ids_with_no_assign:
                    total = 0
                    sheet.write(row, col, 'Day', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'يوم', main_heading2)
                    row += 1
                    for rec_id in rec_ids_with_no_assign:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3, str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name), main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7, str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8, str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9, str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11, str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no), main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names), main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22, str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23, str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work), main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name), main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'weekly':
                self.env.ref(
                    'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Assignment Date (/week/) Report"
                sheet.merge_range('A1:Q1',
                                  'تقرير تسليم شاحنة تجميع بحسب تاريخ التسليم /الأسبوع/',
                                  main_heading3)
                row += 1
                sheet.merge_range('A2:Q2',
                                  'Vehicle Driver Assignment Group by Assignment Date (/week/) Report',
                                  main_heading3)
                row += 2
                sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
                sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
                sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
                sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
                sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
                sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
                sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
                sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
                sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
                sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
                sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
                sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
                sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
                sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
                sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
                sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
                sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
                sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
                sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
                sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
                sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
                sheet.write(row, col + 28, 'أنشئ بواسطة', main_heading2)
                sheet.write(row, col + 29, 'نوع النشاط الحالي', main_heading2)
                sheet.write(row, col + 30, 'تاريخ التسجيل', main_heading2)
                sheet.write(row, col + 31, 'مرجع التسجيل', main_heading2)
                sheet.write(row, col + 32, 'عدم التسجيل نظام تام', main_heading2)
                row += 1
                sheet.write(row, col, 'Assignment No.', main_heading2)
                sheet.write(row, col + 1, 'Assignment Date', main_heading2)
                sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
                sheet.write(row, col + 3, 'Sticker No.', main_heading2)
                sheet.write(row, col + 4, 'Maker Name', main_heading2)
                sheet.write(row, col + 5, 'Model Name', main_heading2)
                sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
                sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
                sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
                sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
                sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
                sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
                sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
                sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
                sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
                sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
                sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
                sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
                sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
                sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
                sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
                sheet.write(row, col + 21, 'Trailer Name', main_heading2)
                sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
                sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
                sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
                sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
                sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
                sheet.write(row, col + 27, 'Comment', main_heading2)
                sheet.write(row, col + 28, 'Created by', main_heading2)
                sheet.write(row, col + 29, 'New Vehicle Type', main_heading2)
                sheet.write(row, col + 30, 'Register Date', main_heading2)
                sheet.write(row, col + 31, 'Register Reference', main_heading2)
                sheet.write(row, col + 32, 'Reason', main_heading2)
                row += 1
                week_list = []
                grand_total = 0
                for rec_id in rec_ids:
                    if rec_id:
                        if rec_id.assign_date:
                            year = rec_id.assign_date.year
                            week = rec_id.assign_date.strftime("%V")
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
                        for rec_id in rec_ids:
                            if rec_id:
                                if rec_id.assign_date:
                                    doc_year = rec_id.assign_date.year
                                    doc_week = rec_id.assign_date.strftime("%V")
                                    doc_year_week = "year %s Week %s" % (doc_year, doc_week)
                                    if doc_year_week:
                                        if doc_year_week == week:
                                            if rec_id.assignment_no:
                                                sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                                            if rec_id.assign_date:
                                                sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                                            if rec_id.document_ref:
                                                sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                                sheet.write_string(row, col + 3,
                                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                                   main_heading)
                                            if rec_id.model_id.brand_id.name:
                                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                                   main_heading)
                                            if rec_id.model_id.name:
                                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                                   main_heading)
                                            if rec_id.model_id.display_name:
                                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                                   main_heading)
                                            if rec_id.vehicle_type_id.vehicle_type_name:
                                                sheet.write_string(row, col + 7,
                                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                                   main_heading)
                                            if rec_id.vehicle_type_id.domain_name.name:
                                                sheet.write_string(row, col + 8,
                                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                                   main_heading)
                                            if rec_id.assign_driver_id.driver_code:
                                                sheet.write_string(row, col + 9,
                                                                   str(rec_id.assign_driver_id.driver_code),
                                                                   main_heading)
                                            if rec_id.assign_driver_id.name:
                                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                                   main_heading)
                                            if rec_id.unassign_driver_id.driver_code:
                                                sheet.write_string(row, col + 11,
                                                                   str(rec_id.unassign_driver_id.driver_code),
                                                                   main_heading)
                                            if rec_id.unassign_driver_id.name:
                                                sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                                                   main_heading)
                                            if rec_id.comme:
                                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                                            if rec_id.truck_status_id.vehicle_status_name:
                                                sheet.write_string(row, col + 14,
                                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                                   main_heading)
                                            if rec_id.previous_trailer_no.trailer_taq_no:
                                                sheet.write_string(row, col + 15,
                                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                                   main_heading)
                                            if rec_id.previous_trailer_no.trailer_er_name:
                                                sheet.write_string(row, col + 16,
                                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                                   main_heading)
                                            if rec_id.previous_trailer_no.trailer_ar_name:
                                                sheet.write_string(row, col + 17,
                                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                                   main_heading)
                                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                                sheet.write_string(row, col + 18, str(
                                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                                   main_heading)
                                            if rec_id.pre_location_id.route_waypoint_name:
                                                sheet.write_string(row, col + 19,
                                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                                   main_heading)
                                            if rec_id.trailer_id.trailer_taq_no:
                                                sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                                                   main_heading)
                                            if rec_id.trailer_names:
                                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                                   main_heading)
                                            if rec_id.trailer_id.trailer_ar_name:
                                                sheet.write_string(row, col + 22,
                                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                                   main_heading)
                                            if rec_id.trailer_id.trailer_er_name:
                                                sheet.write_string(row, col + 23,
                                                                   str(rec_id.trailer_id.trailer_er_name),
                                                                   main_heading)
                                            if rec_id.new_trailer_asset_status.asset_status_name:
                                                sheet.write_string(row, col + 24,
                                                                   str(
                                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                                   main_heading)
                                            if rec_id.new_location_id.route_waypoint_name:
                                                sheet.write_string(row, col + 25,
                                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                                   main_heading)
                                            if rec_id.maintenence_work:
                                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                                   main_heading)
                                            if rec_id.comme:
                                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                                            if rec_id.create_uid.name:
                                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                                   main_heading)
                                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                                sheet.write_string(row, col + 29,
                                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                                   main_heading)
                                            if rec_id.register == 'yes':
                                                if rec_id.register_date:
                                                    sheet.write_string(row, col + 30, str(rec_id.register_date),
                                                                       main_heading)
                                                if rec_id.register_tamm:
                                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm),
                                                                       main_heading)
                                            if rec_id.register == 'no':
                                                if rec_id.description:
                                                    sheet.write_string(row, col + 32, str(rec_id.description),
                                                                       main_heading)
                                            total += 1
                                            row += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        grand_total += total
                        row += 1
                if rec_ids_with_no_assign:
                    total = 0
                    sheet.write(row, col, 'Week', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'أسبوع', main_heading2)
                    row += 1
                    for rec_id in rec_ids_with_no_assign:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'month':
                self.env.ref(
                    'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Assignment Date (Month) Report"
                sheet.merge_range('A1:Q1',
                                  'تقرير تسليم شاحنة تجميع بحسب تاريخ التسليم /الشهر/',
                                  main_heading3)
                row += 1
                sheet.merge_range('A2:Q2',
                                  'Vehicle Driver Assignment Group by Assignment Date (Month) Report',
                                  main_heading3)
                row += 2
                sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
                sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
                sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
                sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
                sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
                sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
                sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
                sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
                sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
                sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
                sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
                sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
                sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
                sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
                sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
                sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
                sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
                sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
                sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
                sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
                sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
                sheet.write(row, col + 28, 'أنشئ بواسطة', main_heading2)
                sheet.write(row, col + 29, 'نوع النشاط الحالي', main_heading2)
                sheet.write(row, col + 30, 'تاريخ التسجيل', main_heading2)
                sheet.write(row, col + 31, 'مرجع التسجيل', main_heading2)
                sheet.write(row, col + 32, 'عدم التسجيل نظام تام', main_heading2)
                row += 1
                sheet.write(row, col, 'Assignment No.', main_heading2)
                sheet.write(row, col + 1, 'Assignment Date', main_heading2)
                sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
                sheet.write(row, col + 3, 'Sticker No.', main_heading2)
                sheet.write(row, col + 4, 'Maker Name', main_heading2)
                sheet.write(row, col + 5, 'Model Name', main_heading2)
                sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
                sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
                sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
                sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
                sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
                sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
                sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
                sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
                sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
                sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
                sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
                sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
                sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
                sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
                sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
                sheet.write(row, col + 21, 'Trailer Name', main_heading2)
                sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
                sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
                sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
                sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
                sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
                sheet.write(row, col + 27, 'Comment', main_heading2)
                sheet.write(row, col + 28, 'Created by', main_heading2)
                sheet.write(row, col + 29, 'New Vehicle Type', main_heading2)
                sheet.write(row, col + 30, 'Register Date', main_heading2)
                sheet.write(row, col + 31, 'Register Reference', main_heading2)
                sheet.write(row, col + 32, 'Reason', main_heading2)
                row += 1
                months_list = []
                grand_total = 0
                for rec_id in rec_ids:
                    if rec_id.assign_date:
                        if rec_id.assign_date.strftime('%B') not in months_list:
                            months_list.append(rec_id.assign_date.strftime('%B'))
                for month in months_list:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, str(month), main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    filtered_rec_ids = rec_ids.filtered(lambda r: r.assign_date and r.assign_date.strftime('%B') == month)
                    for rec_id in filtered_rec_ids:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no), main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date), main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref), main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12, str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20, str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if rec_ids_with_no_assign:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for rec_id in rec_ids_with_no_assign:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'quarterly':
                self.env.ref(
                    'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Group by Assignment Date (Quarters) Report"
                sheet.merge_range('A1:Q1',
                                  'تقرير تسليم شاحنة تجميع بحسب تاريخ التسليم /ربع سنوي/',
                                  main_heading3)
                row += 1
                sheet.merge_range('A2:Q2',
                                  'Vehicle Driver Assignment Group by Assignment Date (Quarters) Report',
                                  main_heading3)
                row += 2
                sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
                sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
                sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
                sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
                sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
                sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
                sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
                sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
                sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
                sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
                sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
                sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
                sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
                sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
                sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
                sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
                sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
                sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
                sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
                sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
                sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
                sheet.write(row, col + 28, 'أنشئ بواسطة', main_heading2)
                sheet.write(row, col + 29, 'نوع النشاط الحالي', main_heading2)
                sheet.write(row, col + 30, 'تاريخ التسجيل', main_heading2)
                sheet.write(row, col + 31, 'مرجع التسجيل', main_heading2)
                sheet.write(row, col + 32, 'عدم التسجيل نظام تام', main_heading2)
                row += 1
                sheet.write(row, col, 'Assignment No.', main_heading2)
                sheet.write(row, col + 1, 'Assignment Date', main_heading2)
                sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
                sheet.write(row, col + 3, 'Sticker No.', main_heading2)
                sheet.write(row, col + 4, 'Maker Name', main_heading2)
                sheet.write(row, col + 5, 'Model Name', main_heading2)
                sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
                sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
                sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
                sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
                sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
                sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
                sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
                sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
                sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
                sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
                sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
                sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
                sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
                sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
                sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
                sheet.write(row, col + 21, 'Trailer Name', main_heading2)
                sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
                sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
                sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
                sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
                sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
                sheet.write(row, col + 27, 'Comment', main_heading2)
                sheet.write(row, col + 28, 'Created by', main_heading2)
                sheet.write(row, col + 29, 'New Vehicle Type', main_heading2)
                sheet.write(row, col + 30, 'Register Date', main_heading2)
                sheet.write(row, col + 31, 'Register Reference', main_heading2)
                sheet.write(row, col + 32, 'Reason', main_heading2)
                row += 1
                first_quarter = ['January', 'February', 'March']
                second_quarter = ['April', 'May', 'June']
                third_quarter = ['July', 'August', 'September']
                fourth_quarter = ['October', 'November', 'December']
                first_quarter_ids = rec_ids.filtered(
                    lambda r: (r.assign_date and r.assign_date.strftime('%B') in first_quarter))
                second_quarter_ids = rec_ids.filtered(
                    lambda r: (r.assign_date and r.assign_date.strftime('%B') in second_quarter))
                third_quarter_ids = rec_ids.filtered(
                    lambda r: (r.assign_date and r.assign_date.strftime('%B') in third_quarter))
                fourth_quarter_ids = rec_ids.filtered(
                    lambda r: (r.assign_date and r.assign_date.strftime('%B') in fourth_quarter))
                grand_total = 0
                if first_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'First', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for rec_id in first_quarter_ids:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if second_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'second', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for rec_id in second_quarter_ids:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if third_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Third', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for rec_id in third_quarter_ids:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if fourth_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Fourth', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for rec_id in fourth_quarter_ids:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if rec_ids_with_no_assign:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for rec_id in rec_ids_with_no_assign:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
            if docs.period_grouping_by == 'year':
                self.env.ref(
                    'bsg_vehicle_driver_assign_reports.vehicle_driver_assign_report_xlsx_id').report_file = "Vehicle Driver Assignment Report Group By Assignment Date Period Group By Year"
                sheet.merge_range('A1:Q1',
                                  'تقرير تسليم شاحنة تجميع بحسب تاريخ التسليم سنوي',
                                  main_heading3)
                row += 1
                sheet.merge_range('A2:Q2',
                                  'Vehicle Driver Assignment Group by Assignment Date Period Group By (year) Report',
                                  main_heading3)
                row += 2
                sheet.write(row, col, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 1, 'تاريخ الحركة', main_heading2)
                sheet.write(row, col + 2, 'رقم حركة التسليم', main_heading2)
                sheet.write(row, col + 3, 'استيكر الشاحنه ', main_heading2)
                sheet.write(row, col + 4, 'ماركة الشاحنة', main_heading2)
                sheet.write(row, col + 5, 'موديل الشاحنة', main_heading2)
                sheet.write(row, col + 6, 'اسم الشاحنة', main_heading2)
                sheet.write(row, col + 7, 'نشاط الشاحنة', main_heading2)
                sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
                sheet.write(row, col + 9, 'كود السائق المستلم', main_heading2)
                sheet.write(row, col + 10, 'أسم السائق المستلم', main_heading2)
                sheet.write(row, col + 11, 'كود السائق المسلم', main_heading2)
                sheet.write(row, col + 12, 'أسم السائق المسلم', main_heading2)
                sheet.write(row, col + 13, 'ملاحظات الشاحنة', main_heading2)
                sheet.write(row, col + 14, 'حالة الشاحنة', main_heading2)
                sheet.write(row, col + 15, 'استيكر المقطورة المستلم', main_heading2)
                sheet.write(row, col + 16, 'اسم المقطورة المستلم', main_heading2)
                sheet.write(row, col + 17, 'اسم المقطورة المستلم بالعربي', main_heading2)
                sheet.write(row, col + 18, 'حالة المقطورة المستلم', main_heading2)
                sheet.write(row, col + 19, 'الموقع الحالي للمقطورة المستلم', main_heading2)
                sheet.write(row, col + 20, 'رقم استيكر المقطورة المسلم', main_heading2)
                sheet.write(row, col + 21, 'اسم المقطورة المسلم', main_heading2)
                sheet.write(row, col + 22, 'اسم المقطورة المسلم بالعربي', main_heading2)
                sheet.write(row, col + 23, 'اسم المقطورة المسلم بالانجليزي', main_heading2)
                sheet.write(row, col + 24, 'حالة المقطورة المسلم', main_heading2)
                sheet.write(row, col + 25, 'اسم الموقع الحالي للمقطورة المسلم', main_heading2)
                sheet.write(row, col + 26, 'في ورشة الصيانة', main_heading2)
                sheet.write(row, col + 27, 'ملاحظات المقطورة', main_heading2)
                sheet.write(row, col + 28, 'أنشئ بواسطة', main_heading2)
                sheet.write(row, col + 29, 'نوع النشاط الحالي', main_heading2)
                sheet.write(row, col + 30, 'تاريخ التسجيل', main_heading2)
                sheet.write(row, col + 31, 'مرجع التسجيل', main_heading2)
                sheet.write(row, col + 32, 'عدم التسجيل نظام تام', main_heading2)
                row += 1
                sheet.write(row, col, 'Assignment No.', main_heading2)
                sheet.write(row, col + 1, 'Assignment Date', main_heading2)
                sheet.write(row, col + 2, 'UnAssignment No.', main_heading2)
                sheet.write(row, col + 3, 'Sticker No.', main_heading2)
                sheet.write(row, col + 4, 'Maker Name', main_heading2)
                sheet.write(row, col + 5, 'Model Name', main_heading2)
                sheet.write(row, col + 6, 'Truck/Model/Display Name', main_heading2)
                sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
                sheet.write(row, col + 8, 'Vehicle Domain Name', main_heading2)
                sheet.write(row, col + 9, 'Assignment Driver Code', main_heading2)
                sheet.write(row, col + 10, 'Assignment Driver Name', main_heading2)
                sheet.write(row, col + 11, 'Unassignment Driver Code', main_heading2)
                sheet.write(row, col + 12, 'Unassignment Driver Name', main_heading2)
                sheet.write(row, col + 13, 'Vehicle Comment', main_heading2)
                sheet.write(row, col + 14, 'Vehicle Status Name', main_heading2)
                sheet.write(row, col + 15, 'Previous Trailer Sticker No.', main_heading2)
                sheet.write(row, col + 16, 'Previous Trailer Name', main_heading2)
                sheet.write(row, col + 17, 'Previous Trailer Ar Name', main_heading2)
                sheet.write(row, col + 18, 'Previous Trailer Status Name', main_heading2)
                sheet.write(row, col + 19, 'Previous Trailer Location Name', main_heading2)
                sheet.write(row, col + 20, 'New Trailer Linking Sticker No', main_heading2)
                sheet.write(row, col + 21, 'Trailer Name', main_heading2)
                sheet.write(row, col + 22, 'New Trailer Linking Ar Name', main_heading2)
                sheet.write(row, col + 23, 'New Trailer Linking En Name', main_heading2)
                sheet.write(row, col + 24, 'New Trailer Status Name', main_heading2)
                sheet.write(row, col + 25, 'New Trailer Location Name', main_heading2)
                sheet.write(row, col + 26, 'Maintenance Workshop', main_heading2)
                sheet.write(row, col + 27, 'Comment', main_heading2)
                sheet.write(row, col + 28, 'Created by', main_heading2)
                sheet.write(row, col + 29, 'New Vehicle Type', main_heading2)
                sheet.write(row, col + 30, 'Register Date', main_heading2)
                sheet.write(row, col + 31, 'Register Reference', main_heading2)
                sheet.write(row, col + 32, 'Reason', main_heading2)
                row += 1
                years_list = []
                grand_total = 0
                for rec_id in rec_ids:
                    if rec_id.assign_date:
                        if rec_id.assign_date.year not in years_list:
                            years_list.append(rec_id.assign_date.year)
                if years_list:
                    for year in years_list:
                        if year:
                            total = 0
                            sheet.write(row, col, 'Year', main_heading2)
                            sheet.write_string(row, col + 1, str(year), main_heading)
                            sheet.write(row, col + 2, 'عام', main_heading2)
                            row += 1
                            filtered_rec_ids = rec_ids.filtered(lambda r:r.assign_date and r.assign_date.year == year)
                            for rec_id in filtered_rec_ids:
                                if rec_id:
                                    if rec_id.assignment_no:
                                        sheet.write_string(row, col, str(rec_id.assignment_no),
                                                           main_heading)
                                    if rec_id.assign_date:
                                        sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                           main_heading)
                                    if rec_id.document_ref:
                                        sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                           main_heading)
                                    if rec_id.fleet_vehicle_id.sudo().taq_number:
                                        sheet.write_string(row, col + 3,
                                                           str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                           main_heading)
                                    if rec_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                           main_heading)
                                    if rec_id.model_id.name:
                                        sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                           main_heading)
                                    if rec_id.model_id.display_name:
                                        sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 7,
                                                           str(rec_id.vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.vehicle_type_id.domain_name.name:
                                        sheet.write_string(row, col + 8,
                                                           str(rec_id.vehicle_type_id.domain_name.name),
                                                           main_heading)
                                    if rec_id.assign_driver_id.driver_code:
                                        sheet.write_string(row, col + 9,
                                                           str(rec_id.assign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.assign_driver_id.name:
                                        sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.driver_code:
                                        sheet.write_string(row, col + 11,
                                                           str(rec_id.unassign_driver_id.driver_code),
                                                           main_heading)
                                    if rec_id.unassign_driver_id.name:
                                        sheet.write_string(row, col + 12,
                                                           str(rec_id.unassign_driver_id.name),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                                    if rec_id.truck_status_id.vehicle_status_name:
                                        sheet.write_string(row, col + 14,
                                                           str(rec_id.truck_status_id.vehicle_status_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_taq_no:
                                        sheet.write_string(row, col + 15,
                                                           str(rec_id.previous_trailer_no.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_er_name:
                                        sheet.write_string(row, col + 16,
                                                           str(rec_id.previous_trailer_no.trailer_er_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_ar_name:
                                        sheet.write_string(row, col + 17,
                                                           str(rec_id.previous_trailer_no.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 18, str(
                                            rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.pre_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 19,
                                                           str(rec_id.pre_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_taq_no:
                                        sheet.write_string(row, col + 20,
                                                           str(rec_id.trailer_id.trailer_taq_no),
                                                           main_heading)
                                    if rec_id.trailer_names:
                                        sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_ar_name:
                                        sheet.write_string(row, col + 22,
                                                           str(rec_id.trailer_id.trailer_ar_name),
                                                           main_heading)
                                    if rec_id.trailer_id.trailer_er_name:
                                        sheet.write_string(row, col + 23,
                                                           str(rec_id.trailer_id.trailer_er_name),
                                                           main_heading)
                                    if rec_id.new_trailer_asset_status.asset_status_name:
                                        sheet.write_string(row, col + 24,
                                                           str(
                                                               rec_id.new_trailer_asset_status.asset_status_name),
                                                           main_heading)
                                    if rec_id.new_location_id.route_waypoint_name:
                                        sheet.write_string(row, col + 25,
                                                           str(rec_id.new_location_id.route_waypoint_name),
                                                           main_heading)
                                    if rec_id.maintenence_work:
                                        sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                           main_heading)
                                    if rec_id.comme:
                                        sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                                    if rec_id.create_uid.name:
                                        sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                           main_heading)
                                    if rec_id.x_vehicle_type_id.vehicle_type_name:
                                        sheet.write_string(row, col + 29,
                                                           str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                           main_heading)
                                    if rec_id.register == 'yes':
                                        if rec_id.register_date:
                                            sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                        if rec_id.register_tamm:
                                            sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                                    if rec_id.register == 'no':
                                        if rec_id.description:
                                            sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                                    total += 1
                                    row += 1
                            sheet.write(row, col, 'Total', main_heading2)
                            sheet.write_string(row, col + 1, str(total), main_heading)
                            sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                            grand_total += total
                            row += 1
                if rec_ids_with_no_assign:
                    total = 0
                    sheet.write(row, col, 'Year', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'عام', main_heading2)
                    row += 1
                    for rec_id in rec_ids_with_no_assign:
                        if rec_id:
                            if rec_id.assignment_no:
                                sheet.write_string(row, col, str(rec_id.assignment_no),
                                                   main_heading)
                            if rec_id.assign_date:
                                sheet.write_string(row, col + 1, str(rec_id.assign_date),
                                                   main_heading)
                            if rec_id.document_ref:
                                sheet.write_string(row, col + 2, str(rec_id.document_ref),
                                                   main_heading)
                            if rec_id.fleet_vehicle_id.sudo().taq_number:
                                sheet.write_string(row, col + 3,
                                                   str(rec_id.fleet_vehicle_id.sudo().taq_number),
                                                   main_heading)
                            if rec_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 4, str(rec_id.model_id.brand_id.name),
                                                   main_heading)
                            if rec_id.model_id.name:
                                sheet.write_string(row, col + 5, str(rec_id.model_id.name),
                                                   main_heading)
                            if rec_id.model_id.display_name:
                                sheet.write_string(row, col + 6, str(rec_id.model_id.display_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 7,
                                                   str(rec_id.vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.vehicle_type_id.domain_name.name:
                                sheet.write_string(row, col + 8,
                                                   str(rec_id.vehicle_type_id.domain_name.name),
                                                   main_heading)
                            if rec_id.assign_driver_id.driver_code:
                                sheet.write_string(row, col + 9,
                                                   str(rec_id.assign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.assign_driver_id.name:
                                sheet.write_string(row, col + 10, str(rec_id.assign_driver_id.name),
                                                   main_heading)
                            if rec_id.unassign_driver_id.driver_code:
                                sheet.write_string(row, col + 11,
                                                   str(rec_id.unassign_driver_id.driver_code),
                                                   main_heading)
                            if rec_id.unassign_driver_id.name:
                                sheet.write_string(row, col + 12,
                                                   str(rec_id.unassign_driver_id.name),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 13, str(rec_id.comme), main_heading)
                            if rec_id.truck_status_id.vehicle_status_name:
                                sheet.write_string(row, col + 14,
                                                   str(rec_id.truck_status_id.vehicle_status_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_taq_no:
                                sheet.write_string(row, col + 15,
                                                   str(rec_id.previous_trailer_no.trailer_taq_no),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_er_name:
                                sheet.write_string(row, col + 16,
                                                   str(rec_id.previous_trailer_no.trailer_er_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_ar_name:
                                sheet.write_string(row, col + 17,
                                                   str(rec_id.previous_trailer_no.trailer_ar_name),
                                                   main_heading)
                            if rec_id.previous_trailer_no.trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 18, str(
                                    rec_id.previous_trailer_no.trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.pre_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 19,
                                                   str(rec_id.pre_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_taq_no:
                                sheet.write_string(row, col + 20,
                                                   str(rec_id.trailer_id.trailer_taq_no),
                                                   main_heading)
                            if rec_id.trailer_names:
                                sheet.write_string(row, col + 21, str(rec_id.trailer_names),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_ar_name:
                                sheet.write_string(row, col + 22,
                                                   str(rec_id.trailer_id.trailer_ar_name),
                                                   main_heading)
                            if rec_id.trailer_id.trailer_er_name:
                                sheet.write_string(row, col + 23,
                                                   str(rec_id.trailer_id.trailer_er_name),
                                                   main_heading)
                            if rec_id.new_trailer_asset_status.asset_status_name:
                                sheet.write_string(row, col + 24,
                                                   str(
                                                       rec_id.new_trailer_asset_status.asset_status_name),
                                                   main_heading)
                            if rec_id.new_location_id.route_waypoint_name:
                                sheet.write_string(row, col + 25,
                                                   str(rec_id.new_location_id.route_waypoint_name),
                                                   main_heading)
                            if rec_id.maintenence_work:
                                sheet.write_string(row, col + 26, str(rec_id.maintenence_work),
                                                   main_heading)
                            if rec_id.comme:
                                sheet.write_string(row, col + 27, str(rec_id.comme), main_heading)
                            if rec_id.create_uid.name:
                                sheet.write_string(row, col + 28, str(rec_id.create_uid.name),
                                                   main_heading)
                            if rec_id.x_vehicle_type_id.vehicle_type_name:
                                sheet.write_string(row, col + 29,
                                                   str(rec_id.x_vehicle_type_id.vehicle_type_name),
                                                   main_heading)
                            if rec_id.register == 'yes':
                                if rec_id.register_date:
                                    sheet.write_string(row, col + 30, str(rec_id.register_date), main_heading)
                                if rec_id.register_tamm:
                                    sheet.write_string(row, col + 31, str(rec_id.register_tamm), main_heading)
                            if rec_id.register == 'no':
                                if rec_id.description:
                                    sheet.write_string(row, col + 32, str(rec_id.description), main_heading)
                            total += 1
                            row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                sheet.write(row, col, 'Grand Total', main_heading2)
                sheet.write_string(row, col + 1, str(grand_total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)






































































