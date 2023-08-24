from odoo import api, fields, models, _


class ClaimsReport(models.TransientModel):
    _name = "claims.report"

    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To", required=True)
    driver_id = fields.Many2one('res.partner', string="Driver")
    customer_id = fields.Many2one('res.partner', string="Customer")
    accident_agreement_type = fields.Selection(
        [('bassami_truck', 'Bassami Truck'), ('agreement_cus', 'Agreement Customer'),
         ('agreement_comp', 'Agreement Company')], string='Accident Agreement Type')

    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_truck_accidents.truck_accidents_claims_report_xlsx_id').report_action(self, data=data)


class ClaimsReportReportExcel(models.AbstractModel):
    _name = 'report.bsg_truck_accidents.truck_accidents_claims_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        domain = [('accident_date', '>=', docs.from_date), ('accident_date', '<=', docs.to_date)]
        # if docs.customer_id:
        #     domain += [('so_line_partner_id', '=', docs.customer_id.id)]
        # if docs.driver_id:
        #     domain += [('driver_name', '=', docs.driver_id.id)]
        # if docs.current_branches:
        #     domain += [('current_branch_id', 'in', docs.current_branches.ids)]
        # if docs.vehicle_type:
        #     domain += [('vehicle_type', 'in', docs.vehicle_type.ids)]
        rec_ids = self.env['bsg.truck.accident'].search(domain)
        main_heading = workbook.add_format({
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            'font_size': '12',
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
        sheet = workbook.add_worksheet('Claims Report')
        sheet.set_column('A:D', 30)
        sheet.set_column('E:M', 20)
        row = 0
        col = 0
        self.env.ref(
            'bsg_truck_accidents.driver_deduction_report_xlsx_id').report_file = "Claims Report"
        sheet.merge_range('A1:Q1', 'تقرير المطالبات', main_heading3)
        row += 1
        sheet.merge_range('A2:Q2', 'Claims Report', main_heading2)
        sheet.write('A4', 'Date From', main_heading2)
        sheet.write('B4', str(docs.from_date), main_heading2)
        sheet.write('C4', 'Date To', main_heading2)
        sheet.write('D4', str(docs.to_date), main_heading2)
        sheet.write('E4', 'Company', main_heading2)
        sheet.write('F4', str(self.env.user.company_id.name), main_heading2)
        row = 5
        sheet.write(row, col, 'Shipment No', main_heading2)
        sheet.write(row, col + 1, 'Accident Date', main_heading2)
        sheet.write(row, col + 2, 'Customer', main_heading2)
        sheet.write(row, col + 3, 'Note', main_heading2)
        sheet.write(row, col + 4, 'Compensation Amount', main_heading2)
        sheet.write(row, col + 5, 'Less RFQ Price', main_heading2)
        sheet.write(row, col + 6, 'RFQ Price', main_heading2)
        sheet.write(row, col + 7, 'Spare Parts Amount', main_heading2)
        sheet.write(row, col + 8, 'Raw Material Amount', main_heading2)
        sheet.write(row, col + 9, 'Hand Wages Amount', main_heading2)
        sheet.write(row, col + 10, 'Driver Name', main_heading2)
        sheet.write(row, col + 11, 'Mistake Amount', main_heading2)
        sheet.write(row, col + 12, 'Status', main_heading2)
        row += 1
        sheet.write(row, col, 'رقم الشحنة', main_heading2)
        sheet.write(row, col + 1, 'تاريخ الحادث', main_heading2)
        sheet.write(row, col + 2, 'عميل', main_heading2)
        sheet.write(row, col + 3, 'ملحوظة', main_heading2)
        sheet.write(row, col + 4, 'مبلغ التعويض', main_heading2)
        sheet.write(row, col + 5, 'سعر RFQ أقل', main_heading2)
        sheet.write(row, col + 6, 'سعر RFQ', main_heading2)
        sheet.write(row, col + 7, 'مبلغ قطع الغيار', main_heading2)
        sheet.write(row, col + 8, 'كمية المواد الخام', main_heading2)
        sheet.write(row, col + 9, 'مبلغ الأجور اليدوية', main_heading2)
        sheet.write(row, col + 10, 'اسم السائق', main_heading2)
        sheet.write(row, col + 11, 'مبلغ الخطأ', main_heading2)
        sheet.write(row, col + 12, 'حالة', main_heading2)
        row += 1
        accident_ids = sorted(rec_ids, key=lambda r: r.accident_date)
        tot_comp_amount = 0
        tot_less_rfq_amount = 0
        tot_rfq_amount = 0
        tot_spare_parts_amount = 0
        tot_raw_material_amount = 0
        tot_hand_wages_amount = 0
        tot_mistake_amount = 0
        if accident_ids:
            for accident in accident_ids:
                if accident:
                    if accident.assign_deduction_drivers:
                        driver_name = accident.special_customer.ref
                    else:
                        driver_name = accident.driver_name.partner_id.ref
                    if accident.shipment_no_id:
                        sheet.write_string(row, col, str(accident.shipment_no_id.display_name), main_heading)
                    if accident.accident_date:
                        sheet.write_string(row, col + 1, str(accident.accident_date), main_heading)
                    if accident.so_line_partner_id:
                        sheet.write_string(row, col + 2, str(accident.so_line_partner_id.display_name), main_heading)
                    if accident.note:
                        sheet.write_string(row, col + 3, str(accident.note), main_heading)
                    if accident.compensation_amount:
                        sheet.write_string(row, col + 4, str(accident.compensation_amount), main_heading)
                        tot_comp_amount = tot_comp_amount + accident.compensation_amount
                    if accident.less_rfq_price:
                        sheet.write_string(row, col + 5, str(accident.less_rfq_price), main_heading)
                        tot_less_rfq_amount = tot_less_rfq_amount + accident.less_rfq_price
                    if accident.rfq_price:
                        sheet.write_string(row, col + 6, str(accident.rfq_price), main_heading)
                        tot_rfq_amount = tot_rfq_amount + accident.rfq_price
                    if accident.spare_parts_amount:
                        sheet.write_string(row, col + 7, str(accident.spare_parts_amount), main_heading)
                        tot_spare_parts_amount = tot_spare_parts_amount + accident.spare_parts_amount
                    if accident.raw_materials_amount:
                        sheet.write_string(row, col + 8, str(accident.raw_materials_amount), main_heading)
                        tot_raw_material_amount = tot_raw_material_amount + accident.raw_materials_amount
                    if accident.hand_wages_amount:
                        sheet.write_string(row, col + 9, str(accident.hand_wages_amount), main_heading)
                        tot_hand_wages_amount = tot_hand_wages_amount + accident.hand_wages_amount
                    if accident.driver_name:
                        sheet.write_string(row, col + 10, str(driver_name), main_heading)
                    if accident.mistake_percentage:
                        sheet.write_string(row, col + 11, str(accident.mistake_percentage), main_heading)
                        tot_mistake_amount = tot_mistake_amount + accident.mistake_percentage
                    if accident.state:
                        sheet.write_string(row, col + 12, str(dict(accident._fields['state'].selection).get(accident.state)), main_heading)
                    row += 1
            sheet.write_string(row, 0, "Total", main_heading2)
            sheet.write_string(row, 4, str(tot_comp_amount), main_heading2)
            sheet.write_string(row, 5, str(tot_less_rfq_amount), main_heading2)
            sheet.write_string(row, 6, str(tot_rfq_amount), main_heading2)
            sheet.write_string(row, 7, str(tot_spare_parts_amount), main_heading2)
            sheet.write_string(row, 8, str(tot_raw_material_amount), main_heading2)
            sheet.write_string(row, 9, str(tot_hand_wages_amount), main_heading2)
            sheet.write_string(row, 11, str(tot_mistake_amount), main_heading2)
        else:
            sheet.merge_range('A9:Q9', 'No results found', main_heading3)
