from odoo import api, fields, models, _


class DriverDeductionReport(models.TransientModel):
    _name = "driver.deduction.report"

    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To", required=True)
    driver_id = fields.Many2one('res.partner', string="Driver")

    def click_print_excel(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('bsg_truck_accidents.driver_deduction_report_xlsx_id').report_action(self, data=data)


class DriverDeductionReportExcel(models.AbstractModel):
    _name = 'report.bsg_truck_accidents.driver_deduction_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, lines, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        domain = [('accident_date', '>=', docs.from_date), ('accident_date', '<=', docs.to_date),
                  ('move_id', '!=', False)]
        if docs.driver_id:
            domain += [('special_customer', '=', docs.driver_id.id),('assign_deduction_drivers', '=', True)]
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
        sheet = workbook.add_worksheet('Driver Mistake Percentage Report')
        sheet.set_column('A:F', 18)
        row = 0
        col = 0
        self.env.ref(
            'bsg_truck_accidents.driver_deduction_report_xlsx_id').report_file = "Driver Mistake Percentage Report"
        sheet.merge_range('A1:Q1', 'تقرير نسبة خطأ السائق', main_heading3)
        row += 1
        sheet.merge_range('A2:Q2', 'Driver Mistake Percentage Report', main_heading3)
        sheet.write('A4', 'Date From', main_heading2)
        sheet.write('B4', str(docs.from_date), main_heading2)
        sheet.write('C4', 'Date To', main_heading2)
        sheet.write('D4', str(docs.to_date), main_heading2)
        sheet.write('E4', 'Company', main_heading2)
        sheet.write('F4', str(self.env.user.company_id.name), main_heading2)
        row = 5
        sheet.write(row, col, 'Driver Name', main_heading2)
        sheet.write(row, col + 1, 'Driver Code', main_heading2)
        sheet.write(row, col + 2, 'Amount', main_heading2)
        sheet.write(row, col + 3, 'Note', main_heading2)
        row += 1
        sheet.write(row, col, 'اسم السائق', main_heading2)
        sheet.write(row, col + 1, 'كود السائق', main_heading2)
        sheet.write(row, col + 2, 'كمية', main_heading2)
        sheet.write(row, col + 3, 'ملحوظة', main_heading2)
        row += 1
        accident_ids = sorted(rec_ids, key=lambda r: r.accident_date)
        total_amount = 0
        if accident_ids:
            for accident in accident_ids:
                if accident:
                    if accident.driver_name:
                        sheet.write_string(row, col, str(accident.driver_name.name), main_heading)
                    if accident.driver_code:
                        sheet.write_string(row, col + 1, str(accident.driver_code), main_heading)
                    if accident.mistake_percentage:
                        sheet.write_string(row, col + 2, str(accident.mistake_percentage), main_heading)
                        total_amount = total_amount + accident.mistake_percentage
                    if accident.note:
                        sheet.write_string(row, col + 3, str(accident.note), main_heading)

                    row += 1
            sheet.write_string(row, 0, "Total", main_heading2)
            sheet.write_string(row, 2, str(total_amount), main_heading2)
        else:
            sheet.merge_range('A9:Q9', 'No results found', main_heading3)
