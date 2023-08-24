from odoo import models
import pandas as pd
from odoo.exceptions import UserError


class SimCardReportExcel(models.AbstractModel):
    _name = 'report.sim_card_reports.sim_card_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_job_positions(self, positin_ids_str):
        result_str = []
        position_str = []
        arr = set(list(positin_ids_str.split(',')))
        for rec in arr:
            if rec == 'nan':
                continue
            if int(float(rec)) not in result_str:
                result_str.append(int(float(rec)))
        for rec in result_str:
            name = self.env['hr.job'].browse(rec).name
            position_str.append(name)
        return ',\n'.join(position_str)

    def get_branch_str(self, branch_ids_str):
        result_str = []
        position_str = []
        arr = set(list(branch_ids_str.split(',')))
        for rec in arr:
            if rec == 'nan':
                continue
            if int(float(rec)) not in result_str:
                result_str.append(int(float(rec)))
        for rec in result_str:
            name = self.env['bsg_branches.bsg_branches'].browse(rec).branch_ar_name
            position_str.append(name)
        return ',\n'.join(position_str)

    def get_department_str(self, department_ids_str):
        result_str = []
        position_str = []
        arr = set(list(department_ids_str.split(',')))
        for rec in arr:
            if rec == 'nan':
                continue
            if int(float(rec)) not in result_str:
                result_str.append(int(float(rec)))
        for rec in result_str:
            name = self.env['hr.department'].browse(rec).name
            position_str.append(name)
        return ',\n'.join(position_str)

    def generate_xlsx_report(self, workbook, lines, data=None):
        table_name = "sim_card_define"
        self.env.cr.execute("select id,pkg_id,mble_no,service_id,date,is_cost,employee,"
                            "last_delivery_seq_id,notes,sim_type,contract_no,imis_no,msisdn,id_no,delivery_seq_id,"
                            "description,state,request_count,delivered_id,delivered_count,receipt_id,receipt_count FROM " + table_name + " ")
        result = self._cr.fetchall()
        all_data = pd.DataFrame(list(result))
        all_data = all_data.rename(
            columns={0: 'self_id', 1: 'pkg_id', 2: 'mble_no', 3: 'service_id', 4: 'date',
                     5: 'is_cost', 6: 'employee', 7: 'last_delivery_seq_id', 8: 'notes', 9: 'sim_type',
                     10: 'contract_no', 11: 'imis_no', 12: 'msisdn', 13: 'id_no',
                     14: 'delivery_seq_id', 15: 'description', 16: 'state',
                     17: 'request_count', 18: 'delivered_id', 19: 'delivered_count', 20: 'receipt_id',
                     21: 'receipt_count'})
        bsg_branches_sim_card_table = "bsg_branches_bsg_branches_sim_card_define_rel"
        self.env.cr.execute(
            "select sim_card_define_id,bsg_branches_bsg_branches_id FROM " + bsg_branches_sim_card_table + "")
        result = self._cr.fetchall()
        bsg_branches_sim_card = pd.DataFrame(list(result))
        bsg_branches_sim_card = bsg_branches_sim_card.rename(
            columns={0: 'sim_card_id', 1: 'branch_id'})
        all_data = pd.merge(all_data, bsg_branches_sim_card, how='left', left_on='self_id', right_on='sim_card_id')
        all_data['branch_id'] = all_data['branch_id'].astype(str)
        hr_job_sim_card_table = "hr_job_sim_card_define_rel"
        self.env.cr.execute(
            "select sim_card_define_id,hr_job_id FROM " + hr_job_sim_card_table + "")
        result = self._cr.fetchall()
        hr_job_sim_card = pd.DataFrame(list(result))
        hr_job_sim_card = hr_job_sim_card.rename(
            columns={0: 'sim_card_id', 1: 'hr_job_id'})
        all_data = pd.merge(all_data, hr_job_sim_card, how='left', left_on='self_id',
                            right_on='sim_card_id')
        all_data['hr_job_id'] = all_data['hr_job_id'].astype(str)
        hr_department_sim_card_table = "hr_department_sim_card_define_rel"
        self.env.cr.execute(
            "select sim_card_define_id,hr_department_id FROM " + hr_department_sim_card_table + "")
        result = self._cr.fetchall()
        hr_department_sim_card = pd.DataFrame(list(result))
        hr_department_sim_card = hr_department_sim_card.rename(
            columns={0: 'sim_card_id', 1: 'hr_department_id'})
        all_data = pd.merge(all_data, hr_department_sim_card, how='left', left_on='self_id',
                            right_on='sim_card_id')
        all_data['hr_department_id'] = all_data['hr_department_id'].astype(str)
        all_data = all_data.groupby('mble_no').agg(
            {'sim_type': 'first', 'service_id': 'first', 'pkg_id': 'first', 'date': 'first',
             'is_cost': 'first', 'employee': 'first', 'branch_id': ', '.join, 'hr_job_id': ', '.join,
             'hr_department_id': ', '.join}).reset_index()

        main_heading1 = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": 'left',
            "valign": 'vcenter',
            "font_color": 'black',
            "bg_color": '#D3D3D3',
            'font_size': '11',
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
            'font_size': '10',
        })
        main_data.set_border()
        worksheet = workbook.add_worksheet('SIM CARD REPORT')
        worksheet.merge_range('A1:L1', "SIM CARD REPORT", merge_format)
        worksheet.merge_range('A2:L2', "تقرير بيانات الشرائح", merge_format)
        worksheet.write('A5', 'Sim Card No', main_heading1)
        worksheet.write('B5', 'Sim Card Type', main_heading1)
        worksheet.write('C5', 'Service Provider', main_heading1)
        worksheet.write('D5', 'Package Type Name', main_heading1)
        worksheet.write('E5', 'Activation Date', main_heading1)
        worksheet.write('F5', 'Bear The Cost', main_heading1)
        worksheet.write('G5', 'Current Employee', main_heading1)
        worksheet.write('H5', 'Job Position', main_heading1)
        worksheet.write('I5', 'Branch', main_heading1)
        worksheet.write('J5', 'Department', main_heading1)
        # worksheet.write('K5', 'Analytic Account', main_heading1)
        worksheet.set_column('A:AB', 15)
        worksheet.set_default_row(25)

        row = 5
        col = 0

        for index, rec in all_data.iterrows():
            positions = self.get_job_positions(rec['hr_job_id'])
            branches = self.get_branch_str(rec['branch_id'])
            departments = self.get_department_str(rec['hr_department_id'])
            service_id = self.env['service.provider'].browse(int(rec['service_id'])).name
            pkg_id = self.env['package.type'].browse(int(rec['service_id'])).name
            worksheet.write_string(row, col + 0, str(rec['mble_no']), main_data)
            worksheet.write_string(row, col + 1, str(rec['sim_type']), main_data)
            worksheet.write_string(row, col + 2, service_id, main_data)
            worksheet.write_string(row, col + 3, pkg_id, main_data)
            worksheet.write_string(row, col + 4, str(rec['date']), main_data)
            worksheet.write_string(row, col + 5, str(rec['is_cost']), main_data)
            worksheet.write_string(row, col + 6, str(rec['employee']), main_data)
            worksheet.write_string(row, col + 7, positions, main_data)
            worksheet.write_string(row, col + 8, branches, main_data)
            worksheet.write_string(row, col + 9, departments, main_data)
            # worksheet.write_string(row, col + 10, str(rec['is_cost']), main_data)
            row += 1
