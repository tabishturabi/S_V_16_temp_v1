from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd


class VehicleDetailsReportExcel(models.AbstractModel):
    _name = 'report.bsg_vehicle_details_reports.vehicle_data_report_xlsx'
    _inherit ='report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        domain=[]
        if docs.vehicle_make:
            domain += [('model_id.brand_id', 'in', docs.vehicle_make.ids)]
        if docs.vehicle_sticker_no:
            domain += [('id', 'in', docs.vehicle_sticker_no.ids)]
        if docs.model_year:
            year_list = []
            for year in docs.model_year:
                if year:
                    year_list.append(year.car_year_name)
            domain += [('model_year', 'in', year_list)]
        if docs.vehicle_state:
            domain += [('state_id', 'in', docs.vehicle_state.ids)]
        if docs.trailer_group:
            domain += [('trailer_id.trailer_asset_group', 'in', docs.trailer_group.ids)]
        if docs.current_branches:
            domain += [('current_branch_id', 'in', docs.current_branches.ids)]
        if docs.vehicle_type:
            domain += [('vehicle_type', 'in', docs.vehicle_type.ids)]
        if docs.domain_name:
            domain += [('vehicle_type.domain_name', 'in', docs.domain_name.ids)]
        if docs.vehicle_group:
            domain += [('vehicle_group_name', 'in', docs.vehicle_group.ids)]
        if docs.vehicle_status:
            domain += [('vehicle_status', 'in', docs.vehicle_status.ids)]
        if docs.driver_link == 'linked' and docs.driver_name:
            domain += [('bsg_driver', 'in', docs.driver_name.ids)]
        if docs.driver_link == 'linked' and not docs.driver_name:
            domain += [('bsg_driver', '!=',None)]
        if docs.driver_link == 'unlinked':
            domain += [('bsg_driver', '=',False)]
        if docs.trailer_link == 'linked' and docs.trailer_sticker_no:
            domain += [('trailer_id', 'in', docs.trailer_sticker_no.ids)]
        if docs.trailer_link == 'linked' and not docs.trailer_sticker_no:
            domain += [('trailer_id', '!=',None)]
        if docs.trailer_link == "unlinked":
            domain += [('trailer_id','=',False)]
        if docs.route_name:
            domain += [('bsg_route', 'in', docs.route_name.ids)]
        if docs.current_locations:
            domain += [('current_loc_id', 'in', docs.current_locations.ids)]
        rec_ids = self.env['fleet.vehicle'].search(domain)
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
        sheet.set_column('A:Q',15)
        row = 0
        col = 0
        if docs.grouping_by == 'all':
            self.env.ref('bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col+1, 'Maker Name', main_heading2)
            sheet.write(row, col+2, 'Model Name', main_heading2)
            sheet.write(row, col+3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col+4, 'License Plate', main_heading2)
            sheet.write(row, col+5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col+6, 'Chassis Number', main_heading2)
            sheet.write(row, col+7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col+8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col+9, 'Domain Name', main_heading2)
            sheet.write(row, col+10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col+11, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col+12, 'State Name', main_heading2)
            sheet.write(row, col+13, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col+14, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col+15, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col+16, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col+17, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col+18, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col+19, 'Trailer En Name', main_heading2)
            sheet.write(row, col+20, 'Trailer Group Name', main_heading2)
            sheet.write(row, col+21, 'Last Trip ID', main_heading2)
            sheet.write(row, col+22, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col+23, 'Current Branch Name', main_heading2)
            sheet.write(row, col+24, 'Current Location Name', main_heading2)
            sheet.write(row, col+25,'Last Odometer', main_heading2)
            sheet.write(row, col+26,'Created By', main_heading2)

            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col+1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col+2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col+3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col+4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col+5, 'سنة الصنع', main_heading2)
            sheet.write(row, col+6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col+7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col+8, 'النشاط ', main_heading2)
            sheet.write(row, col+9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col+10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col+11, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col+12, 'الحالة', main_heading2)
            sheet.write(row, col+13, 'كود السائق', main_heading2)
            sheet.write(row, col+14, 'اسم السائق ', main_heading2)
            sheet.write(row, col+15, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col+16, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col+17, 'رقم المقطوره', main_heading2)
            sheet.write(row, col+18, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col+19, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col+20, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col+21, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col+22, 'آخر خط سير', main_heading2)
            sheet.write(row, col+23, 'الفرع الحالي', main_heading2)
            sheet.write(row, col+24, 'الموقع الحالي', main_heading2)
            sheet.write(row, col+25,'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col+26, 'أنشي بواسطة', main_heading2)
            row += 1
            vehicle_ids=rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.taq_number:
                        sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                    if vehicle_id.model_id.brand_id.name:
                        sheet.write_string(row, col + 1,str(vehicle_id.model_id.brand_id.name), main_heading)
                    if vehicle_id.model_id.name:
                        sheet.write_string(row, col + 2,str(vehicle_id.model_id.name), main_heading)
                    if vehicle_id.vehicle_ar_name:
                        sheet.write_string(row, col + 3,str(vehicle_id.vehicle_ar_name), main_heading)
                    if vehicle_id.license_plate:
                        sheet.write_string(row, col + 4,str(vehicle_id.license_plate), main_heading)
                    if vehicle_id.model_year:
                        sheet.write_string(row, col + 5,str(vehicle_id.model_year), main_heading)
                    if vehicle_id.vin_sn:
                        sheet.write_string(row, col + 6,str(vehicle_id.vin_sn), main_heading)
                    if vehicle_id.estmaira_serial_no:
                        sheet.write_string(row, col + 7,str(vehicle_id.estmaira_serial_no), main_heading)
                    if vehicle_id.vehicle_type.vehicle_type_name:
                        sheet.write_string(row, col + 8,str(vehicle_id.vehicle_type.vehicle_type_name), main_heading)
                    if vehicle_id.vehicle_type.domain_name.name:
                        sheet.write_string(row, col + 9,str(vehicle_id.vehicle_type.domain_name.name), main_heading)
                    if vehicle_id.vehicle_group_name.vehicle_group_name:
                        sheet.write_string(row, col + 10,str(vehicle_id.vehicle_group_name.vehicle_group_name), main_heading)
                    if vehicle_id.vehicle_status.vehicle_status_name:
                        sheet.write_string(row, col + 11,str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                    if vehicle_id.state_id.name:
                        sheet.write_string(row, col + 12,str(vehicle_id.state_id.name), main_heading)
                    if vehicle_id.bsg_driver.driver_code:
                        sheet.write_string(row, col + 13,str(vehicle_id.bsg_driver.driver_code), main_heading)
                    if vehicle_id.bsg_driver.name:
                        sheet.write_string(row, col + 14,str(vehicle_id.bsg_driver.name), main_heading)
                    if vehicle_id.bsg_driver.mobile_phone:
                        sheet.write_string(row, col + 15,str(vehicle_id.bsg_driver.mobile_phone), main_heading)
                    if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                        sheet.write_string(row, col + 16,str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name), main_heading)
                    if vehicle_id.trailer_id.trailer_taq_no:
                        sheet.write_string(row, col + 17,str(vehicle_id.trailer_id.trailer_taq_no), main_heading)
                    if vehicle_id.trailer_id.trailer_ar_name:
                        sheet.write_string(row, col + 18,str(vehicle_id.trailer_id.trailer_ar_name), main_heading)
                    if vehicle_id.trailer_id.trailer_er_name:
                        sheet.write_string(row, col + 19,str(vehicle_id.trailer_id.trailer_er_name), main_heading)
                    if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                        sheet.write_string(row, col + 20,str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name), main_heading)
                    if vehicle_id.trip_id.name:
                        sheet.write_string(row, col + 21,str(vehicle_id.trip_id.name), main_heading)
                    if vehicle_id.route_id.route_name:
                        sheet.write_string(row, col + 22,str(vehicle_id.route_id.route_name), main_heading)
                    if vehicle_id.current_branch_id.branch_ar_name:
                        sheet.write_string(row, col + 23,str(vehicle_id.current_branch_id.branch_ar_name), main_heading)
                    if vehicle_id.current_loc_id.route_waypoint_name:
                        sheet.write_string(row, col + 24,str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                    if vehicle_id.odometer:
                        sheet.write_string(row, col + 25,str(vehicle_id.odometer), main_heading)
                    sheet.write_string(row, col + 26, str(vehicle_id.create_uid.name), main_heading)
                    row += 1
        if docs.grouping_by == 'by_maker_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Vehicle Make"
            sheet.merge_range('A1:Q1', 'مجموعة تقرير تفاصيل السيارة حسب اسم الصانع', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Maker Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Model Name', main_heading2)
            sheet.write(row, col + 2, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 3, 'License Plate', main_heading2)
            sheet.write(row, col + 4, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 11, 'State Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 6, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 7, 'النشاط ', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحالة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            make_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.model_id.brand_id.name not in make_list:
                        make_list.append(vehicle_id.model_id.brand_id.name)
            for make_id in make_list:
                if make_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Make', main_heading2)
                    sheet.write_string(row, col + 1, str(make_id), main_heading)
                    sheet.write(row, col + 2, 'صناعة المركبات', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.model_id.brand_id.name == make_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 3, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 4, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 6, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 7, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 9,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total +=1
                                row +=1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r:not r.model_id.brand_id)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Make', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'صناعة المركبات', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 2, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 3, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 4, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 5, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 6, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 7, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 9,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_model_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Model Name"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب موديل الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Model Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 3, 'License Plate', main_heading2)
            sheet.write(row, col + 4, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 11, 'State Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 6, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 7, 'النشاط ', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحالة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            model_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.model_id.name not in model_list:
                        model_list.append(vehicle_id.model_id.name)
            for model_id in model_list:
                if model_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Model', main_heading2)
                    sheet.write_string(row, col + 1, str(model_id), main_heading)
                    sheet.write(row, col + 2, 'طراز السيارة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.model_id.name == model_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 3, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 4, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 6, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 7, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 9,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.model_id)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Model', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'طراز السيارة', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 2, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 3, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 4, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 5, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 6, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 7, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 9,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_manufacturing_year':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Manufacturing Year"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب سنة الصنع', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Manufacturing Year', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 7, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 8, 'Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 11, 'State Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 6, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 7, 'النشاط ', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحالة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            manufacturing_year_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.model_year not in manufacturing_year_list:
                        manufacturing_year_list.append(vehicle_id.model_year)
            for manufacture_id in manufacturing_year_list:
                if manufacture_id:
                    total = 0
                    sheet.write(row, col, 'Manufacturing Year', main_heading2)
                    sheet.write_string(row, col + 1, str(manufacture_id), main_heading)
                    sheet.write(row, col + 2, 'تصنيع السنة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.model_year == manufacture_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 6, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 7, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 9,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.model_year)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Manufacturing Year', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'تصنيع السنة', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 5, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 6, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 7, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 9,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_vehicle_type_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Vehicle Type"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب النشاط ', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Vehicle Type Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Domain Name', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 11, 'State Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 9, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحالة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            type_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.vehicle_type.vehicle_type_name not in type_list:
                        type_list.append(vehicle_id.vehicle_type.vehicle_type_name)
            for type_id in type_list:
                if type_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Type', main_heading2)
                    sheet.write_string(row, col + 1, str(type_id), main_heading)
                    sheet.write(row, col + 2, 'نوع السيارة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.vehicle_type.vehicle_type_name == type_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 9,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total+=total
                    row += 1
            vehicle_ids_filtered = rec_ids.filtered(lambda r:not r.vehicle_type)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Type', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'نوع السيارة', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 9,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
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
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Domain Name"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب القطاع', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Domain Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 11, 'State Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحالة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            domain_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.vehicle_type.domain_name.name not in domain_list:
                        domain_list.append(vehicle_id.vehicle_type.domain_name.name)
            for domain_id in domain_list:
                if domain_id:
                    total = 0
                    sheet.write(row, col, 'Domain Name', main_heading2)
                    sheet.write_string(row, col + 1, str(domain_id), main_heading)
                    sheet.write(row, col + 2, 'اسم النطاق', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.vehicle_type.domain_name.name == domain_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 9,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.vehicle_type.domain_name)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Domain Name', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'اسم النطاق', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 9,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'vehicle_group_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Vehicle Group Name"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب اسم مجموعة الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Vehicle Group Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 11, 'State Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحالة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17,'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18,'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            group_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.vehicle_group_name.vehicle_group_name not in group_list:
                        group_list.append(vehicle_id.vehicle_group_name.vehicle_group_name)
            for group_id in group_list:
                if group_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Group Name', main_heading2)
                    sheet.write_string(row, col + 1, str(group_id), main_heading)
                    sheet.write(row, col + 2, 'اسم مجموعة المركبات', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.vehicle_group_name.vehicle_group_name == group_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.vehicle_group_name)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Group Name', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'اسم مجموعة المركبات', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'vehicle_status_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Vehicle Status"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب حالة الشاحنة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Vehicle Status Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 11, 'State Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 1, 'الحالة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            status_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.vehicle_status.vehicle_status_name not in status_list:
                        status_list.append(vehicle_id.vehicle_status.vehicle_status_name)
            for status_id in status_list:
                if status_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Status Name', main_heading2)
                    sheet.write_string(row, col + 1, str(status_id), main_heading)
                    sheet.write(row, col + 2, 'اسم حالة المركبة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.vehicle_status.vehicle_status_name == status_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r:not r.vehicle_status)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Status Name', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'اسم حالة المركبة', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_state_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Vehicle State Name"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب القطاع', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By State Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 12, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 14, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 15, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 16, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 17, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 18, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 12, 'كود السائق', main_heading2)
            sheet.write(row, col + 13, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 14, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 15, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 17, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 19, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            state_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.state_id.name not in state_list:
                        state_list.append(vehicle_id.state_id.name)
            for state_id in state_list:
                if state_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle State', main_heading2)
                    sheet.write_string(row, col + 1, str(state_id), main_heading)
                    sheet.write(row, col + 2, 'حالة السيارة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.state_id.name == state_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.state_id)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Vehicle State', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'حالة السيارة', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 11,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_trailer_group_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Trailer Group Name"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب اسم  مجموعة المقطوره', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Trailer Group Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 12, 'State Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 15, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 16, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 17, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 18, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 20, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 21, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 12, 'الحالة', main_heading2)
            sheet.write(row, col + 13, 'كود السائق', main_heading2)
            sheet.write(row, col + 14, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 15, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 17, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 19, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 20, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 21, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            trailer_group_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.trailer_id.trailer_asset_group.asset_group_name not in trailer_group_list:
                        trailer_group_list.append(vehicle_id.trailer_id.trailer_asset_group.asset_group_name)
            for trailer_group_id in trailer_group_list:
                if trailer_group_id:
                    total = 0
                    sheet.write(row, col, 'Trailer Group Name', main_heading2)
                    sheet.write_string(row, col + 1, str(trailer_group_id), main_heading)
                    sheet.write(row, col + 2, 'اسم مجموعة مقطورة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.trailer_id.trailer_asset_group.asset_group_name == trailer_group_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 15,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 19,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r:not r.trailer_id.trailer_asset_group)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Trailer Group Name', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'اسم مجموعة مقطورة', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 11, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 12, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 15,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 16, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 19,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 20, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 21, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_last_trip_route_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Last Trip Route Name"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب آخر خط سير ', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Last Trip Route Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 12, 'State Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 15, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 16, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 17, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 18, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 20, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 21, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 22, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 12, 'الحالة', main_heading2)
            sheet.write(row, col + 13, 'كود السائق', main_heading2)
            sheet.write(row, col + 14, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 15, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 17, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 19, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 20, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 21, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 22, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            route_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.route_id.route_name not in route_list:
                        route_list.append(vehicle_id.route_id.route_name)
            for route_id in route_list:
                if route_id:
                    total = 0
                    sheet.write(row, col, 'Last Trip Route', main_heading2)
                    sheet.write_string(row, col + 1, str(route_id), main_heading)
                    sheet.write(row, col + 2, 'آخر مسار رحلة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.route_id.route_name == route_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 12, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 15, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 16,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 19, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 20,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.bsg_route)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Last Trip Route', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'آخر مسار رحلة', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 11,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 12, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 15, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 16,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 19, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 20,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 21, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1,str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_current_branch_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Current Branch Name"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب الفرع الحالي', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Current Branch Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 12, 'State Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 15, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 16, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 17, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 18, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 20, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 21, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 22, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 23, 'Current Location Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 12, 'الحالة', main_heading2)
            sheet.write(row, col + 13, 'كود السائق', main_heading2)
            sheet.write(row, col + 14, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 15, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 17, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 19, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 20, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 21, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 22, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 23, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            branch_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.current_branch_id.branch_ar_name not in branch_list:
                        branch_list.append(vehicle_id.current_branch_id.branch_ar_name)
            for branch_id in branch_list:
                if branch_id:
                    total = 0
                    sheet.write(row, col, 'Current Branch', main_heading2)
                    sheet.write_string(row, col + 1, str(branch_id), main_heading)
                    sheet.write(row, col + 2, 'الفرع الحالي', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.current_branch_id.branch_ar_name == branch_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 12, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 15, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 16,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 19, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 20,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 23,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.current_branch_id)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Current Branch', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'الفرع الحالي', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 11,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 12, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 15, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 16,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 19, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 20,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 21, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_loc_id.route_waypoint_name:
                            sheet.write_string(row, col + 23,
                                               str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_current_location_name':
            self.env.ref(
                'bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Current Location"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات بحسب الموقع الحالي', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group By Current Location Name', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 12, 'State Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 15, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 16, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 17, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 18, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 20, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 21, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 22, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 23, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 24, 'Last Odometer', main_heading2)
            sheet.write(row, col + 25, 'Created By', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 12, 'الحالة', main_heading2)
            sheet.write(row, col + 13, 'كود السائق', main_heading2)
            sheet.write(row, col + 14, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 15, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 17, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 19, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 20, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 21, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 22, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 23, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 24, 'اخرقراءة للعداد', main_heading2)
            sheet.write(row, col + 25, 'أنشي بواسطة', main_heading2)
            row += 1
            location_list = []
            grand_total=0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.current_loc_id.route_waypoint_name not in location_list:
                        location_list.append(vehicle_id.current_loc_id.route_waypoint_name)
            for location_id in location_list:
                if location_id:
                    total = 0
                    sheet.write(row, col, 'Current Location', main_heading2)
                    sheet.write_string(row, col + 1, str(location_id), main_heading)
                    sheet.write(row, col + 2, 'الموقع الحالي', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.current_loc_id.route_waypoint_name == location_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 12, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 15, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 16,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 19, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 20,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 23, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                                sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total+=total
            vehicle_ids_filtered = rec_ids.filtered(lambda r: not r.current_loc_id)
            vehicle_ids = vehicle_ids_filtered
            if vehicle_ids:
                total = 0
                sheet.write(row, col, 'Current Location', main_heading2)
                sheet.write_string(row, col + 1,'Undefined', main_heading)
                sheet.write(row, col + 2, 'الموقع الحالي', main_heading2)
                row += 1
                for vehicle_id in vehicle_ids:
                    if vehicle_id:
                        if vehicle_id.taq_number:
                            sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                        if vehicle_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                               main_heading)
                        if vehicle_id.model_id.name:
                            sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                        if vehicle_id.vehicle_ar_name:
                            sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                        if vehicle_id.license_plate:
                            sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                        if vehicle_id.model_year:
                            sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                        if vehicle_id.vin_sn:
                            sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                        if vehicle_id.estmaira_serial_no:
                            sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                        if vehicle_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if vehicle_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if vehicle_id.vehicle_group_name.vehicle_group_name:
                            sheet.write_string(row, col + 10,
                                               str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                               main_heading)
                        if vehicle_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 11,
                                               str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                        if vehicle_id.state_id.name:
                            sheet.write_string(row, col + 12, str(vehicle_id.state_id.name), main_heading)
                        if vehicle_id.bsg_driver.driver_code:
                            sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.driver_code),
                                               main_heading)
                        if vehicle_id.bsg_driver.name:
                            sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.name), main_heading)
                        if vehicle_id.bsg_driver.mobile_phone:
                            sheet.write_string(row, col + 15, str(vehicle_id.bsg_driver.mobile_phone),
                                               main_heading)
                        if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                            sheet.write_string(row, col + 16,
                                               str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_taq_no:
                            sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_taq_no),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_ar_name:
                            sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_ar_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_er_name:
                            sheet.write_string(row, col + 19, str(vehicle_id.trailer_id.trailer_er_name),
                                               main_heading)
                        if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                            sheet.write_string(row, col + 20,
                                               str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                               main_heading)
                        if vehicle_id.trip_id.name:
                            sheet.write_string(row, col + 21, str(vehicle_id.trip_id.name),
                                               main_heading)
                        if vehicle_id.route_id.route_name:
                            sheet.write_string(row, col + 22, str(vehicle_id.route_id.route_name),
                                               main_heading)
                        if vehicle_id.current_branch_id.branch_ar_name:
                            sheet.write_string(row, col + 23, str(vehicle_id.current_branch_id.branch_ar_name),
                                               main_heading)
                        if vehicle_id.odometer:
                            sheet.write_string(row, col + 24, str(vehicle_id.odometer), main_heading)
                        sheet.write_string(row, col + 25, str(vehicle_id.create_uid.name), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                row += 1
                grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'by_created_by':
            self.env.ref('bsg_vehicle_details_reports.vehicle_details_report_xlsx_id').report_file = "Vehicles Details Report Group By Created By"
            sheet.merge_range('A1:Q1', 'تقرير تفصيلي لشاحنات التجميع بحسب انشئ بواسطة', main_heading3)
            row += 1
            sheet.merge_range('A2:Q2', 'Vehicle Details Report Group by Created by', main_heading3)
            row += 2
            sheet.write(row, col, 'Sticker No.', main_heading2)
            sheet.write(row, col + 1, 'Maker Name', main_heading2)
            sheet.write(row, col + 2, 'Model Name', main_heading2)
            sheet.write(row, col + 3, 'Vehicle AR Name', main_heading2)
            sheet.write(row, col + 4, 'License Plate', main_heading2)
            sheet.write(row, col + 5, 'Manufacturing Year', main_heading2)
            sheet.write(row, col + 6, 'Chassis Number', main_heading2)
            sheet.write(row, col + 7, 'Istimara Serial No.', main_heading2)
            sheet.write(row, col + 8, 'Vehicle Type Name', main_heading2)
            sheet.write(row, col + 9, 'Domain Name', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Group Name', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status Name', main_heading2)
            sheet.write(row, col + 12, 'State Name', main_heading2)
            sheet.write(row, col + 13, 'Vehicle Driver ID', main_heading2)
            sheet.write(row, col + 14, 'Vehicle Driver Name ', main_heading2)
            sheet.write(row, col + 15, 'Driver Mobile No.', main_heading2)
            sheet.write(row, col + 16, 'Driver Iqama No./National ID', main_heading2)
            sheet.write(row, col + 17, 'Trailer Sticker No.', main_heading2)
            sheet.write(row, col + 18, 'Trailer Ar Name', main_heading2)
            sheet.write(row, col + 19, 'Trailer En Name', main_heading2)
            sheet.write(row, col + 20, 'Trailer Group Name', main_heading2)
            sheet.write(row, col + 21, 'Last Trip ID', main_heading2)
            sheet.write(row, col + 22, 'Last Trip Route Name', main_heading2)
            sheet.write(row, col + 23, 'Current Branch Name', main_heading2)
            sheet.write(row, col + 24, 'Current Location Name', main_heading2)
            sheet.write(row, col + 25, 'Last Odometer', main_heading2)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه', main_heading2)
            sheet.write(row, col + 1, 'ماركة الشاحنة', main_heading2)
            sheet.write(row, col + 2, 'موديل الشاحنة', main_heading2)
            sheet.write(row, col + 3, 'اسم الشاحنة', main_heading2)
            sheet.write(row, col + 4, 'رقم اللوحه', main_heading2)
            sheet.write(row, col + 5, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 6, 'رقم الهيكل', main_heading2)
            sheet.write(row, col + 7, 'رقم التسلسلي للاستمارة', main_heading2)
            sheet.write(row, col + 8, 'النشاط ', main_heading2)
            sheet.write(row, col + 9, 'قطاع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'اسم مجموعة الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'حالة الشاحنة', main_heading2)
            sheet.write(row, col + 12, 'الحالة', main_heading2)
            sheet.write(row, col + 13, 'كود السائق', main_heading2)
            sheet.write(row, col + 14, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 15, 'رقم جوال السائق', main_heading2)
            sheet.write(row, col + 16, 'رقم إقامة/الهوئة الوطنية السائق', main_heading2)
            sheet.write(row, col + 17, 'رقم المقطوره', main_heading2)
            sheet.write(row, col + 18, 'اسم  المقطوره بالعربي', main_heading2)
            sheet.write(row, col + 19, 'اسم  المقطوره بالإنجليزي', main_heading2)
            sheet.write(row, col + 20, 'اسم  مجموعة المقطوره', main_heading2)
            sheet.write(row, col + 21, 'أخر رقم رحلة', main_heading2)
            sheet.write(row, col + 22, 'آخر خط سير', main_heading2)
            sheet.write(row, col + 23, 'الفرع الحالي', main_heading2)
            sheet.write(row, col + 24, 'الموقع الحالي', main_heading2)
            sheet.write(row, col + 25, 'اخرقراءة للعداد', main_heading2)
            row += 1
            created_by_list = []
            grand_total = 0
            vehicle_ids = rec_ids
            for vehicle_id in vehicle_ids:
                if vehicle_id:
                    if vehicle_id.create_uid.name not in created_by_list:
                        created_by_list.append(vehicle_id.create_uid.name)
            for creator_id in created_by_list:
                if creator_id:
                    total = 0
                    sheet.write(row, col, 'Created By', main_heading2)
                    sheet.write_string(row, col + 1, str(creator_id), main_heading)
                    sheet.write(row, col + 2, 'أنشي بواسطة', main_heading2)
                    row += 1
                    for vehicle_id in vehicle_ids:
                        if vehicle_id:
                            if vehicle_id.create_uid.name == creator_id:
                                if vehicle_id.taq_number:
                                    sheet.write_string(row, col, str(vehicle_id.taq_number), main_heading)
                                if vehicle_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(vehicle_id.model_id.brand_id.name),
                                                       main_heading)
                                if vehicle_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(vehicle_id.model_id.name), main_heading)
                                if vehicle_id.vehicle_ar_name:
                                    sheet.write_string(row, col + 3, str(vehicle_id.vehicle_ar_name), main_heading)
                                if vehicle_id.license_plate:
                                    sheet.write_string(row, col + 4, str(vehicle_id.license_plate), main_heading)
                                if vehicle_id.model_year:
                                    sheet.write_string(row, col + 5, str(vehicle_id.model_year), main_heading)
                                if vehicle_id.vin_sn:
                                    sheet.write_string(row, col + 6, str(vehicle_id.vin_sn), main_heading)
                                if vehicle_id.estmaira_serial_no:
                                    sheet.write_string(row, col + 7, str(vehicle_id.estmaira_serial_no), main_heading)
                                if vehicle_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 8, str(vehicle_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if vehicle_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9, str(vehicle_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if vehicle_id.vehicle_group_name.vehicle_group_name:
                                    sheet.write_string(row, col + 10,
                                                       str(vehicle_id.vehicle_group_name.vehicle_group_name),
                                                       main_heading)
                                if vehicle_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(vehicle_id.vehicle_status.vehicle_status_name), main_heading)
                                if vehicle_id.state_id.name:
                                    sheet.write_string(row, col + 12, str(vehicle_id.state_id.name), main_heading)
                                if vehicle_id.bsg_driver.driver_code:
                                    sheet.write_string(row, col + 13, str(vehicle_id.bsg_driver.driver_code),
                                                       main_heading)
                                if vehicle_id.bsg_driver.name:
                                    sheet.write_string(row, col + 14, str(vehicle_id.bsg_driver.name), main_heading)
                                if vehicle_id.bsg_driver.mobile_phone:
                                    sheet.write_string(row, col + 15, str(vehicle_id.bsg_driver.mobile_phone),
                                                       main_heading)
                                if vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name:
                                    sheet.write_string(row, col + 16,
                                                       str(vehicle_id.bsg_driver.bsg_empiqama.bsg_iqama_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_taq_no:
                                    sheet.write_string(row, col + 17, str(vehicle_id.trailer_id.trailer_taq_no),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_ar_name:
                                    sheet.write_string(row, col + 18, str(vehicle_id.trailer_id.trailer_ar_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_er_name:
                                    sheet.write_string(row, col + 19, str(vehicle_id.trailer_id.trailer_er_name),
                                                       main_heading)
                                if vehicle_id.trailer_id.trailer_asset_group.asset_group_name:
                                    sheet.write_string(row, col + 20,
                                                       str(vehicle_id.trailer_id.trailer_asset_group.asset_group_name),
                                                       main_heading)
                                if vehicle_id.trip_id.name:
                                    sheet.write_string(row, col + 21, str(vehicle_id.trip_id.name),
                                                       main_heading)
                                if vehicle_id.route_id.route_name:
                                    sheet.write_string(row, col + 22, str(vehicle_id.route_id.route_name),
                                                       main_heading)
                                if vehicle_id.current_branch_id.branch_ar_name:
                                    sheet.write_string(row, col + 23, str(vehicle_id.current_branch_id.branch_ar_name),
                                                       main_heading)
                                if vehicle_id.current_loc_id.route_waypoint_name:
                                    sheet.write_string(row, col + 24,
                                                       str(vehicle_id.current_loc_id.route_waypoint_name), main_heading)
                                if vehicle_id.odometer:
                                    sheet.write_string(row, col + 25, str(vehicle_id.odometer), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    row += 1
                    grand_total += total
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)