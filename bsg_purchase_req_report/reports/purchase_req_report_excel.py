from odoo import models
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter
import collections, functools, operator
from collections import OrderedDict
import pandas as pd
from num2words import num2words

state_format = {'all':'All','tsub': 'To Submit',
        'tapprove': 'To Approve','approve': 'Approved',
        'open': 'Open', 'close': 'Close','cancel': 'Cancel',
        'reject': 'Reject','done': 'Done','done_close':'Done And Close'}

class PurchaseReqReportExcel(models.AbstractModel):
    _name = 'report.bsg_purchase_req_report.pr_report_xlsx'
    _inherit ='report.report_xlsx.abstract'



    def generate_xlsx_report(self, workbook,lines,data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
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
        sheet = workbook.add_worksheet('Purchase Request Report  Report')
        sheet.freeze_panes(1, 0)
        sheet.freeze_panes(2, 0)
        sheet.freeze_panes(3, 0)
        sheet.freeze_panes(4, 0)
        sheet.freeze_panes(5, 0)
        sheet.freeze_panes(6, 0)
        sheet.freeze_panes(7, 0)
        sheet.set_column('A:AE', 15)
        domain=[]
        row = 2
        col = 0
        date_cond = ''    
        if docs.start_date and docs.end_date:
            date_cond = f"purchase_req_line.date_pr between '{str(docs.start_date)}' and '{str(docs.end_date)}'"
        
        product_cond = ''
        if docs.product_ids:
            product_ids = len(docs.product_ids.ids) == 1 and "(%s)" %docs.product_ids.ids[0] or  str(tuple(docs.product_ids.ids))
            product_cond = f"and purchase_req_line.product_id in {product_ids}"
        category_cond = ''    
        if docs.category_ids:
            category_ids = len(docs.category_ids.ids) == 1 and "(%s)" %docs.category_ids.ids[0] or  str(tuple(docs.category_ids.ids))
            category_cond = f"and purchase_req_line.product_categ in {category_ids}"
        branch_cond = ''    
        if docs.branch_ids:
            branch_ids = len(docs.branch_ids.ids) == 1 and "(%s)" %docs.branch_ids.ids[0] or  str(tuple(docs.branch_ids.ids))
            branch_cond = f"and purchase_req_line.branches in {branch_ids}"
        department_cond = ''    
        if docs.department_ids:
            department_ids = len(docs.department_ids.ids) == 1 and "(%s)" %docs.department_ids.ids[0] or  str(tuple(docs.department_ids.ids))
            department_cond = f"and purchase_req_line.department_id in {department_ids}"
        state_filter_cond = ''
        if docs.state_filter != 'all':
            if docs.state_filter == 'done_close':
                state_filter_cond = f"and purchase_req_line.state in ('done','close')"
            else:
                state_filter_cond = f"and purchase_req_line.state = '{docs.state_filter}'"
        request_type_cond = ''    
        if docs.request_type == 'stock':
            request_type_cond = f"and purchase_req_line.request_type = 'stock'"
        if docs.request_type == 'workshop':
            request_type_cond = f"and purchase_req_line.request_type = 'workshop'"
        if docs.request_type == 'branch':
            request_type_cond = f"and purchase_req_line.request_type = 'branch'"
        pr_qty_cond = ''
        if docs.has_rfq:  
            pr_qty_cond += f"and purchase_req_line.qty_rfq > 0"
        if docs.has_po:  
            pr_qty_cond += f"and purchase_req_line.qty_po > 0"
        if docs.has_iss: 
            pr_qty_cond += f"and purchase_req_line.iss_qty > 0"
        if docs.has_recieved:
            pr_qty_cond += f"and purchase_req_line.qty_received  > 0"
        
        if docs.has_no_rfq:  
            pr_qty_cond += f"and purchase_req_line.qty_rfq = 0"
        if docs.has_no_po:  
            pr_qty_cond += f"and purchase_req_line.qty_po = 0"
        if docs.has_no_iss: 
            pr_qty_cond += f"and purchase_req_line.iss_qty = 0"
        if docs.has_no_recieved:
            pr_qty_cond += f"and purchase_req_line.qty_received  = 0"


        table_name = "purchase_req_line as purchase_req_line \
            LEFT JOIN purchase_req as purchase_req ON purchase_req_line.preq = purchase_req.id\
            LEFT JOIN product_category as product_category ON purchase_req_line.product_categ = product_category.id\
            LEFT JOIN  bsg_branches_bsg_branches as bsg_branches_bsg_branches ON purchase_req_line.branches = bsg_branches_bsg_branches.id\
            LEFT JOIN product_product as product_product ON purchase_req_line.product_id = product_product.id \
            LEFT JOIN product_template as product_template ON product_product.product_tmpl_id = product_template.id \
            LEFT JOIN hr_department as department_department ON purchase_req_line.department_id = department_department.id"
        self.env.cr.execute(
            "select purchase_req_line.id as purchase_req_line_id,purchase_req_line.preq as purchase_req_line_preq,purchase_req_line.date_pr as purchase_req_line_date_pr,purchase_req_line.name as purchase_req_line_name\
            ,purchase_req_line.product_categ as purchase_req_line_product_categ,purchase_req_line.product_id as purchase_req_line_product_id,purchase_req_line.qty as purchase_req_line_qty\
            ,purchase_req_line.qty_po as purchase_req_line_qty_po,purchase_req_line.qty_received as purchase_req_line_qty_received,purchase_req_line.department_id as purchase_req_line_department_id\
            ,purchase_req_line.branches as purchase_req_line_branches,purchase_req_line.request_type as purchase_req_line_request_type,purchase_req_line.state as purchase_req_line_state\
            ,purchase_req_line.qty_rfq as purchase_req_line_qty_rfq, purchase_req_line.iss_qty as purchase_req_line_iss_qty,purchase_req_line.qty_returned as purchase_req_line_qty_returned,purchase_req_line.qty_net_received as purchase_req_line_qty_net_received\
            ,purchase_req_line.fleet_num as purchase_req_line_fleet_num,purchase_req.id as purchase_req_id,purchase_req.name as purchase_req_name\
            ,product_category.id as product_category_id,product_category.name as product_category_name,product_category.complete_name as product_category_complete_name\
            ,bsg_branches_bsg_branches.id as bsg_branches_bsg_branches_id,bsg_branches_bsg_branches.branch_ar_name as bsg_branches_bsg_branches_name\
            ,product_product.id as product_product_id ,product_template.id as product_template_id,product_template.name as product_template_name\
            ,department_department.id as department_department_id,department_department.complete_name as department_department_name\
             FROM " + table_name + "\
            Where %s %s %s %s %s %s %s %s ORDER BY purchase_req_line.date_pr"%(date_cond,product_cond,category_cond,branch_cond,department_cond,state_filter_cond,request_type_cond,pr_qty_cond))
        result = self._cr.fetchall()
        
        bsg_pr_lines = pd.DataFrame(list(result))
        bsg_pr_lines = bsg_pr_lines.rename(
            columns={0: 'pr_line_id', 1: 'pr_id', 2: 'date_pr_line', 3: 'pr_line_name',
                     4: 'product_categ_id', 5: 'product_id', 6: 'qty',  7: 'qty_po',
                     8: 'qty_received',9: 'department_id',10: 'branch_id',11:'request_type',12:'pr_line_state',
                     13:'qty_rfq',14:'iss_qty',15:'qty_returned',16:'qty_net_received',17:'fleet_num',
                     18: 'pr_id', 19: 'pr_name',20: 'pc_id', 21: 'pc_name',22:'pc_complete_name',23: 'branch_id', 24: 'branch_name',
                     25:'product_product_id',26:'product_template_id',27:'product_template_name',
                     28:'department_id',29:'department_name'})

        row+=1
        if not bsg_pr_lines.empty:
            self.env.ref('bsg_purchase_req_report.purchase_req_report_xlsx_id').report_file = "Purchase Request Report"
            sheet.merge_range('A1:O1', 'تقرير طلبات الشراء', main_heading3)
            sheet.merge_range('A2:O2', 'Purchase Request Report', main_heading3)
            sheet.write(row, col, 'PR State', main_heading2)
            sheet.write_string(row, col + 1, str(state_format[docs.state_filter]), main_heading)
            row+=1
            sheet.write(row, col , 'Company', main_heading2)
            sheet.write(row, col + 1, 'Start Date', main_heading2)
            sheet.write(row, col + 2, 'End Date', main_heading2)
            row+=1
            sheet.write_string(row, col, str(self.env.user.company_id.name), main_heading)
            sheet.write_string(row, col + 1, str(docs.start_date), main_heading)
            sheet.write_string(row, col + 2, str(docs.end_date), main_heading)
            row+=1
            total_qty = 0
            total_qty_rfq = 0
            total_qty_po = 0
            total_po_price = 0
            total_invoice_price = 0
            total_qty_received = 0
            total_iss_qty = 0
            total_qty_returned = 0
            total_qty_net_received = 0
            if docs.pr_groub_by == 'group_by_product':
                sheet.write(row, col, 'Requested Product ', main_heading2)
                sheet.write(row, col + 1, 'Requested Qty ', main_heading2)
                sheet.write(row, col + 2, 'Rfq Qty ', main_heading2)
                sheet.write(row, col + 3, 'PO Qty ', main_heading2)
                sheet.write(row, col + 4, 'Received Qty ', main_heading2)
                sheet.write(row, col + 5, 'ISS Qty ', main_heading2)
                sheet.write(row, col + 6, 'Returned Qty ', main_heading2)
                sheet.write(row, col + 7, 'Net Received Qty ', main_heading2)
                row += 1
                bsg_pr_lines_group_by_product = bsg_pr_lines.groupby(['product_id'])
                for key_product,df_product in bsg_pr_lines_group_by_product:
                    qty = 0
                    qty_rfq = 0
                    qty_po = 0
                    qty_received = 0
                    iss_qty = 0
                    qty_returned = 0
                    qty_net_received = 0
                    for key, value in df_product.iterrows():
                        qty += value['qty']
                        qty_rfq += value['qty_rfq']
                        qty_po += value['qty_po']
                        qty_received += value['qty_received']
                        iss_qty += value['iss_qty']
                        qty_returned += value['qty_returned']
                        qty_net_received += value['qty_net_received']
                    if value['product_template_name']:
                        sheet.write_string(row, col, str(value['product_template_name']), main_heading)
                    if qty:
                        sheet.write_string(row, col + 1, str(qty), main_heading)
                        total_qty += qty
                    if qty_rfq:
                        sheet.write_string(row, col + 2, str(qty_rfq), main_heading)
                        total_qty_rfq += qty_rfq
                    if qty_po:
                        sheet.write_string(row, col + 3, str(qty_po), main_heading)
                        total_qty_po += qty_po
                    if qty_received:
                        sheet.write_string(row, col + 4, str(qty_received), main_heading)
                        total_qty_received += qty_received
                    if iss_qty:
                        sheet.write_string(row, col + 5, str(iss_qty), main_heading)
                        total_iss_qty += iss_qty
                    if qty_returned:
                        sheet.write_string(row, col + 6, str(qty_returned), main_heading)
                        total_qty_returned += qty_returned
                    if qty_net_received:
                        sheet.write_string(row, col + 7, str(qty_net_received), main_heading)
                        total_qty_net_received += qty_net_received
                    row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total_qty), main_heading)
                sheet.write_string(row, col + 2, str(total_qty_rfq), main_heading)
                sheet.write_string(row, col + 3, str(total_qty_po), main_heading)
                sheet.write_string(row, col + 4, str(total_qty_received), main_heading)
                sheet.write_string(row, col + 5, str(total_iss_qty), main_heading)
                sheet.write_string(row, col + 6, str(total_qty_returned), main_heading)
                sheet.write_string(row, col + 7, str(total_qty_net_received), main_heading)

            elif docs.pr_groub_by == 'group_by_category':
                sheet.write(row, col, 'Product Category ', main_heading2)
                sheet.write(row, col + 1, 'Requested Qty ', main_heading2)
                sheet.write(row, col + 2, 'Rfq Qty ', main_heading2)
                sheet.write(row, col + 3, 'PO Qty ', main_heading2)
                sheet.write(row, col + 4, 'Received Qty ', main_heading2)
                sheet.write(row, col + 5, 'ISS Qty ', main_heading2)
                sheet.write(row, col + 6, 'Returned Qty ', main_heading2)
                sheet.write(row, col + 7, 'Net Received Qty ', main_heading2)
                row += 1
                bsg_pr_lines_group_by_category = bsg_pr_lines.groupby(['pc_name'])
                for key_product_categ,df_product_categ in bsg_pr_lines_group_by_category:
                    qty = 0
                    qty_rfq = 0
                    qty_po = 0
                    qty_received = 0
                    iss_qty = 0
                    qty_returned = 0
                    qty_net_received = 0
                    for key, value in df_product_categ.iterrows():
                        qty += value['qty']
                        qty_rfq += value['qty_rfq']
                        qty_po += value['qty_po']
                        qty_received += value['qty_received']
                        iss_qty += value['iss_qty']
                        qty_returned += value['qty_returned']
                        qty_net_received += value['qty_net_received']
                    if key_product_categ:
                        sheet.write_string(row, col, str(key_product_categ), main_heading)
                    if qty:
                        sheet.write_string(row, col + 1, str(qty), main_heading)
                        total_qty += qty
                    if qty_rfq:
                        sheet.write_string(row, col + 2, str(qty_rfq), main_heading)
                        total_qty_rfq += qty_rfq
                    if qty_po:
                        sheet.write_string(row, col + 3, str(qty_po), main_heading)
                        total_qty_po += qty_po
                    if qty_received:
                        sheet.write_string(row, col + 4, str(qty_received), main_heading)
                        total_qty_received += qty_received
                    if iss_qty:
                        sheet.write_string(row, col + 5, str(iss_qty), main_heading)
                        total_iss_qty += iss_qty
                    if qty_returned:
                        sheet.write_string(row, col + 6, str(qty_returned), main_heading)
                        total_qty_returned += qty_returned
                    if qty_net_received:
                        sheet.write_string(row, col + 7, str(qty_net_received), main_heading)
                        total_qty_net_received += qty_net_received
                    row += 1
                sheet.write(row, col, 'Total', main_heading2)
                sheet.write_string(row, col + 1, str(total_qty), main_heading)
                sheet.write_string(row, col + 2, str(total_qty_rfq), main_heading)
                sheet.write_string(row, col + 3, str(total_qty_po), main_heading)
                sheet.write_string(row, col + 4, str(total_qty_received), main_heading)
                sheet.write_string(row, col + 5, str(total_iss_qty), main_heading)
                sheet.write_string(row, col + 6, str(total_qty_returned), main_heading)
                sheet.write_string(row, col + 7, str(total_qty_net_received), main_heading)

            elif not docs.is_with_details:
                    sheet.write(row, col, 'PR #', main_heading2)
                    sheet.write(row, col + 1, 'PR Date', main_heading2)
                    sheet.write(row, col + 2, 'Description', main_heading2)
                    sheet.write(row, col + 3, 'Product Category ', main_heading2)
                    sheet.write(row, col + 4, 'Requested Product ', main_heading2)
                    sheet.write(row, col + 5, 'Requested Qty ', main_heading2)
                    sheet.write(row, col + 6, 'Rfq Qty ', main_heading2)
                    sheet.write(row, col + 7, 'PO Qty ', main_heading2)
                    sheet.write(row, col + 8, 'Received Qty ', main_heading2)
                    sheet.write(row, col + 9, 'ISS Qty ', main_heading2)
                    sheet.write(row, col + 10, 'Returned Qty ', main_heading2)
                    sheet.write(row, col + 11, 'Net Received Qty ', main_heading2)
                    sheet.write(row, col + 12, 'Department ', main_heading2)
                    sheet.write(row, col + 13, 'Branch ', main_heading2)
                    sheet.write(row, col + 14, 'Request Type ', main_heading2)
                    sheet.write(row, col + 15, 'Fleet/Trailer', main_heading2)
                    sheet.write(row, col + 16, 'State', main_heading2)
                    row += 1
                    for key,value in bsg_pr_lines.iterrows():
                        if value['pr_name']:
                            sheet.write_string(row, col, str(value['pr_name']), main_heading)
                        if value['date_pr_line']:
                            sheet.write_string(row, col + 1,str(value['date_pr_line']), main_heading)
                        if value['pr_line_name']:
                            sheet.write_string(row, col + 2,str(value['pr_line_name']), main_heading)
                        if value['pc_name']:
                            sheet.write_string(row, col + 3,str(value['pc_complete_name']), main_heading)
                        if value['product_template_name']:
                            sheet.write_string(row, col + 4, str(value['product_template_name']),main_heading)
                        if value['qty']:
                            sheet.write_string(row, col + 5,str(value['qty']), main_heading)
                            total_qty += value['qty']
                        if value['qty_rfq']:
                            sheet.write_string(row, col + 6,str(value['qty_rfq']), main_heading)
                            total_qty_rfq += value['qty_rfq']
                        if value['qty_po']:
                            sheet.write_string(row, col + 7,str(value['qty_po']), main_heading)
                            total_qty_po += value['qty_po']
                        if value['qty_received']:
                            sheet.write_string(row, col + 8,str(value['qty_received']), main_heading)
                            total_qty_received += value['qty_received']
                        if value['iss_qty']:
                            sheet.write_string(row, col + 9,str(value['iss_qty']), main_heading)
                            total_iss_qty += value['iss_qty']
                        if value['qty_returned']:
                            sheet.write_string(row, col + 10,str(value['qty_returned']), main_heading)
                            total_qty_returned += value['qty_returned']
                        if value['qty_net_received']:
                            sheet.write_string(row, col + 11,str(value['qty_net_received']), main_heading)
                            total_qty_net_received += value['qty_net_received']
                        if value['department_name']:
                            sheet.write_string(row, col + 12,str(value['department_name']), main_heading)
                        if value['branch_name']:
                            sheet.write_string(row, col + 13,str(value['branch_name']), main_heading)
                        if value['request_type']:
                            sheet.write_string(row, col + 14, str(value['request_type']),main_heading)
                        if value['fleet_num']:
                            sheet.write_string(row, col + 15,str(value['fleet_num']), main_heading)
                        if value['pr_line_state']:
                            sheet.write_string(row, col + 16, str(state_format[value['pr_line_state']]), main_heading)
                        row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 5, str(total_qty), main_heading)
                    sheet.write_string(row, col + 6, str(total_qty_rfq), main_heading)
                    sheet.write_string(row, col + 7, str(total_qty_po), main_heading)
                    sheet.write_string(row, col + 8, str(total_qty_received), main_heading)
                    sheet.write_string(row, col + 9, str(total_iss_qty), main_heading)
                    sheet.write_string(row, col + 10, str(total_qty_returned), main_heading)
                    sheet.write_string(row, col + 11, str(total_qty_net_received), main_heading)
            elif  docs.is_with_details:
                    sheet.write(row, col, 'PR #', main_heading2)
                    sheet.write(row, col + 1, 'PR Date', main_heading2)
                    sheet.write(row, col + 2, 'Description', main_heading2)
                    sheet.write(row, col + 3, 'Product Category ', main_heading2)
                    sheet.write(row, col + 4, 'Requested Product ', main_heading2)
                    sheet.write(row, col + 5, 'Requested Qty ', main_heading2)
                    sheet.write(row, col + 6, 'Rfq Qty ', main_heading2)
                    sheet.write(row, col + 7, 'PO Qty ', main_heading2)
                    sheet.write(row, col + 8, 'PO Price ', main_heading2)
                    sheet.write(row, col + 9, 'Invoice Price ', main_heading2)
                    sheet.write(row, col + 10, 'Vendors ', main_heading2)
                    sheet.write(row, col + 11, 'Received Qty ', main_heading2)
                    sheet.write(row, col + 12, 'ISS Qty ', main_heading2)
                    sheet.write(row, col + 13, 'Returned Qty ', main_heading2)
                    sheet.write(row, col + 14, 'Net Received Qty ', main_heading2)
                    sheet.write(row, col + 15, 'Department ', main_heading2)
                    sheet.write(row, col + 16, 'Branch ', main_heading2)
                    sheet.write(row, col + 17, 'Request Type ', main_heading2)
                    sheet.write(row, col + 18, 'Fleet/Trailer', main_heading2)
                    sheet.write(row, col + 19, 'State', main_heading2)
                    row += 1
                    for key,value in bsg_pr_lines.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id','=',int(value['pr_line_id']))],limit=1)
                        if value['pr_name']:
                            sheet.write_string(row, col, str(value['pr_name']), main_heading)
                        if value['date_pr_line']:
                            sheet.write_string(row, col + 1,str(value['date_pr_line']), main_heading)
                        if value['pr_line_name']:
                            sheet.write_string(row, col + 2,str(value['pr_line_name']), main_heading)
                        if value['pc_name']:
                            sheet.write_string(row, col + 3,str(value['pc_complete_name']), main_heading)
                        if purchase_req_id.product_id.name:
                            sheet.write_string(row, col + 4, str(purchase_req_id.product_id.name),main_heading)
                        if value['qty']:
                            sheet.write_string(row, col + 5, str(value['qty']), main_heading)
                            total_qty += value['qty']
                        if purchase_req_id.qty_rfq:
                            sheet.write_string(row, col + 6, str(purchase_req_id.qty_rfq), main_heading)
                            total_qty_rfq += purchase_req_id.qty_rfq
                        if value['qty_po']:
                            sheet.write_string(row, col + 7, str(value['qty_po']), main_heading)
                            total_qty_po += value['qty_po']
                        if purchase_req_id.price_total:
                            sheet.write_string(row, col + 8, str(purchase_req_id.price_total), main_heading)
                            total_po_price += purchase_req_id.price_total
                        if purchase_req_id.invoice_total_price:
                            sheet.write_string(row, col + 9, str(purchase_req_id.invoice_total_price), main_heading)
                            total_invoice_price += purchase_req_id.invoice_total_price
                        if purchase_req_id.partner_ids:
                            vals_list = purchase_req_id.partner_ids.mapped('name')
                            vals = ",".join(vals_list)
                            sheet.write_string(row, col + 10, str(vals), main_heading)
                        if value['qty_received']:
                            sheet.write_string(row, col + 11, str(value['qty_received']), main_heading)
                            total_qty_received += value['qty_received']
                        if purchase_req_id.iss_qty:
                            sheet.write_string(row, col + 12, str(purchase_req_id.iss_qty), main_heading)
                            total_iss_qty += purchase_req_id.iss_qty
                        if purchase_req_id.qty_returned:
                            sheet.write_string(row, col + 13, str(purchase_req_id.qty_returned), main_heading)
                            total_qty_returned += purchase_req_id.qty_returned
                        if purchase_req_id.qty_net_received:
                            sheet.write_string(row, col + 14, str(purchase_req_id.qty_net_received), main_heading)
                            total_qty_net_received += purchase_req_id.qty_net_received
                        if purchase_req_id.department_id.display_name:
                            sheet.write_string(row, col + 15,str(purchase_req_id.department_id.display_name), main_heading)
                        if value['branch_name']:
                            sheet.write_string(row, col + 16,str(value['branch_name']), main_heading)
                        if value['request_type']:
                            sheet.write_string(row, col + 17, str(value['request_type']),main_heading)
                        if purchase_req_id.fleet_id_ref:
                            sheet.write_string(row, col + 18,str(purchase_req_id.fleet_num), main_heading)
                        if value['pr_line_state']:
                            sheet.write_string(row, col + 19, str(state_format[value['pr_line_state']]), main_heading)
                        row += 1
                    sheet.write(row, col, 'Total', main_heading2)
                    sheet.write_string(row, col + 5, str(total_qty), main_heading)
                    sheet.write_string(row, col + 6, str(total_qty_rfq), main_heading)
                    sheet.write_string(row, col + 7, str(total_qty_po), main_heading)
                    sheet.write_string(row, col + 8, str(total_po_price), main_heading)
                    sheet.write_string(row, col + 9, str(total_invoice_price), main_heading)
                    sheet.write_string(row, col + 11, str(total_qty_received), main_heading)
                    sheet.write_string(row, col + 12, str(total_iss_qty), main_heading)
                    sheet.write_string(row, col + 13, str(total_qty_returned), main_heading)
                    sheet.write_string(row, col + 14, str(total_qty_net_received), main_heading)
