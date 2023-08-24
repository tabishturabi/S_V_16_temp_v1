from odoo import models
from datetime import date, datetime
from ummalqura.hijri_date import HijriDate
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd


class VehicleDocumentsReportExcel(models.AbstractModel):
    _name = 'report.bsg_vehicle_documents_reports.vehicle_doc_report_xlsx'
    _inherit ='report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):
        model = 'vehicle.documents.report.wizard'
        docs = self.env[model].browse(self.env.context.get('active_id'))
        domain = []
        if docs.last_update_by:
            domain += [('write_uid', 'in', docs.last_update_by.ids)]
        if docs.create_by:
            domain += [('create_uid', 'in', docs.create_by.ids)]
        if docs.vehicle_make:
            domain += [('document_id.model_id.brand_id', 'in', docs.vehicle_make.ids)]
        if docs.document_type:
            domain += [('document_type_id', 'in', docs.document_type.ids)]
        if docs.vehicle_sticker_no:
            domain += [('document_id', 'in', docs.vehicle_sticker_no.ids)]
        if docs.driver_link == 'linked' and docs.driver_name:
            domain += [('document_id.bsg_driver', 'in', docs.driver_name.ids)]
        if docs.driver_link == 'linked' and not docs.driver_name:
            domain += [('document_id.bsg_driver', '!=', None)]
        if docs.driver_link == 'unlinked':
            domain += [('document_id.bsg_driver', '=', False)]
        if docs.vehicle_state:
            domain += [('document_id.state_id', 'in', docs.vehicle_state.ids)]
        if docs.vehicle_status:
            domain += [('document_id.vehicle_status', 'in', docs.vehicle_status.ids)]
        if docs.model_year:
            year_list = []
            for year in docs.model_year:
                if year:
                    year_list.append(year.car_year_name)
            domain += [('document_id.model_year', 'in', year_list)]
        if docs.vehicle_type:
            domain += [('document_id.vehicle_type', 'in', docs.vehicle_type.ids)]
        if docs.domain_name:
            domain += [('document_id.vehicle_type.domain_name', 'in', docs.domain_name.ids)]
        if docs.date_filter_by == 'expire_date':
            if docs.expire_date_condition == 'is_equal_to':
                domain += [('expiry_date', '=', docs.expiry_date)]
            if docs.expire_date_condition == 'is_not_equal_to':
                domain += [('expiry_date', '!=', docs.expiry_date)]
            if docs.expire_date_condition == 'is_after':
                domain += [('expiry_date', '>', docs.expiry_date)]
            if docs.expire_date_condition == 'is_before':
                domain += [('expiry_date', '<', docs.expiry_date)]
            if docs.expire_date_condition == 'is_after_or_equal_to':
                domain += [('expiry_date', '>=', docs.expiry_date)]
            if docs.expire_date_condition == 'is_before_or_equal_to':
                domain += [('expiry_date', '<=', docs.expiry_date)]
            if docs.expire_date_condition == 'is_between':
                domain += [('expiry_date', '>', docs.date_from),
                           ('expiry_date', '<', docs.date_to)]
            if docs.expire_date_condition == 'is_set':
                domain += [('expiry_date', '!=', None)]
            if docs.expire_date_condition == 'is_not_set':
                domain += [('expiry_date', '=', None)]
        if docs.date_filter_by == 'renewel_license_date':
            if docs.renewal_license_date_condition == 'is_equal_to':
                domain += [('renewel_license_date', '=', docs.renewal_license_date)]
            if docs.renewal_license_date_condition == 'is_not_equal_to':
                domain += [('renewel_license_date', '!=', docs.renewal_license_date)]
            if docs.renewal_license_date_condition == 'is_after':
                domain += [('renewel_license_date', '>', docs.renewal_license_date)]
            if docs.renewal_license_date_condition == 'is_before':
                domain += [('renewel_license_date', '<', docs.renewal_license_date)]
            if docs.renewal_license_date_condition == 'is_after_or_equal_to':
                domain += [('renewel_license_date', '>=', docs.renewal_license_date)]
            if docs.renewal_license_date_condition == 'is_before_or_equal_to':
                domain += [('renewel_license_date', '<=', docs.renewal_license_date)]
            if docs.renewal_license_date_condition == 'is_between':
                domain += [('renewel_license_date', '>', docs.date_from_renewel_license),
                           ('renewel_license_date', '<', docs.date_to_renewel_license)]
            if docs.renewal_license_date_condition == 'is_set':
                domain += [('renewel_license_date', '!=', None)]
            if docs.renewal_license_date_condition == 'is_not_set':
                domain += [('renewel_license_date', '=', None)]
        if docs.date_filter_by == 'last_update_date':
            if docs.last_update_date_condition == 'is_equal_to':
                domain += [('last_update_date', '=', docs.last_update_date)]
            if docs.last_update_date_condition == 'is_not_equal_to':
                domain += [('last_update_date', '!=', docs.last_update_date)]
            if docs.last_update_date_condition == 'is_after':
                domain += [('last_update_date', '>', docs.last_update_date)]
            if docs.last_update_date_condition == 'is_before':
                domain += [('last_update_date', '<', docs.last_update_date)]
            if docs.last_update_date_condition == 'is_after_or_equal_to':
                domain += [('last_update_date', '>=', docs.last_update_date)]
            if docs.last_update_date_condition == 'is_before_or_equal_to':
                domain += [('last_update_date', '<=', docs.last_update_date)]
            if docs.last_update_date_condition == 'is_between':
                domain += [('last_update_date', '>', docs.date_from_last_update),
                           ('last_update_date', '<', docs.date_to_last_update)]
            if docs.last_update_date_condition == 'is_set':
                domain += [('last_update_date', '!=', None)]
            if docs.last_update_date_condition == 'is_not_set':
                domain += [('last_update_date', '=', None)]
        rec_ids = self.env['document.info.fleet'].search(domain)
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
        sheet = workbook.add_worksheet('Vehicle Documents Report')
        sheet.set_column('A:V', 15)
        row = 0
        col = 0
        if docs.grouping_by == 'all':
            self.env.ref(
                'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report"
            sheet.merge_range('A1:V1', 'تقرير وثائق الشاحنات', main_heading3)
            row += 1
            sheet.merge_range('A2:V2', 'Vehicle Document Reports', main_heading3)
            row += 2
            sheet.write(row, col, 'Print ON', main_heading2)
            sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
            sheet.write(row, col + 1, 'الماركة', main_heading2)
            sheet.write(row, col + 2, 'الموديل', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
            sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
            sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 8, 'نوع المستند', main_heading2)
            sheet.write(row, col + 9, 'القطاع ', main_heading2)
            sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحاله ', main_heading2)
            sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
            sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
            sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
            sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
            sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
            sheet.write(row, col + 17, 'انشأ من قبل ', main_heading2)
            sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة', main_heading2)
            sheet.write(row, col + 19, 'تاريخ تجديد الوثيقة هجري', main_heading2)
            sheet.write(row, col + 20, 'تعديل من قبل', main_heading2)
            sheet.write(row, col + 21, 'تاريخ آخر تعديل', main_heading2)
            row += 1
            sheet.write(row, col, 'Sticker No', main_heading2)
            sheet.write(row, col + 1, 'Make', main_heading2)
            sheet.write(row, col + 2, 'Model', main_heading2)
            sheet.write(row, col + 3, 'License Plate', main_heading2)
            sheet.write(row, col + 4, 'Model Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Employee Code ', main_heading2)
            sheet.write(row, col + 7, 'Driver name ', main_heading2)
            sheet.write(row, col + 8, 'Document Type', main_heading2)
            sheet.write(row, col + 9, 'Domain Name ', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
            sheet.write(row, col + 12, 'Issue Date', main_heading2)
            sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
            sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
            sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
            sheet.write(row, col + 16, 'No. Of Days', main_heading2)
            sheet.write(row, col + 17, 'Created By', main_heading2)
            sheet.write(row, col + 18, 'Renewal License date', main_heading2)
            sheet.write(row, col + 19, 'Renewal License Hijri date', main_heading2)
            sheet.write(row, col + 20, 'last update by', main_heading2)
            sheet.write(row, col + 21, 'last update on', main_heading2)

            row += 1
            doc_ids = sorted(rec_ids, key=lambda r: (r.document_id, r.document_type_id.document_type_id))
            for doc_id in doc_ids:
                if doc_id:
                    if doc_id.expiry_date:
                        hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                        delta = doc_id.expiry_date - date.today()
                        days = int(delta.days)
                    else:
                        days = 0
                        hijri_expiry_date = None

                    if doc_id.issue_date:
                        hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                    else:
                        hijri_issue_date = None
                    if doc_id.renewel_license_date:
                        renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                    else:
                        renewel_license_hijri_date = None

                    if doc_id.document_id.taq_number:
                        sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                    if doc_id.document_id.model_id.brand_id.name:
                        sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name), main_heading)
                    if doc_id.document_id.model_id.name:
                        sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                    if doc_id.document_id.license_plate:
                        sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                    if doc_id.document_id.model_year:
                        sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                    if doc_id.document_id.vin_sn:
                        sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                    if doc_id.document_id.bsg_driver.employee_code:
                        sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code), main_heading)
                    if doc_id.document_id.bsg_driver.name:
                        sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                    if doc_id.document_type_id.document_type_id:
                        sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id), main_heading)
                    if doc_id.document_id.vehicle_type.domain_name.name:
                        sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.domain_name.name),
                                           main_heading)
                    if doc_id.document_id.vehicle_type.vehicle_type_name:
                        sheet.write_string(row, col + 10, str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                           main_heading)
                    if doc_id.document_id.vehicle_status.vehicle_status_name:
                        sheet.write_string(row, col + 11, str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                           main_heading)
                    if doc_id.issue_date:
                        sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                        sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                    if doc_id.expiry_date:
                        sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                        sheet.write_string(row, col + 16, str(days), main_heading)
                    if hijri_expiry_date:
                        sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                    if doc_id.create_uid.name:
                        sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                    if doc_id.renewel_license_date:
                        sheet.write_string(row, col + 18, str(doc_id.renewel_license_date), main_heading)
                    if renewel_license_hijri_date:
                        sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                    if doc_id.write_uid.name:
                        sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                    if doc_id.last_update_date:
                        sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                    row += 1
        if docs.grouping_by == 'document_type':
            self.env.ref(
                'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Document Type"
            sheet.write(row, col + 7, 'تقرير وثائق الشاحنات بحسب نوع الوثيقة', main_heading3)
            row += 1
            sheet.write(row, col + 7, 'Vehicle Document Reports Grouping By Document Type',
                        main_heading3)
            row += 2
            sheet.write(row, col, 'Print ON', main_heading2)
            sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
            sheet.write(row, col + 1, 'الماركة', main_heading2)
            sheet.write(row, col + 2, 'الموديل', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
            sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
            sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 8, 'القطاع ', main_heading2)
            sheet.write(row, col + 9, 'نوع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'الحاله ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ الإصدار', main_heading2)
            sheet.write(row, col + 12, 'تاريخ الإصدار هجري', main_heading2)
            sheet.write(row, col + 13, 'تاريخ الانتهاء ', main_heading2)
            sheet.write(row, col + 14, 'تاريخ الانتهاء هجري', main_heading2)
            sheet.write(row, col + 15, 'عدد الايام ', main_heading2)
            sheet.write(row, col + 16, 'انشأ من قبل ', main_heading2)
            sheet.write(row, col + 17, 'تاريخ تجديد الوثيقة', main_heading2)
            sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة هجري', main_heading2)
            sheet.write(row, col + 29, 'تعديل من قبل', main_heading2)
            sheet.write(row, col + 20, 'تاريخ آخر تعديل', main_heading2)
            row += 1
            sheet.write(row, col, 'Sticker No ', main_heading2)
            sheet.write(row, col + 1, 'Make', main_heading2)
            sheet.write(row, col + 2, 'Model', main_heading2)
            sheet.write(row, col + 3, 'License Plate ', main_heading2)
            sheet.write(row, col + 4, 'Model Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Employee Code ', main_heading2)
            sheet.write(row, col + 7, 'Driver name ', main_heading2)
            sheet.write(row, col + 8, 'Domain Name ', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status ', main_heading2)
            sheet.write(row, col + 11, 'Issue Date', main_heading2)
            sheet.write(row, col + 12, 'Issue Date Hijri', main_heading2)
            sheet.write(row, col + 13, 'Expiry Date ', main_heading2)
            sheet.write(row, col + 14, 'Expiry Date Hijri', main_heading2)
            sheet.write(row, col + 15, 'No. Of Days', main_heading2)
            sheet.write(row, col + 16, 'Created By', main_heading2)
            sheet.write(row, col + 17, 'Renewal License date', main_heading2)
            sheet.write(row, col + 18, 'Renewal License Hijri date', main_heading2)
            sheet.write(row, col + 19, 'last update by', main_heading2)
            sheet.write(row, col + 20, 'last update on', main_heading2)
            row += 1
            doc_type_list = []
            grand_total = 0
            doc_ids = sorted(rec_ids, key=lambda r: r.document_id)
            for doc_id in doc_ids:
                if doc_id:
                    if doc_id.document_type_id.document_type_id not in doc_type_list:
                        doc_type_list.append(doc_id.document_type_id.document_type_id)
            for doc_type_id in doc_type_list:
                if doc_type_id:
                    total = 0
                    sheet.write(row, col, 'Document Type', main_heading2)
                    sheet.write_string(row, col + 1, str(doc_type_id), main_heading)
                    sheet.write(row, col + 2, 'نوع المستند', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        if doc_id:
                            if doc_id.document_type_id.document_type_id == doc_type_id:
                                if doc_id.expiry_date:
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                else:
                                    days = 0
                                    hijri_expiry_date = None

                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                       main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 8,
                                                       str(doc_id.document_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                                if doc_id.create_uid.name:
                                    sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
            filtered_doc_ids = rec_ids.filtered(lambda r: not r.document_type_id)
            doc_ids = sorted(filtered_doc_ids, key=lambda r: r.document_id)
            if doc_ids:
                total = 0
                sheet.write(row, col, 'Document Type', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'نوع المستند', main_heading2)
                row += 1
                for doc_id in doc_ids:
                    if doc_id:
                        if doc_id.expiry_date:
                            hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                            delta = doc_id.expiry_date - date.today()
                            days = int(delta.days)
                        else:
                            days = 0
                            hijri_expiry_date = None

                        if doc_id.issue_date:
                            hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                        else:
                            hijri_issue_date = None
                        if doc_id.renewel_license_date:
                            renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                        else:
                            renewel_license_hijri_date = None
                        if doc_id.document_id.taq_number:
                            sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                        if doc_id.document_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                               main_heading)
                        if doc_id.document_id.model_id.name:
                            sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                        if doc_id.document_id.license_plate:
                            sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                        if doc_id.document_id.model_year:
                            sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                        if doc_id.document_id.vin_sn:
                            sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                        if doc_id.document_id.bsg_driver.employee_code:
                            sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                               main_heading)
                        if doc_id.document_id.bsg_driver.name:
                            sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                        if doc_id.document_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 8, str(doc_id.document_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if doc_id.document_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if doc_id.document_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                               main_heading)
                        if doc_id.issue_date:
                            sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                            sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                        if doc_id.expiry_date:
                            sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if hijri_expiry_date:
                            sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                        if doc_id.create_uid.name:
                            sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                        if doc_id.renewel_license_date:
                            sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                        if renewel_license_hijri_date:
                            sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                        if doc_id.write_uid.name:
                            sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                        if doc_id.last_update_date:
                            sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
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
        if docs.grouping_by == 'vehicle_make':
            self.env.ref(
                'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Vehicle Make"
            sheet.write(row, col + 7, 'تقرير وثائق الشاحنات بحسب ماركة الشاحنة', main_heading3)
            row += 1
            sheet.write(row, col + 7, 'Vehicle Document Reports Grouping By Vehicle Make', main_heading3)
            row += 2
            sheet.write(row, col, 'Print ON', main_heading2)
            sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
            sheet.write(row, col + 1, 'الموديل', main_heading2)
            sheet.write(row, col + 2, 'رقم اللوحه ', main_heading2)
            sheet.write(row, col + 3, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 4, 'رقم الهيكل ', main_heading2)
            sheet.write(row, col + 5, 'كمبيوتر السائق ', main_heading2)
            sheet.write(row, col + 6, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 7, 'نوع المستند', main_heading2)
            sheet.write(row, col + 8, 'القطاع ', main_heading2)
            sheet.write(row, col + 9, 'نوع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'الحاله ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ الإصدار', main_heading2)
            sheet.write(row, col + 12, 'تاريخ الإصدار هجري', main_heading2)
            sheet.write(row, col + 13, 'تاريخ الانتهاء ', main_heading2)
            sheet.write(row, col + 14, 'تاريخ الانتهاء هجري', main_heading2)
            sheet.write(row, col + 15, 'عدد الايام ', main_heading2)
            sheet.write(row, col + 16, 'انشأ من قبل ', main_heading2)
            sheet.write(row, col + 17, 'تاريخ تجديد الوثيقة', main_heading2)
            sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة هجري', main_heading2)
            sheet.write(row, col + 19, 'تعديل من قبل', main_heading2)
            sheet.write(row, col + 20, 'تاريخ آخر تعديل', main_heading2)
            row += 1
            sheet.write(row, col, 'Sticker No ', main_heading2)
            sheet.write(row, col + 1, 'Model', main_heading2)
            sheet.write(row, col + 2, 'License Plate ', main_heading2)
            sheet.write(row, col + 3, 'Model Year', main_heading2)
            sheet.write(row, col + 4, 'Chassis Number', main_heading2)
            sheet.write(row, col + 5, 'Employee Code ', main_heading2)
            sheet.write(row, col + 6, 'Driver name ', main_heading2)
            sheet.write(row, col + 7, 'Document Type', main_heading2)
            sheet.write(row, col + 8, 'Domain Name ', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status ', main_heading2)
            sheet.write(row, col + 11, 'Issue Date', main_heading2)
            sheet.write(row, col + 12, 'Issue Date Hijri', main_heading2)
            sheet.write(row, col + 13, 'Expiry Date ', main_heading2)
            sheet.write(row, col + 14, 'Expiry Date Hijri', main_heading2)
            sheet.write(row, col + 15, 'No. Of Days', main_heading2)
            sheet.write(row, col + 16, 'Created By', main_heading2)
            sheet.write(row, col + 17, 'Renewal License date', main_heading2)
            sheet.write(row, col + 18, 'Renewal License Hijri date', main_heading2)
            sheet.write(row, col + 19, 'last update by', main_heading2)
            sheet.write(row, col + 20, 'last update on', main_heading2)
            row += 1
            grand_total = 0
            vehicle_make_list = []
            doc_ids = sorted(rec_ids, key=lambda r: (
            r.document_id.model_id.brand_id, r.document_id, r.document_type_id.document_type_id))
            for doc_id in doc_ids:
                if doc_id:
                    if doc_id.document_id.model_id.brand_id.name not in vehicle_make_list:
                        vehicle_make_list.append(doc_id.document_id.model_id.brand_id.name)
            for vehicle_make_id in vehicle_make_list:
                if vehicle_make_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Make', main_heading2)
                    sheet.write_string(row, col + 1, str(vehicle_make_id), main_heading)
                    sheet.write(row, col + 2, 'ماركة الشاحنة', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        if doc_id:
                            if doc_id.document_id.model_id.brand_id.name == vehicle_make_id:
                                if doc_id.expiry_date:
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                else:
                                    days = 0
                                    hijri_expiry_date = None

                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.model_year), main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_type_id.document_type_id:
                                    sheet.write_string(row, col + 7, str(doc_id.document_type_id.document_type_id),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 8,
                                                       str(doc_id.document_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                                if doc_id.create_uid.name:
                                    sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
            filtered_doc_ids = rec_ids.filtered(lambda r: not r.document_id.model_id.brand_id)
            doc_ids = sorted(filtered_doc_ids, key=lambda r: (
            r.document_id.model_id.brand_id, r.document_id, r.document_type_id.document_type_id))
            if doc_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Make', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'ماركة الشاحنة', main_heading2)
                row += 1
                for doc_id in doc_ids:
                    if doc_id:
                        if doc_id.expiry_date:
                            hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                            delta = doc_id.expiry_date - date.today()
                            days = int(delta.days)
                        else:
                            days = 0
                            hijri_expiry_date = None

                        if doc_id.issue_date:
                            hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                        else:
                            hijri_issue_date = None
                        if doc_id.renewel_license_date:
                            renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                        else:
                            renewel_license_hijri_date = None
                        if doc_id.document_id.taq_number:
                            sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                        if doc_id.document_id.model_id.name:
                            sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.name), main_heading)
                        if doc_id.document_id.license_plate:
                            sheet.write_string(row, col + 2, str(doc_id.document_id.license_plate), main_heading)
                        if doc_id.document_id.model_year:
                            sheet.write_string(row, col + 3, str(doc_id.document_id.model_year), main_heading)
                        if doc_id.document_id.vin_sn:
                            sheet.write_string(row, col + 4, str(doc_id.document_id.vin_sn), main_heading)
                        if doc_id.document_id.bsg_driver.employee_code:
                            sheet.write_string(row, col + 5, str(doc_id.document_id.bsg_driver.employee_code),
                                               main_heading)
                        if doc_id.document_id.bsg_driver.name:
                            sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.name), main_heading)
                        if doc_id.document_type_id.document_type_id:
                            sheet.write_string(row, col + 7, str(doc_id.document_type_id.document_type_id),
                                               main_heading)
                        if doc_id.document_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 8, str(doc_id.document_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if doc_id.document_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if doc_id.document_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                               main_heading)
                        if doc_id.issue_date:
                            sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                            sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                        if doc_id.expiry_date:
                            sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if hijri_expiry_date:
                            sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                        if doc_id.create_uid.name:
                            sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                        if doc_id.renewel_license_date:
                            sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                        if renewel_license_hijri_date:
                            sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                        if doc_id.write_uid.name:
                            sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                        if doc_id.last_update_date:
                            sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
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
        if docs.grouping_by == 'vehicle_type':
            self.env.ref(
                'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Vehicle Type"
            sheet.write(row, col + 7, 'تقرير وثائق الشاحنات بحسب نوع الشاحنة', main_heading3)
            row += 1
            sheet.write(row, col + 7, 'Vehicle Document Reports Grouping By Vehicle Type', main_heading3)
            row += 2
            sheet.write(row, col, 'Print ON', main_heading2)
            sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
            sheet.write(row, col + 1, 'الماركة', main_heading2)
            sheet.write(row, col + 2, 'الموديل', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
            sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
            sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 8, 'نوع المستند', main_heading2)
            sheet.write(row, col + 9, 'القطاع ', main_heading2)
            sheet.write(row, col + 10, 'الحاله ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ الإصدار', main_heading2)
            sheet.write(row, col + 12, 'تاريخ الإصدار هجري', main_heading2)
            sheet.write(row, col + 13, 'تاريخ الانتهاء ', main_heading2)
            sheet.write(row, col + 14, 'تاريخ الانتهاء هجري', main_heading2)
            sheet.write(row, col + 15, 'عدد الايام ', main_heading2)
            sheet.write(row, col + 16, 'انشأ من قبل ', main_heading2)
            sheet.write(row, col + 17, 'تاريخ تجديد الوثيقة', main_heading2)
            sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة هجري', main_heading2)
            sheet.write(row, col + 19, 'تعديل من قبل', main_heading2)
            sheet.write(row, col + 20, 'تاريخ آخر تعديل', main_heading2)
            row += 1
            sheet.write(row, col, 'Sticker No ', main_heading2)
            sheet.write(row, col + 1, 'Make', main_heading2)
            sheet.write(row, col + 2, 'Model', main_heading2)
            sheet.write(row, col + 3, 'License Plate ', main_heading2)
            sheet.write(row, col + 4, 'Model Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Employee Code ', main_heading2)
            sheet.write(row, col + 7, 'Driver name ', main_heading2)
            sheet.write(row, col + 8, 'Document Type', main_heading2)
            sheet.write(row, col + 9, 'Domain Name ', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status ', main_heading2)
            sheet.write(row, col + 11, 'Issue Date', main_heading2)
            sheet.write(row, col + 12, 'Issue Date Hijri', main_heading2)
            sheet.write(row, col + 13, 'Expiry Date ', main_heading2)
            sheet.write(row, col + 14, 'Expiry Date Hijri', main_heading2)
            sheet.write(row, col + 15, 'No. Of Days', main_heading2)
            sheet.write(row, col + 16, 'Created By', main_heading2)
            sheet.write(row, col + 17, 'Renewal License date', main_heading2)
            sheet.write(row, col + 18, 'Renewal License Hijri date', main_heading2)
            sheet.write(row, col + 19, 'last update by', main_heading2)
            sheet.write(row, col + 20, 'last update on', main_heading2)
            row += 1
            grand_total = 0
            vehicle_type_list = []
            doc_ids = sorted(rec_ids, key=lambda r: (
            r.document_id.vehicle_type, r.document_id, r.document_type_id.document_type_id))
            for doc_id in doc_ids:
                if doc_id:
                    if doc_id.document_id.vehicle_type.vehicle_type_name not in vehicle_type_list:
                        vehicle_type_list.append(doc_id.document_id.vehicle_type.vehicle_type_name)
            for vehicle_type_id in vehicle_type_list:
                if vehicle_type_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Type', main_heading2)
                    sheet.write_string(row, col + 1, str(vehicle_type_id), main_heading)
                    sheet.write(row, col + 2, 'نوع الشاحنة', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        if doc_id:
                            if doc_id.document_id.vehicle_type.vehicle_type_name == vehicle_type_id:
                                if doc_id.expiry_date:
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                else:
                                    days = 0
                                    hijri_expiry_date = None

                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                       main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_type_id.document_type_id:
                                    sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                                if doc_id.create_uid.name:
                                    sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي ', main_heading2)
                    grand_total += total
                    row += 1
            filtered_doc_ids = rec_ids.filtered(lambda r: not r.document_id.vehicle_type)
            doc_ids = sorted(filtered_doc_ids, key=lambda r: (
            r.document_id.vehicle_type, r.document_id, r.document_type_id.document_type_id))
            if doc_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Type', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'نوع الشاحنة', main_heading2)
                row += 1
                for doc_id in doc_ids:
                    if doc_id:
                        if doc_id.expiry_date:
                            hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                            delta = doc_id.expiry_date - date.today()
                            days = int(delta.days)
                        else:
                            days = 0
                            hijri_expiry_date = None

                        if doc_id.issue_date:
                            hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                        else:
                            hijri_issue_date = None
                        if doc_id.renewel_license_date:
                            renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                        else:
                            renewel_license_hijri_date = None
                        if doc_id.document_id.taq_number:
                            sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                        if doc_id.document_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                               main_heading)
                        if doc_id.document_id.model_id.name:
                            sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                        if doc_id.document_id.license_plate:
                            sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                        if doc_id.document_id.model_year:
                            sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                        if doc_id.document_id.vin_sn:
                            sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                        if doc_id.document_id.bsg_driver.employee_code:
                            sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                               main_heading)
                        if doc_id.document_id.bsg_driver.name:
                            sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                        if doc_id.document_type_id.document_type_id:
                            sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                               main_heading)
                        if doc_id.document_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if doc_id.document_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                               main_heading)
                        if doc_id.issue_date:
                            sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                            sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                        if doc_id.expiry_date:
                            sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if hijri_expiry_date:
                            sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                        if doc_id.create_uid.name:
                            sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                        if doc_id.renewel_license_date:
                            sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                        if renewel_license_hijri_date:
                            sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                        if doc_id.write_uid.name:
                            sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                        if doc_id.last_update_date:
                            sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
                        total += 1
                        row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total), main_heading)
                sheet.write(row, col + 2, 'الاجمالي ', main_heading2)
                grand_total += total
                row += 1
            sheet.write(row, col, 'Grand Total', main_heading2)
            sheet.write_string(row, col + 1, str(grand_total), main_heading)
            sheet.write(row, col + 2, 'الاجمالي الكلي', main_heading2)
        if docs.grouping_by == 'vehicle_domain_name':
            self.env.ref(
                'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Vehicle Domain Name"
            sheet.write(row, col + 7, 'تقرير وثائق الشاحنات بحسب القطاع', main_heading3)
            row += 1
            sheet.write(row, col + 7, 'Vehicle Document Reports Grouping By Domain Name	', main_heading3)
            row += 2
            sheet.write(row, col, 'Print ON', main_heading2)
            sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
            sheet.write(row, col + 1, 'الماركة', main_heading2)
            sheet.write(row, col + 2, 'الموديل', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
            sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
            sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 8, 'نوع المستند', main_heading2)
            sheet.write(row, col + 9, 'نوع الشاحنة', main_heading2)
            sheet.write(row, col + 10, 'الحاله ', main_heading2)
            sheet.write(row, col + 11, 'تاريخ الإصدار', main_heading2)
            sheet.write(row, col + 12, 'تاريخ الإصدار هجري', main_heading2)
            sheet.write(row, col + 13, 'تاريخ الانتهاء ', main_heading2)
            sheet.write(row, col + 14, 'تاريخ الانتهاء هجري', main_heading2)
            sheet.write(row, col + 15, 'عدد الايام ', main_heading2)
            sheet.write(row, col + 16, 'انشأ من قبل ', main_heading2)
            sheet.write(row, col + 17, 'تاريخ تجديد الوثيقة', main_heading2)
            sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة هجري', main_heading2)
            sheet.write(row, col + 19, 'تعديل من قبل', main_heading2)
            sheet.write(row, col + 20, 'تاريخ آخر تعديل', main_heading2)
            row += 1
            sheet.write(row, col, 'Sticker No ', main_heading2)
            sheet.write(row, col + 1, 'Make', main_heading2)
            sheet.write(row, col + 2, 'Model', main_heading2)
            sheet.write(row, col + 3, 'License Plate ', main_heading2)
            sheet.write(row, col + 4, 'Model Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Employee Code ', main_heading2)
            sheet.write(row, col + 7, 'Driver name ', main_heading2)
            sheet.write(row, col + 8, 'Document Type', main_heading2)
            sheet.write(row, col + 9, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Status ', main_heading2)
            sheet.write(row, col + 11, 'Issue Date', main_heading2)
            sheet.write(row, col + 12, 'Issue Date Hijri', main_heading2)
            sheet.write(row, col + 13, 'Expiry Date ', main_heading2)
            sheet.write(row, col + 14, 'Expiry Date Hijri', main_heading2)
            sheet.write(row, col + 15, 'No. Of Days', main_heading2)
            sheet.write(row, col + 16, 'Created By', main_heading2)
            sheet.write(row, col + 17, 'Renewal License date', main_heading2)
            sheet.write(row, col + 18, 'Renewal License Hijri date', main_heading2)
            sheet.write(row, col + 19, 'last update by', main_heading2)
            sheet.write(row, col + 20, 'last update on', main_heading2)
            row += 1
            vehicle_domain_list = []
            grand_total = 0
            doc_ids = sorted(rec_ids, key=lambda r: (
            r.document_id.vehicle_type.domain_name, r.document_id, r.document_type_id.document_type_id))
            for doc_id in doc_ids:
                if doc_id:
                    if doc_id.document_id.vehicle_type.domain_name.name not in vehicle_domain_list:
                        vehicle_domain_list.append(doc_id.document_id.vehicle_type.domain_name.name)
            for vehicle_domain_id in vehicle_domain_list:
                if vehicle_domain_id:
                    total = 0
                    sheet.write(row, col, 'Domain Name', main_heading2)
                    sheet.write_string(row, col + 1, str(vehicle_domain_id), main_heading)
                    sheet.write(row, col + 2, 'اسم النطاق', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        if doc_id:
                            if doc_id.document_id.vehicle_type.domain_name.name == vehicle_domain_id:
                                if doc_id.expiry_date:
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                else:
                                    days = 0
                                    hijri_expiry_date = None

                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                       main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_type_id.document_type_id:
                                    sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                                if doc_id.create_uid.name:
                                    sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
            filtered_doc_ids = rec_ids.filtered(lambda r: not r.document_id.vehicle_type.domain_name)
            doc_ids = sorted(filtered_doc_ids, key=lambda r: (
            r.document_id.vehicle_type.domain_name, r.document_id, r.document_type_id.document_type_id))
            if doc_ids:
                total = 0
                sheet.write(row, col, 'Domain Name', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'اسم النطاق', main_heading2)
                row += 1
                for doc_id in doc_ids:
                    if doc_id:
                        if doc_id.expiry_date:
                            hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                            delta = doc_id.expiry_date - date.today()
                            days = int(delta.days)
                        else:
                            days = 0
                            hijri_expiry_date = None

                        if doc_id.issue_date:
                            hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                        else:
                            hijri_issue_date = None
                        if doc_id.renewel_license_date:
                            renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                        else:
                            renewel_license_hijri_date = None
                        if doc_id.document_id.taq_number:
                            sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                        if doc_id.document_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                               main_heading)
                        if doc_id.document_id.model_id.name:
                            sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                        if doc_id.document_id.license_plate:
                            sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                        if doc_id.document_id.model_year:
                            sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                        if doc_id.document_id.vin_sn:
                            sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                        if doc_id.document_id.bsg_driver.employee_code:
                            sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                               main_heading)
                        if doc_id.document_id.bsg_driver.name:
                            sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                        if doc_id.document_type_id.document_type_id:
                            sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                               main_heading)
                        if doc_id.document_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if doc_id.document_id.vehicle_status.vehicle_status_name:
                            sheet.write_string(row, col + 10,
                                               str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                               main_heading)
                        if doc_id.issue_date:
                            sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                            sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                        if doc_id.expiry_date:
                            sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if hijri_expiry_date:
                            sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                        if doc_id.create_uid.name:
                            sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                        if doc_id.renewel_license_date:
                            sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                        if renewel_license_hijri_date:
                            sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                        if doc_id.write_uid.name:
                            sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                        if doc_id.last_update_date:
                            sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
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
        if docs.grouping_by == 'vehicle_status':
            self.env.ref(
                'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Vehicle Status"
            sheet.write(row, col + 7, 'تقرير وثائق الشاحنات بحسب الحاله الشاحنة ', main_heading3)
            row += 1
            sheet.write(row, col + 7, 'Vehicle Document Reports Grouping By Vehicle State', main_heading3)
            row += 2
            sheet.write(row, col, 'Print ON', main_heading2)
            sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
            sheet.write(row, col + 1, 'الماركة', main_heading2)
            sheet.write(row, col + 2, 'الموديل', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
            sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
            sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 8, 'نوع المستند', main_heading2)
            sheet.write(row, col + 9, 'القطاع ', main_heading2)
            sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'تاريخ الإصدار', main_heading2)
            sheet.write(row, col + 12, 'تاريخ الإصدار هجري', main_heading2)
            sheet.write(row, col + 13, 'تاريخ الانتهاء ', main_heading2)
            sheet.write(row, col + 14, 'تاريخ الانتهاء هجري', main_heading2)
            sheet.write(row, col + 15, 'عدد الايام ', main_heading2)
            sheet.write(row, col + 16, 'انشأ من قبل ', main_heading2)
            sheet.write(row, col + 17, 'تاريخ تجديد الوثيقة', main_heading2)
            sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة هجري', main_heading2)
            sheet.write(row, col + 19, 'تعديل من قبل', main_heading2)
            sheet.write(row, col + 20, 'تاريخ آخر تعديل', main_heading2)
            row += 1
            sheet.write(row, col, 'Sticker No ', main_heading2)
            sheet.write(row, col + 1, 'Make', main_heading2)
            sheet.write(row, col + 2, 'Model', main_heading2)
            sheet.write(row, col + 3, 'License Plate ', main_heading2)
            sheet.write(row, col + 4, 'Model Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Employee Code ', main_heading2)
            sheet.write(row, col + 7, 'Driver name ', main_heading2)
            sheet.write(row, col + 8, 'Document Type', main_heading2)
            sheet.write(row, col + 9, 'Domain Name ', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 11, 'Issue Date', main_heading2)
            sheet.write(row, col + 12, 'Issue Date Hijri', main_heading2)
            sheet.write(row, col + 13, 'Expiry Date ', main_heading2)
            sheet.write(row, col + 14, 'Expiry Date Hijri', main_heading2)
            sheet.write(row, col + 15, 'No. Of Days', main_heading2)
            sheet.write(row, col + 16, 'Created By', main_heading2)
            sheet.write(row, col + 17, 'Renewal License date', main_heading2)
            sheet.write(row, col + 18, 'Renewal License Hijri date', main_heading2)
            sheet.write(row, col + 19, 'last update by', main_heading2)
            sheet.write(row, col + 20, 'last update on', main_heading2)
            row += 1
            vehicle_status_list = []
            grand_total = 0
            doc_ids = sorted(rec_ids, key=lambda r: (
            r.document_id.vehicle_status, r.document_id, r.document_type_id.document_type_id))
            for doc_id in doc_ids:
                if doc_id:
                    if doc_id.document_id.vehicle_status.vehicle_status_name not in vehicle_status_list:
                        vehicle_status_list.append(doc_id.document_id.vehicle_status.vehicle_status_name)
            for vehicle_status_id in vehicle_status_list:
                if vehicle_status_id:
                    total = 0
                    sheet.write(row, col, 'Vehicle Status', main_heading2)
                    sheet.write_string(row, col + 1, str(vehicle_status_id), main_heading)
                    sheet.write(row, col + 2, 'حالة المركبة', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        if doc_id:
                            if doc_id.document_id.vehicle_status.vehicle_status_name == vehicle_status_id:
                                if doc_id.expiry_date:
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                else:
                                    days = 0
                                    hijri_expiry_date = None

                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                       main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_type_id.document_type_id:
                                    sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 15, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                                if doc_id.create_uid.name:
                                    sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
                                total += 1
                                row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
            filtered_doc_ids = rec_ids.filtered(lambda r: not r.document_id.vehicle_status)
            doc_ids = sorted(filtered_doc_ids, key=lambda r: (
            r.document_id.vehicle_status, r.document_id, r.document_type_id.document_type_id))
            if doc_ids:
                total = 0
                sheet.write(row, col, 'Vehicle Status', main_heading2)
                sheet.write_string(row, col + 1, 'Undefined', main_heading)
                sheet.write(row, col + 2, 'حالة المركبة', main_heading2)
                row += 1
                for doc_id in doc_ids:
                    if doc_id:
                        if doc_id.expiry_date:
                            hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                            delta = doc_id.expiry_date - date.today()
                            days = int(delta.days)
                        else:
                            days = 0
                            hijri_expiry_date = None

                        if doc_id.issue_date:
                            hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                        else:
                            hijri_issue_date = None
                        if doc_id.renewel_license_date:
                            renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                        else:
                            renewel_license_hijri_date = None
                        if doc_id.document_id.taq_number:
                            sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                        if doc_id.document_id.model_id.brand_id.name:
                            sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                               main_heading)
                        if doc_id.document_id.model_id.name:
                            sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                        if doc_id.document_id.license_plate:
                            sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                        if doc_id.document_id.model_year:
                            sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                        if doc_id.document_id.vin_sn:
                            sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                        if doc_id.document_id.bsg_driver.employee_code:
                            sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                               main_heading)
                        if doc_id.document_id.bsg_driver.name:
                            sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                        if doc_id.document_type_id.document_type_id:
                            sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                               main_heading)
                        if doc_id.document_id.vehicle_type.domain_name.name:
                            sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.domain_name.name),
                                               main_heading)
                        if doc_id.document_id.vehicle_type.vehicle_type_name:
                            sheet.write_string(row, col + 10,
                                               str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                               main_heading)
                        if doc_id.issue_date:
                            sheet.write_string(row, col + 11, str(doc_id.issue_date), main_heading)
                            sheet.write_string(row, col + 12, str(hijri_issue_date), main_heading)
                        if doc_id.expiry_date:
                            sheet.write_string(row, col + 13, str(doc_id.expiry_date), main_heading)
                            sheet.write_string(row, col + 15, str(days), main_heading)
                        if hijri_expiry_date:
                            sheet.write_string(row, col + 14, str(hijri_expiry_date), main_heading)
                        if doc_id.create_uid.name:
                            sheet.write_string(row, col + 16, str(doc_id.create_uid.name), main_heading)
                        if doc_id.renewel_license_date:
                            sheet.write_string(row, col + 17, str(doc_id.renewel_license_date), main_heading)
                        if renewel_license_hijri_date:
                            sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                        if doc_id.write_uid.name:
                            sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                        if doc_id.last_update_date:
                            sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
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
        if docs.grouping_by == 'document_expiry_date':
            doc_ids = sorted(rec_ids,
                             key=lambda r: (str(r.expiry_date), r.document_id, r.document_type_id.document_type_id))
            doc_ids_with_no_expiry = rec_ids.filtered(lambda r: not r.expiry_date)
            doc_ids_with_no_expiry_sorted = sorted(doc_ids_with_no_expiry, key=lambda r: (
            str(r.expiry_date), r.document_id, r.document_type_id.document_type_id))
            if not docs.period_grouping_by:
                self.env.ref(
                    'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Documents Expiry Date Period Group By Date"
                sheet.merge_range('A1:Q1', 'تقرير وثائق الشاحنات بحسب(تاريخ)', main_heading3)
                sheet.merge_range('A2:Q2', 'Vehicle Document Reports Grouping By Period (Date)', main_heading3)
                row = 2
                sheet.write(row, col, 'Print ON', main_heading2)
                sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
                row += 1
                sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
                sheet.write(row, col + 1, 'الماركة', main_heading2)
                sheet.write(row, col + 2, 'الموديل', main_heading2)
                sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
                sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
                sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
                sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
                sheet.write(row, col + 8, 'نوع المستند', main_heading2)
                sheet.write(row, col + 9, 'القطاع ', main_heading2)
                sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
                sheet.write(row, col + 11, 'الحاله ', main_heading2)
                sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
                sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
                sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
                sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
                sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
                sheet.write(row, col + 17, 'انشأ من قبل ', main_heading2)
                sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة', main_heading2)
                sheet.write(row, col + 19, 'تاريخ تجديد الوثيقة هجري', main_heading2)
                sheet.write(row, col + 20, 'تعديل من قبل', main_heading2)
                sheet.write(row, col + 21, 'تاريخ آخر تعديل', main_heading2)
                row += 1
                sheet.write(row, col, 'Sticker No ', main_heading2)
                sheet.write(row, col + 1, 'Make', main_heading2)
                sheet.write(row, col + 2, 'Model', main_heading2)
                sheet.write(row, col + 3, 'License Plate ', main_heading2)
                sheet.write(row, col + 4, 'Model Year', main_heading2)
                sheet.write(row, col + 5, 'Chassis Number', main_heading2)
                sheet.write(row, col + 6, 'Employee Code ', main_heading2)
                sheet.write(row, col + 7, 'Driver name ', main_heading2)
                sheet.write(row, col + 8, 'Document Type', main_heading2)
                sheet.write(row, col + 9, 'Domain Name ', main_heading2)
                sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
                sheet.write(row, col + 12, 'Issue Date', main_heading2)
                sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
                sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
                sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
                sheet.write(row, col + 16, 'No. Of Days', main_heading2)
                sheet.write(row, col + 17, 'Created By', main_heading2)
                sheet.write(row, col + 18, 'Renewal License date', main_heading2)
                sheet.write(row, col + 19, 'Renewal License Hijri date', main_heading2)
                sheet.write(row, col + 20, 'last update by', main_heading2)
                sheet.write(row, col + 21, 'last update on', main_heading2)
                row += 1
                date_list = []
                grand_total = 0
                for doc_id in doc_ids:
                    if doc_id:
                        if doc_id.expiry_date not in date_list:
                            date_list.append(doc_id.expiry_date)
                for date_id in date_list:
                    if date_id:
                        total = 0
                        sheet.write(row, col, 'Date', main_heading2)
                        sheet.write_string(row, col + 1, str(date_id), main_heading)
                        sheet.write(row, col + 2, 'تاريخ', main_heading2)
                        row += 1
                        for doc_id in doc_ids:
                            if doc_id:
                                if doc_id.expiry_date == date_id:
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                    if doc_id.issue_date:
                                        hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                    else:
                                        hijri_issue_date = None
                                    if doc_id.renewel_license_date:
                                        renewel_license_hijri_date = HijriDate.get_hijri_date(
                                            doc_id.renewel_license_date)
                                    else:
                                        renewel_license_hijri_date = None
                                    if doc_id.document_id.taq_number:
                                        sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                    if doc_id.document_id.model_id.brand_id.name:
                                        sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                           main_heading)
                                    if doc_id.document_id.model_id.name:
                                        sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                           main_heading)
                                    if doc_id.document_id.license_plate:
                                        sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                           main_heading)
                                    if doc_id.document_id.model_year:
                                        sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                           main_heading)
                                    if doc_id.document_id.vin_sn:
                                        sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                    if doc_id.document_id.bsg_driver.employee_code:
                                        sheet.write_string(row, col + 6,
                                                           str(doc_id.document_id.bsg_driver.employee_code),
                                                           main_heading)
                                    if doc_id.document_id.bsg_driver.name:
                                        sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                           main_heading)
                                    if doc_id.document_type_id.document_type_id:
                                        sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                           main_heading)
                                    if doc_id.document_id.vehicle_type.domain_name.name:
                                        sheet.write_string(row, col + 9,
                                                           str(doc_id.document_id.vehicle_type.domain_name.name),
                                                           main_heading)
                                    if doc_id.document_id.vehicle_type.vehicle_type_name:
                                        sheet.write_string(row, col + 10,
                                                           str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                           main_heading)
                                    if doc_id.document_id.vehicle_status.vehicle_status_name:
                                        sheet.write_string(row, col + 11,
                                                           str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                           main_heading)
                                    if doc_id.issue_date:
                                        sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                        sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                                    if doc_id.expiry_date:
                                        sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                        sheet.write_string(row, col + 16, str(days), main_heading)
                                    if hijri_expiry_date:
                                        sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                                    if doc_id.create_uid.name:
                                        sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                                    if doc_id.renewel_license_date:
                                        sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                           main_heading)
                                    if renewel_license_hijri_date:
                                        sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                                    if doc_id.write_uid.name:
                                        sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                                    if doc_id.last_update_date:
                                        sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                                    total += 1
                                    row += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        grand_total += total
                        row += 1
                if doc_ids_with_no_expiry_sorted:
                    total = 0
                    sheet.write(row, col, 'Date', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'تاريخ', main_heading2)
                    row += 1
                    for doc_id in doc_ids_with_no_expiry_sorted:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None
                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                   main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                   main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                   main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6,
                                                   str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                   main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9,
                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
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
                    'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Documents Expiry Date Period Group By Year"
                sheet.merge_range('A1:Q1', 'تقرير وثائق الشاحنات بحسب(سنوي)', main_heading3)
                sheet.merge_range('A2:Q2', 'Vehicle Document Reports Grouping By Period (year)', main_heading3)
                row = 2
                sheet.write(row, col, 'Print ON', main_heading2)
                sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
                row += 1
                sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
                sheet.write(row, col + 1, 'الماركة', main_heading2)
                sheet.write(row, col + 2, 'الموديل', main_heading2)
                sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
                sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
                sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
                sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
                sheet.write(row, col + 8, 'نوع المستند', main_heading2)
                sheet.write(row, col + 9, 'القطاع ', main_heading2)
                sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
                sheet.write(row, col + 11, 'الحاله ', main_heading2)
                sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
                sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
                sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
                sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
                sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
                sheet.write(row, col + 17, 'انشأ من قبل ', main_heading2)
                sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة', main_heading2)
                sheet.write(row, col + 19, 'تاريخ تجديد الوثيقة هجري', main_heading2)
                sheet.write(row, col + 20, 'تعديل من قبل', main_heading2)
                sheet.write(row, col + 21, 'تاريخ آخر تعديل', main_heading2)
                row += 1
                sheet.write(row, col, 'Sticker No ', main_heading2)
                sheet.write(row, col + 1, 'Make', main_heading2)
                sheet.write(row, col + 2, 'Model', main_heading2)
                sheet.write(row, col + 3, 'License Plate ', main_heading2)
                sheet.write(row, col + 4, 'Model Year', main_heading2)
                sheet.write(row, col + 5, 'Chassis Number', main_heading2)
                sheet.write(row, col + 6, 'Employee Code ', main_heading2)
                sheet.write(row, col + 7, 'Driver name ', main_heading2)
                sheet.write(row, col + 8, 'Document Type', main_heading2)
                sheet.write(row, col + 9, 'Domain Name ', main_heading2)
                sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
                sheet.write(row, col + 12, 'Issue Date', main_heading2)
                sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
                sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
                sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
                sheet.write(row, col + 16, 'No. Of Days', main_heading2)
                sheet.write(row, col + 17, 'Created By', main_heading2)
                sheet.write(row, col + 18, 'Renewal License date', main_heading2)
                sheet.write(row, col + 19, 'Renewal License Hijri date', main_heading2)
                sheet.write(row, col + 20, 'last update by', main_heading2)
                sheet.write(row, col + 21, 'last update on', main_heading2)
                row += 1
                years_list = []
                grand_total = 0
                for doc_id in doc_ids:
                    if doc_id.expiry_date:
                        if doc_id.expiry_date.year not in years_list:
                            years_list.append(doc_id.expiry_date.year)
                for year in years_list:
                    total = 0
                    sheet.write(row, col, 'Year', main_heading2)
                    sheet.write_string(row, col + 1, str(year), main_heading)
                    sheet.write(row, col + 2, 'عام', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        days = 0
                        if doc_id.expiry_date:
                            if year == doc_id.expiry_date.year:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                       main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_type_id.document_type_id:
                                    sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 16, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                                if doc_id.create_uid.name:
                                    sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                       main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                                total += 1
                                row += 1
                    row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if doc_ids_with_no_expiry_sorted:
                    total = 0
                    sheet.write(row, col, 'Year', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'عام', main_heading2)
                    row += 1
                    for doc_id in doc_ids_with_no_expiry_sorted:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None
                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                   main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                   main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                   main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6,
                                                   str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                   main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9,
                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
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
                    'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Documents Expiry Date Period Group By Month"
                sheet.merge_range('A1:Q1', 'تقرير وثائق الشاحنات بحسب(الشهر)', main_heading3)
                sheet.merge_range('A2:Q2', 'Vehicle Document Reports Grouping By Period (Month)', main_heading3)
                row = 2
                sheet.write(row, col, 'Print ON', main_heading2)
                sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
                row += 1
                sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
                sheet.write(row, col + 1, 'الماركة', main_heading2)
                sheet.write(row, col + 2, 'الموديل', main_heading2)
                sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
                sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
                sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
                sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
                sheet.write(row, col + 8, 'نوع المستند', main_heading2)
                sheet.write(row, col + 9, 'القطاع ', main_heading2)
                sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
                sheet.write(row, col + 11, 'الحاله ', main_heading2)
                sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
                sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
                sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
                sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
                sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
                sheet.write(row, col + 17, 'انشأ من قبل ', main_heading2)
                sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة', main_heading2)
                sheet.write(row, col + 19, 'تاريخ تجديد الوثيقة هجري', main_heading2)
                sheet.write(row, col + 20, 'تعديل من قبل', main_heading2)
                sheet.write(row, col + 21, 'تاريخ آخر تعديل', main_heading2)
                row += 1
                sheet.write(row, col, 'Sticker No ', main_heading2)
                sheet.write(row, col + 1, 'Make', main_heading2)
                sheet.write(row, col + 2, 'Model', main_heading2)
                sheet.write(row, col + 3, 'License Plate ', main_heading2)
                sheet.write(row, col + 4, 'Model Year', main_heading2)
                sheet.write(row, col + 5, 'Chassis Number', main_heading2)
                sheet.write(row, col + 6, 'Employee Code ', main_heading2)
                sheet.write(row, col + 7, 'Driver name ', main_heading2)
                sheet.write(row, col + 8, 'Document Type', main_heading2)
                sheet.write(row, col + 9, 'Domain Name ', main_heading2)
                sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
                sheet.write(row, col + 12, 'Issue Date', main_heading2)
                sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
                sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
                sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
                sheet.write(row, col + 16, 'No. Of Days', main_heading2)
                sheet.write(row, col + 17, 'Created By', main_heading2)
                sheet.write(row, col + 18, 'Renewal License date', main_heading2)
                sheet.write(row, col + 19, 'Renewal License Hijri date', main_heading2)
                sheet.write(row, col + 20, 'last update by', main_heading2)
                sheet.write(row, col + 21, 'last update on', main_heading2)
                row += 1
                months_list = []
                grand_total = 0
                for doc_id in doc_ids:
                    if doc_id.expiry_date:
                        if doc_id.expiry_date.strftime('%B') not in months_list:
                            months_list.append(doc_id.expiry_date.strftime('%B'))
                for month in months_list:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, str(month), main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        if doc_id.expiry_date:
                            days = 0
                            if month == doc_id.expiry_date.strftime('%B'):
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                       main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_type_id.document_type_id:
                                    sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 16, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                                if doc_id.create_uid.name:
                                    sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                       main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                                total += 1
                                row += 1
                    row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if doc_ids_with_no_expiry_sorted:
                    total = 0
                    sheet.write(row, col, 'Month', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'شهر', main_heading2)
                    row += 1
                    for doc_id in doc_ids_with_no_expiry_sorted:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None
                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                   main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                   main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                   main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6,
                                                   str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                   main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9,
                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
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
                    'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Documents Expiry Date Period Group By Day"
                sheet.merge_range('A1:Q1', 'تقرير وثائق الشاحنات بحسب(اليوم)',
                                  main_heading3)
                sheet.merge_range('A2:Q2',
                                  'Vehicle Document Reports Grouping By Period (Day)',
                                  main_heading3)
                row = 2
                sheet.write(row, col, 'Print ON', main_heading2)
                sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
                row += 1
                sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
                sheet.write(row, col + 1, 'الماركة', main_heading2)
                sheet.write(row, col + 2, 'الموديل', main_heading2)
                sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
                sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
                sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
                sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
                sheet.write(row, col + 8, 'نوع المستند', main_heading2)
                sheet.write(row, col + 9, 'القطاع ', main_heading2)
                sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
                sheet.write(row, col + 11, 'الحاله ', main_heading2)
                sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
                sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
                sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
                sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
                sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
                sheet.write(row, col + 17, 'انشأ من قبل ', main_heading2)
                sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة', main_heading2)
                sheet.write(row, col + 19, 'تاريخ تجديد الوثيقة هجري', main_heading2)
                sheet.write(row, col + 20, 'تعديل من قبل', main_heading2)
                sheet.write(row, col + 21, 'تاريخ آخر تعديل', main_heading2)
                row += 1
                sheet.write(row, col, 'Sticker No ', main_heading2)
                sheet.write(row, col + 1, 'Make', main_heading2)
                sheet.write(row, col + 2, 'Model', main_heading2)
                sheet.write(row, col + 3, 'License Plate ', main_heading2)
                sheet.write(row, col + 4, 'Model Year', main_heading2)
                sheet.write(row, col + 5, 'Chassis Number', main_heading2)
                sheet.write(row, col + 6, 'Employee Code ', main_heading2)
                sheet.write(row, col + 7, 'Driver name ', main_heading2)
                sheet.write(row, col + 8, 'Document Type', main_heading2)
                sheet.write(row, col + 9, 'Domain Name ', main_heading2)
                sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
                sheet.write(row, col + 12, 'Issue Date', main_heading2)
                sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
                sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
                sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
                sheet.write(row, col + 16, 'No. Of Days', main_heading2)
                sheet.write(row, col + 17, 'Created By', main_heading2)
                sheet.write(row, col + 18, 'Renewal License date', main_heading2)
                sheet.write(row, col + 19, 'Renewal License Hijri date', main_heading2)
                sheet.write(row, col + 20, 'last update by', main_heading2)
                sheet.write(row, col + 21, 'last update on', main_heading2)
                row += 1
                days_list = []
                grand_total = 0
                day_name = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
                for doc_id in doc_ids:
                    if doc_id.expiry_date:
                        day = doc_id.expiry_date.weekday()
                        if day not in days_list:
                            days_list.append(day)
                for day_id in days_list:
                    total = 0
                    sheet.write(row, col, 'Day', main_heading2)
                    sheet.write_string(row, col + 1, str(day_name[day_id]), main_heading)
                    sheet.write(row, col + 2, 'يوم', main_heading2)
                    row += 1
                    filtered_doc_ids = rec_ids.filtered(lambda r: r.expiry_date and r.expiry_date.weekday() == day_id)
                    sorted_doc_ids = sorted(filtered_doc_ids, key=lambda r: (
                    str(r.expiry_date), r.document_id, r.document_type_id.document_type_id))
                    for doc_id in sorted_doc_ids:
                        days = 0
                        if doc_id.issue_date:
                            hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                        else:
                            hijri_issue_date = None
                        if doc_id.renewel_license_date:
                            renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                        else:
                            renewel_license_hijri_date = None
                        if doc_id.expiry_date:
                            hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                            delta = doc_id.expiry_date - date.today()
                            days = int(delta.days)
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                   main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                   main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                   main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9,
                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                            total += 1
                            row += 1
                    row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if doc_ids_with_no_expiry_sorted:
                    total = 0
                    sheet.write(row, col, 'Day', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'يوم', main_heading2)
                    row += 1
                    for doc_id in doc_ids_with_no_expiry_sorted:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None
                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                   main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                   main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                   main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6,
                                                   str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                   main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9,
                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
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
                    'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Documents Expiry Date Period Group By Qaurterly"
                sheet.merge_range('A1:Q1', 'تقرير وثائق الشاحنات بحسب(ربع سنوي)',
                                  main_heading3)
                sheet.merge_range('A2:Q2',
                                  'Vehicle Document Reports Grouping By Period (Quarters)',
                                  main_heading3)
                row = 2
                sheet.write(row, col, 'Print ON', main_heading2)
                sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
                row += 1
                sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
                sheet.write(row, col + 1, 'الماركة', main_heading2)
                sheet.write(row, col + 2, 'الموديل', main_heading2)
                sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
                sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
                sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
                sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
                sheet.write(row, col + 8, 'نوع المستند', main_heading2)
                sheet.write(row, col + 9, 'القطاع ', main_heading2)
                sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
                sheet.write(row, col + 11, 'الحاله ', main_heading2)
                sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
                sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
                sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
                sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
                sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
                sheet.write(row, col + 17, 'انشأ من قبل ', main_heading2)
                sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة', main_heading2)
                sheet.write(row, col + 19, 'تاريخ تجديد الوثيقة هجري', main_heading2)
                sheet.write(row, col + 20, 'تعديل من قبل', main_heading2)
                sheet.write(row, col + 21, 'تاريخ آخر تعديل', main_heading2)
                row += 1
                sheet.write(row, col, 'Sticker No ', main_heading2)
                sheet.write(row, col + 1, 'Make', main_heading2)
                sheet.write(row, col + 2, 'Model', main_heading2)
                sheet.write(row, col + 3, 'License Plate ', main_heading2)
                sheet.write(row, col + 4, 'Model Year', main_heading2)
                sheet.write(row, col + 5, 'Chassis Number', main_heading2)
                sheet.write(row, col + 6, 'Employee Code ', main_heading2)
                sheet.write(row, col + 7, 'Driver name ', main_heading2)
                sheet.write(row, col + 8, 'Document Type', main_heading2)
                sheet.write(row, col + 9, 'Domain Name ', main_heading2)
                sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
                sheet.write(row, col + 12, 'Issue Date', main_heading2)
                sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
                sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
                sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
                sheet.write(row, col + 16, 'No. Of Days', main_heading2)
                sheet.write(row, col + 17, 'Created By', main_heading2)
                sheet.write(row, col + 18, 'Renewal License date', main_heading2)
                sheet.write(row, col + 19, 'Renewal License Hijri date', main_heading2)
                sheet.write(row, col + 20, 'last update by', main_heading2)
                sheet.write(row, col + 21, 'last update on', main_heading2)
                row += 1
                first_quarter = ['January', 'February', 'March']
                second_quarter = ['April', 'May', 'June']
                third_quarter = ['July', 'August', 'September']
                fourth_quarter = ['October', 'November', 'December']
                first_quarter_ids = rec_ids.filtered(
                    lambda r: (r.expiry_date and r.expiry_date.strftime('%B') in first_quarter))
                second_quarter_ids = rec_ids.filtered(
                    lambda r: (r.expiry_date and r.expiry_date.strftime('%B') in second_quarter))
                third_quarter_ids = rec_ids.filtered(
                    lambda r: (r.expiry_date and r.expiry_date.strftime('%B') in third_quarter))
                fourth_quarter_ids = rec_ids.filtered(
                    lambda r: (r.expiry_date and r.expiry_date.strftime('%B') in fourth_quarter))
                sorted_first_quarter_ids = sorted(first_quarter_ids, key=lambda r: (
                str(r.expiry_date), r.document_id, r.document_type_id.document_type_id))
                sorted_second_quarter_ids = sorted(second_quarter_ids, key=lambda r: (
                str(r.expiry_date), r.document_id, r.document_type_id.document_type_id))
                sorted_third_quarter_ids = sorted(third_quarter_ids, key=lambda r: (
                str(r.expiry_date), r.document_id, r.document_type_id.document_type_id))
                sorted_fourth_quarter_ids = sorted(fourth_quarter_ids, key=lambda r: (
                str(r.expiry_date), r.document_id, r.document_type_id.document_type_id))
                grand_total = 0
                if sorted_first_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'First', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for doc_id in sorted_first_quarter_ids:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None

                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name), main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                            total += 1
                            row += 1
                    row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if sorted_second_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Second', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for doc_id in sorted_second_quarter_ids:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None

                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name), main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                            total += 1
                            row += 1
                    row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if sorted_third_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Third', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for doc_id in sorted_third_quarter_ids:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None

                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name), main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                            total += 1
                            row += 1
                    row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if sorted_fourth_quarter_ids:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Fourth', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for doc_id in sorted_fourth_quarter_ids:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None

                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name), main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate), main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year), main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6, str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name), main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9, str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name), main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
                            total += 1
                            row += 1
                    row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 1, str(total), main_heading)
                    sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                    grand_total += total
                    row += 1
                if doc_ids_with_no_expiry_sorted:
                    total = 0
                    sheet.write(row, col, 'Quarter', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'ربع', main_heading2)
                    row += 1
                    for doc_id in doc_ids_with_no_expiry_sorted:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None
                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                   main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                   main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                   main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6,
                                                   str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                   main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9,
                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
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
                    'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Documents Expiry Date Period Group By Weekly"
                sheet.merge_range('A1:Q1', 'تقرير وثائق الشاحنات بحسب(الأسبوع)',
                                  main_heading3)
                sheet.merge_range('A2:Q2',
                                  'Vehicle Document Reports Grouping By Period (week)',
                                  main_heading3)
                row = 2
                sheet.write(row, col, 'Print ON', main_heading2)
                sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
                row += 1
                sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
                sheet.write(row, col + 1, 'الماركة', main_heading2)
                sheet.write(row, col + 2, 'الموديل', main_heading2)
                sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
                sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
                sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
                sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
                sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
                sheet.write(row, col + 8, 'نوع المستند', main_heading2)
                sheet.write(row, col + 9, 'القطاع ', main_heading2)
                sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
                sheet.write(row, col + 11, 'الحاله ', main_heading2)
                sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
                sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
                sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
                sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
                sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
                sheet.write(row, col + 17, 'انشأ من قبل ', main_heading2)
                sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة', main_heading2)
                sheet.write(row, col + 19, 'تاريخ تجديد الوثيقة هجري', main_heading2)
                sheet.write(row, col + 20, 'تعديل من قبل', main_heading2)
                sheet.write(row, col + 21, 'تاريخ آخر تعديل', main_heading2)
                row += 1
                sheet.write(row, col, 'Sticker No ', main_heading2)
                sheet.write(row, col + 1, 'Make', main_heading2)
                sheet.write(row, col + 2, 'Model', main_heading2)
                sheet.write(row, col + 3, 'License Plate ', main_heading2)
                sheet.write(row, col + 4, 'Model Year', main_heading2)
                sheet.write(row, col + 5, 'Chassis Number', main_heading2)
                sheet.write(row, col + 6, 'Employee Code ', main_heading2)
                sheet.write(row, col + 7, 'Driver name ', main_heading2)
                sheet.write(row, col + 8, 'Document Type', main_heading2)
                sheet.write(row, col + 9, 'Domain Name ', main_heading2)
                sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
                sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
                sheet.write(row, col + 12, 'Issue Date', main_heading2)
                sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
                sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
                sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
                sheet.write(row, col + 16, 'No. Of Days', main_heading2)
                sheet.write(row, col + 17, 'Created By', main_heading2)
                sheet.write(row, col + 18, 'Renewal License date', main_heading2)
                sheet.write(row, col + 19, 'Renewal License Hijri date', main_heading2)
                sheet.write(row, col + 20, 'last update by', main_heading2)
                sheet.write(row, col + 21, 'last update on', main_heading2)
                row += 1
                week_list = []
                grand_total = 0
                for doc_id in doc_ids:
                    if doc_id:
                        if doc_id.expiry_date:
                            year = doc_id.expiry_date.year
                            week = doc_id.expiry_date.strftime("%V")
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
                        for doc_id in doc_ids:
                            if doc_id:
                                days = 0
                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.expiry_date:
                                    doc_year = doc_id.expiry_date.year
                                    doc_week = doc_id.expiry_date.strftime("%V")
                                    doc_year_week = "year %s Week %s" % (doc_year, doc_week)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    if doc_year_week:
                                        if doc_year_week == week:
                                            if doc_id.document_id.taq_number:
                                                sheet.write_string(row, col, str(doc_id.document_id.taq_number),
                                                                   main_heading)
                                            if doc_id.document_id.model_id.brand_id.name:
                                                sheet.write_string(row, col + 1,
                                                                   str(doc_id.document_id.model_id.brand_id.name),
                                                                   main_heading)
                                            if doc_id.document_id.model_id.name:
                                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                                   main_heading)
                                            if doc_id.document_id.license_plate:
                                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                                   main_heading)
                                            if doc_id.document_id.model_year:
                                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                                   main_heading)
                                            if doc_id.document_id.vin_sn:
                                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn),
                                                                   main_heading)
                                            if doc_id.document_id.bsg_driver.employee_code:
                                                sheet.write_string(row, col + 6,
                                                                   str(doc_id.document_id.bsg_driver.employee_code),
                                                                   main_heading)
                                            if doc_id.document_id.bsg_driver.name:
                                                sheet.write_string(row, col + 7,
                                                                   str(doc_id.document_id.bsg_driver.name),
                                                                   main_heading)
                                            if doc_id.document_type_id.document_type_id:
                                                sheet.write_string(row, col + 8,
                                                                   str(doc_id.document_type_id.document_type_id),
                                                                   main_heading)
                                            if doc_id.document_id.vehicle_type.domain_name.name:
                                                sheet.write_string(row, col + 9,
                                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                                   main_heading)
                                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                                sheet.write_string(row, col + 10,
                                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                                   main_heading)
                                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                                sheet.write_string(row, col + 11,
                                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                                   main_heading)
                                            if doc_id.issue_date:
                                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                                            if doc_id.expiry_date:
                                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                                sheet.write_string(row, col + 16, str(days), main_heading)
                                            if hijri_expiry_date:
                                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                                            if doc_id.create_uid.name:
                                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name),
                                                                   main_heading)
                                            if doc_id.renewel_license_date:
                                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                                   main_heading)
                                            if renewel_license_hijri_date:
                                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date),
                                                                   main_heading)
                                            if doc_id.write_uid.name:
                                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name),
                                                                   main_heading)
                                            if doc_id.last_update_date:
                                                sheet.write_string(row, col + 21, str(doc_id.last_update_date),
                                                                   main_heading)
                                            total += 1
                                            row += 1
                        row += 1
                        sheet.write(row, col, 'Total', main_heading2)
                        sheet.write_string(row, col + 1, str(total), main_heading)
                        sheet.write(row, col + 2, 'الاجمالي', main_heading2)
                        grand_total += total
                        row += 1
                if doc_ids_with_no_expiry_sorted:
                    total = 0
                    sheet.write(row, col, 'Week', main_heading2)
                    sheet.write_string(row, col + 1, 'Undefined', main_heading)
                    sheet.write(row, col + 2, 'أسبوع', main_heading2)
                    row += 1
                    for doc_id in doc_ids_with_no_expiry_sorted:
                        if doc_id:
                            if doc_id.expiry_date:
                                hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                delta = doc_id.expiry_date - date.today()
                                days = int(delta.days)
                            else:
                                days = 0
                                hijri_expiry_date = None
                            if doc_id.issue_date:
                                hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                            else:
                                hijri_issue_date = None
                            if doc_id.renewel_license_date:
                                renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                            else:
                                renewel_license_hijri_date = None
                            if doc_id.document_id.taq_number:
                                sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                            if doc_id.document_id.model_id.brand_id.name:
                                sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                   main_heading)
                            if doc_id.document_id.model_id.name:
                                sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                   main_heading)
                            if doc_id.document_id.license_plate:
                                sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                   main_heading)
                            if doc_id.document_id.model_year:
                                sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                   main_heading)
                            if doc_id.document_id.vin_sn:
                                sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                            if doc_id.document_id.bsg_driver.employee_code:
                                sheet.write_string(row, col + 6,
                                                   str(doc_id.document_id.bsg_driver.employee_code),
                                                   main_heading)
                            if doc_id.document_id.bsg_driver.name:
                                sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                   main_heading)
                            if doc_id.document_type_id.document_type_id:
                                sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.domain_name.name:
                                sheet.write_string(row, col + 9,
                                                   str(doc_id.document_id.vehicle_type.domain_name.name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_type.vehicle_type_name:
                                sheet.write_string(row, col + 10,
                                                   str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                   main_heading)
                            if doc_id.document_id.vehicle_status.vehicle_status_name:
                                sheet.write_string(row, col + 11,
                                                   str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                   main_heading)
                            if doc_id.issue_date:
                                sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                            if doc_id.expiry_date:
                                sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                sheet.write_string(row, col + 16, str(days), main_heading)
                            if hijri_expiry_date:
                                sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                            if doc_id.create_uid.name:
                                sheet.write_string(row, col + 17, str(doc_id.create_uid.name), main_heading)
                            if doc_id.renewel_license_date:
                                sheet.write_string(row, col + 18, str(doc_id.renewel_license_date),
                                                   main_heading)
                            if renewel_license_hijri_date:
                                sheet.write_string(row, col + 19, str(renewel_license_hijri_date), main_heading)
                            if doc_id.write_uid.name:
                                sheet.write_string(row, col + 20, str(doc_id.write_uid.name), main_heading)
                            if doc_id.last_update_date:
                                sheet.write_string(row, col + 21, str(doc_id.last_update_date), main_heading)
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
                'bsg_vehicle_documents_reports.vehicle_document_report_xlsx_id').report_file = "Vehicle Documents Report Group By Creator"
            sheet.write(row, col + 7, 'تجميع تقارير وثائق السيارة حسب المنشئ', main_heading3)
            row += 1
            sheet.write(row, col + 7, 'Vehicle Document Reports Grouping By Creator', main_heading3)
            row += 2
            sheet.write(row, col, 'Print ON', main_heading2)
            sheet.write_string(row, col + 1, str(docs.print_date), main_heading)
            row += 1
            sheet.write(row, col, 'رقم الشاحنه ', main_heading2)
            sheet.write(row, col + 1, 'الماركة', main_heading2)
            sheet.write(row, col + 2, 'الموديل', main_heading2)
            sheet.write(row, col + 3, 'رقم اللوحه ', main_heading2)
            sheet.write(row, col + 4, 'سنة الصنع', main_heading2)
            sheet.write(row, col + 5, 'رقم الهيكل ', main_heading2)
            sheet.write(row, col + 6, 'كمبيوتر السائق ', main_heading2)
            sheet.write(row, col + 7, 'اسم السائق ', main_heading2)
            sheet.write(row, col + 8, 'نوع المستند', main_heading2)
            sheet.write(row, col + 9, 'القطاع ', main_heading2)
            sheet.write(row, col + 10, 'نوع الشاحنة', main_heading2)
            sheet.write(row, col + 11, 'الحاله ', main_heading2)
            sheet.write(row, col + 12, 'تاريخ الإصدار', main_heading2)
            sheet.write(row, col + 13, 'تاريخ الإصدار هجري', main_heading2)
            sheet.write(row, col + 14, 'تاريخ الانتهاء ', main_heading2)
            sheet.write(row, col + 15, 'تاريخ الانتهاء هجري', main_heading2)
            sheet.write(row, col + 16, 'عدد الايام ', main_heading2)
            sheet.write(row, col + 17, 'تاريخ تجديد الوثيقة', main_heading2)
            sheet.write(row, col + 18, 'تاريخ تجديد الوثيقة هجري', main_heading2)
            sheet.write(row, col + 19, 'تعديل من قبل', main_heading2)
            sheet.write(row, col + 20, 'تاريخ آخر تعديل', main_heading2)
            row += 1
            sheet.write(row, col, 'Sticker No ', main_heading2)
            sheet.write(row, col + 1, 'Make', main_heading2)
            sheet.write(row, col + 2, 'Model', main_heading2)
            sheet.write(row, col + 3, 'License Plate ', main_heading2)
            sheet.write(row, col + 4, 'Model Year', main_heading2)
            sheet.write(row, col + 5, 'Chassis Number', main_heading2)
            sheet.write(row, col + 6, 'Employee Code ', main_heading2)
            sheet.write(row, col + 7, 'Driver name ', main_heading2)
            sheet.write(row, col + 8, 'Document Type', main_heading2)
            sheet.write(row, col + 9, 'Domain Name ', main_heading2)
            sheet.write(row, col + 10, 'Vehicle Type', main_heading2)
            sheet.write(row, col + 11, 'Vehicle Status ', main_heading2)
            sheet.write(row, col + 12, 'Issue Date', main_heading2)
            sheet.write(row, col + 13, 'Issue Date Hijri', main_heading2)
            sheet.write(row, col + 14, 'Expiry Date ', main_heading2)
            sheet.write(row, col + 15, 'Expiry Date Hijri', main_heading2)
            sheet.write(row, col + 16, 'No. Of Days', main_heading2)
            sheet.write(row, col + 17, 'Renewal License date', main_heading2)
            sheet.write(row, col + 18, 'Renewal License Hijri date', main_heading2)
            sheet.write(row, col + 19, 'last update by', main_heading2)
            sheet.write(row, col + 20, 'last update on', main_heading2)
            row += 1
            creator_list = []
            grand_total = 0
            doc_ids = sorted(rec_ids, key=lambda r: (
                r.create_uid, r.document_id, r.document_type_id.document_type_id))
            for doc_id in doc_ids:
                if doc_id:
                    if doc_id.create_uid.name not in creator_list:
                        creator_list.append(doc_id.create_uid.name)
            for create_id in creator_list:
                if create_id:
                    total = 0
                    sheet.write(row, col, 'Creator Name', main_heading2)
                    sheet.write_string(row, col + 1, str(create_id), main_heading)
                    sheet.write(row, col + 2, 'اسم المنشئ', main_heading2)
                    row += 1
                    for doc_id in doc_ids:
                        if doc_id:
                            if doc_id.create_uid.name == create_id:
                                if doc_id.expiry_date:
                                    hijri_expiry_date = HijriDate.get_hijri_date(doc_id.expiry_date)
                                    delta = doc_id.expiry_date - date.today()
                                    days = int(delta.days)
                                else:
                                    days = 0
                                    hijri_expiry_date = None

                                if doc_id.issue_date:
                                    hijri_issue_date = HijriDate.get_hijri_date(doc_id.issue_date)
                                else:
                                    hijri_issue_date = None
                                if doc_id.renewel_license_date:
                                    renewel_license_hijri_date = HijriDate.get_hijri_date(doc_id.renewel_license_date)
                                else:
                                    renewel_license_hijri_date = None
                                if doc_id.document_id.taq_number:
                                    sheet.write_string(row, col, str(doc_id.document_id.taq_number), main_heading)
                                if doc_id.document_id.model_id.brand_id.name:
                                    sheet.write_string(row, col + 1, str(doc_id.document_id.model_id.brand_id.name),
                                                       main_heading)
                                if doc_id.document_id.model_id.name:
                                    sheet.write_string(row, col + 2, str(doc_id.document_id.model_id.name),
                                                       main_heading)
                                if doc_id.document_id.license_plate:
                                    sheet.write_string(row, col + 3, str(doc_id.document_id.license_plate),
                                                       main_heading)
                                if doc_id.document_id.model_year:
                                    sheet.write_string(row, col + 4, str(doc_id.document_id.model_year),
                                                       main_heading)
                                if doc_id.document_id.vin_sn:
                                    sheet.write_string(row, col + 5, str(doc_id.document_id.vin_sn), main_heading)
                                if doc_id.document_id.bsg_driver.employee_code:
                                    sheet.write_string(row, col + 6,
                                                       str(doc_id.document_id.bsg_driver.employee_code),
                                                       main_heading)
                                if doc_id.document_id.bsg_driver.name:
                                    sheet.write_string(row, col + 7, str(doc_id.document_id.bsg_driver.name),
                                                       main_heading)
                                if doc_id.document_type_id.document_type_id:
                                    sheet.write_string(row, col + 8, str(doc_id.document_type_id.document_type_id),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.domain_name.name:
                                    sheet.write_string(row, col + 9,
                                                       str(doc_id.document_id.vehicle_type.domain_name.name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_type.vehicle_type_name:
                                    sheet.write_string(row, col + 10,
                                                       str(doc_id.document_id.vehicle_type.vehicle_type_name),
                                                       main_heading)
                                if doc_id.document_id.vehicle_status.vehicle_status_name:
                                    sheet.write_string(row, col + 11,
                                                       str(doc_id.document_id.vehicle_status.vehicle_status_name),
                                                       main_heading)
                                if doc_id.issue_date:
                                    sheet.write_string(row, col + 12, str(doc_id.issue_date), main_heading)
                                    sheet.write_string(row, col + 13, str(hijri_issue_date), main_heading)
                                if doc_id.expiry_date:
                                    sheet.write_string(row, col + 14, str(doc_id.expiry_date), main_heading)
                                    sheet.write_string(row, col + 16, str(days), main_heading)
                                if hijri_expiry_date:
                                    sheet.write_string(row, col + 15, str(hijri_expiry_date), main_heading)
                                if doc_id.renewel_license_date:
                                    sheet.write_string(row, col + 17, str(doc_id.renewel_license_date),
                                                       main_heading)
                                if renewel_license_hijri_date:
                                    sheet.write_string(row, col + 18, str(renewel_license_hijri_date), main_heading)
                                if doc_id.write_uid.name:
                                    sheet.write_string(row, col + 19, str(doc_id.write_uid.name), main_heading)
                                if doc_id.last_update_date:
                                    sheet.write_string(row, col + 20, str(doc_id.last_update_date), main_heading)
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



































































