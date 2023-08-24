from odoo import models, fields, api, _
import pandas as pd


class PurchaseReqReportPdf(models.AbstractModel):
    _name = 'report.bsg_purchase_req_report.pr_report_pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        table_name = "purchase_req_line"
        self.env.cr.execute(
            "select id,preq,date_pr,name,product_categ,product_id,qty,qty_po,qty_received,department_id,branches,request_type,state FROM " + table_name + "")
        result = self._cr.fetchall()
        bsg_pr_lines = pd.DataFrame(list(result))
        bsg_pr_lines = bsg_pr_lines.rename(
            columns={0: 'pr_line_id', 1: 'pr_id', 2: 'date_pr_line', 3: 'pr_line_name',
                     4: 'product_categ_id', 5: 'product_id', 6: 'qty', 7: 'qty_po',
                     8: 'qty_received', 9: 'department_id', 10: 'branch_id', 11: 'request_type', 12: 'pr_line_state'})

        pr_table_name = "purchase_req"
        self.env.cr.execute(
            "select id,name FROM " + pr_table_name + "")
        pr_result = self._cr.fetchall()
        bsg_pr = pd.DataFrame(list(pr_result))
        bsg_pr = bsg_pr.rename(columns={0: 'pr_id', 1: 'pr_name'})
        bsg_pr_lines = pd.merge(bsg_pr_lines, bsg_pr, how='left', left_on='pr_id',
                                right_on='pr_id')

        pc_table_name = "product_category"
        self.env.cr.execute(
            "select id,name FROM " + pc_table_name + "")
        pc_result = self._cr.fetchall()
        bsg_pc = pd.DataFrame(list(pc_result))
        bsg_pc = bsg_pc.rename(columns={0: 'pc_id', 1: 'pc_name'})
        bsg_pr_lines = pd.merge(bsg_pr_lines, bsg_pc, how='left', left_on='product_categ_id',
                                right_on='pc_id')

        branch_table_name = "bsg_branches_bsg_branches"
        self.env.cr.execute(
            "select id,branch_ar_name FROM " + branch_table_name + "")
        branch_result = self._cr.fetchall()
        bsg_branch = pd.DataFrame(list(branch_result))
        bsg_branch = bsg_branch.rename(columns={0: 'branch_id', 1: 'branch_name'})
        bsg_pr_lines = pd.merge(bsg_pr_lines, bsg_branch, how='left', left_on='branch_id',
                                right_on='branch_id')

        if docs.product_ids:
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['product_id'].isin(docs.product_ids.ids))]
        if docs.category_ids:
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['product_categ_id'].isin(docs.category_ids.ids))]
        if docs.branch_ids:
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['branch_id'].isin(docs.branch_ids.ids))]
        if docs.department_ids:
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['department_id'].isin(docs.department_ids.ids))]
        if docs.pr_filter_by == 'done_pr':
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['pr_line_state'].isin(['done', 'close']))]
        if docs.pr_filter_by == 'open_pr':
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['pr_line_state'].isin(['open']))]
        if docs.request_type == 'stock':
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['request_type'] == 'stock')]
        if docs.request_type == 'workshop':
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['request_type'] == 'workshop')]
        if docs.request_type == 'branch':
            bsg_pr_lines = bsg_pr_lines.loc[(bsg_pr_lines['request_type'] == 'branch')]
        if docs.start_date and docs.end_date:
            bsg_pr_lines = bsg_pr_lines.loc[
                (bsg_pr_lines['date_pr_line'] >= (docs.start_date)) & (
                        bsg_pr_lines['date_pr_line'] <= (docs.end_date))]
        bsg_pr_lines = bsg_pr_lines.sort_values(by=['date_pr_line'])
        filter_by = (docs.pr_filter_by)
        company = str(self.env.user.company_id.name)
        start_date = str(docs.start_date)
        end_date = str(docs.end_date)
        if not bsg_pr_lines.empty:
            total_qty = 0
            total_qty_rfq = 0
            total_qty_po = 0
            total_po_price = 0
            total_invoice_price = 0
            total_qty_received = 0
            total_iss_qty = 0
            total_qty_returned = 0
            total_qty_net_received = 0
            data_dict_list = []
            data_dict_totals = {}
            if docs.pr_filter_by == 'group_by_product':
                bsg_pr_lines_group_by_product = bsg_pr_lines.groupby(['product_id'])
                for key_product, df_product in bsg_pr_lines_group_by_product:
                    qty = 0
                    qty_rfq = 0
                    qty_po = 0
                    qty_received = 0
                    iss_qty = 0
                    qty_returned = 0
                    qty_net_received = 0
                    product_id = self.env['product.product'].search([('id', '=', int(key_product))], limit=1)
                    for key, value in df_product.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id', '=', int(value['pr_line_id']))],
                                                                               limit=1)
                        qty += value['qty']
                        qty_rfq += purchase_req_id.qty_rfq
                        qty_po += value['qty_po']
                        qty_received += value['qty_received']
                        iss_qty += purchase_req_id.iss_qty
                        qty_returned += purchase_req_id.qty_returned
                        qty_net_received += purchase_req_id.qty_net_received
                        data_dict_list.append(
                            {'product_id': str(product_id.name), 'qty': str(qty), 'qty_rfq': str(qty_rfq),
                             'qty_po': str(qty_po), 'qty_received': str(qty_received),
                             'iss_qty': str(iss_qty), 'qty_returned': str(qty_returned),
                             'qty_net_received': str(qty_net_received)})
                        total_qty += qty
                        total_qty_rfq += qty_rfq
                        total_qty_po += qty_po
                        total_qty_received += qty_received
                        total_iss_qty += iss_qty
                        total_qty_returned += qty_returned
                        total_qty_net_received += qty_net_received
                data_dict_totals = {'total_qty': total_qty, 'total_qty_rfq': total_qty_rfq,
                                    'total_qty_po': total_qty_po, 'total_qty_received': total_qty_received,
                                    'total_iss_qty': total_iss_qty, 'total_qty_returned': total_qty_returned,
                                    'total_qty_net_received': total_qty_net_received}
            elif docs.pr_filter_by == 'group_by_category':
                bsg_pr_lines_group_by_category = bsg_pr_lines.groupby(['pc_name'])
                for key_product_categ, df_product_categ in bsg_pr_lines_group_by_category:
                    qty = 0
                    qty_rfq = 0
                    qty_po = 0
                    qty_received = 0
                    iss_qty = 0
                    qty_returned = 0
                    qty_net_received = 0
                    for key, value in df_product_categ.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id', '=', int(value['pr_line_id']))],
                                                                               limit=1)
                        qty += value['qty']
                        qty_rfq += purchase_req_id.qty_rfq
                        qty_po += value['qty_po']
                        qty_received += value['qty_received']
                        iss_qty += purchase_req_id.iss_qty
                        qty_returned += purchase_req_id.qty_returned
                        qty_net_received += purchase_req_id.qty_net_received
                        total_qty += qty
                        total_qty_rfq += qty_rfq
                        total_qty_po += qty_po
                        total_qty_received += qty_received
                        total_iss_qty += iss_qty
                        total_qty_returned += qty_returned
                        total_qty_net_received += qty_net_received
                        data_dict_list.append(
                            {'product_categ': str(key_product_categ), 'qty': str(qty), 'qty_rfq': str(qty_rfq),
                             'qty_po': str(qty_po), 'qty_received': str(qty_received),
                             'iss_qty': str(iss_qty), 'qty_returned': str(qty_returned),
                             'qty_net_received': str(qty_net_received)})
                data_dict_totals = {'total_qty': total_qty, 'total_qty_rfq': total_qty_rfq,
                                    'total_qty_po': total_qty_po, 'total_qty_received': total_qty_received,
                                    'total_iss_qty': total_iss_qty, 'total_qty_returned': total_qty_returned,
                                    'total_qty_net_received': total_qty_net_received}
            else:
                if docs.pr_filter_by in ['all', 'done_pr', 'open_pr']:
                    for key, value in bsg_pr_lines.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id', '=', int(value['pr_line_id']))],
                                                                               limit=1)
                        total_qty += value['qty']
                        total_qty_rfq += purchase_req_id.qty_rfq
                        total_qty_po += value['qty_po']
                        total_qty_received += value['qty_received']
                        total_iss_qty += purchase_req_id.iss_qty
                        total_qty_returned += purchase_req_id.qty_returned
                        total_qty_net_received += purchase_req_id.qty_net_received
                        data_dict_list.append(
                            {'pr_name': str(value['pr_name']), 'date_pr_line': str(value['date_pr_line']),
                             'pr_line_name': str(value['pr_line_name']),
                             'pc_name': str(value['pc_name']), 'product_id': str(purchase_req_id.product_id.name),
                             'qty': str(value['qty']), 'qty_rfq': str(purchase_req_id.qty_rfq),
                             'qty_po': str(value['qty_po']), 'qty_received': str(value['qty_received']),
                             'iss_qty': str(purchase_req_id.iss_qty), 'qty_returned': str(purchase_req_id.qty_returned),
                             'qty_net_received': str(purchase_req_id.qty_net_received),
                             'department_display_name': str(purchase_req_id.department_id.display_name),
                             'branch_name': str(value['branch_name']), 'request_type': str(value['request_type']),
                             'fleet_num': str(purchase_req_id.fleet_num), 'pr_line_state': str(value['pr_line_state'])})
                    data_dict_totals = {'total_qty': total_qty, 'total_qty_rfq': total_qty_rfq,
                                        'total_qty_po': total_qty_po, 'total_qty_received': total_qty_received,
                                        'total_iss_qty': total_iss_qty, 'total_qty_returned': total_qty_returned,
                                        'total_qty_net_received': total_qty_net_received}
                if docs.pr_filter_by == 'pr_has_rfq_not_po':
                    for key, value in bsg_pr_lines.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id', '=', int(value['pr_line_id']))],
                                                                               limit=1)
                        if purchase_req_id.qty_rfq > 0 and float(value['qty_po']) == 0:
                            total_qty += value['qty']
                            total_qty_rfq += purchase_req_id.qty_rfq
                            total_qty_po += value['qty_po']
                            total_po_price += purchase_req_id.price_total
                            total_invoice_price += purchase_req_id.invoice_total_price
                            vals_list = purchase_req_id.partner_ids.mapped('name')
                            vals = ",".join(vals_list)
                            total_qty_received += value['qty_received']
                            total_iss_qty += purchase_req_id.iss_qty
                            total_qty_returned += purchase_req_id.qty_returned
                            total_qty_net_received += purchase_req_id.qty_net_received
                            data_dict_list.append(
                                {'pr_name': str(value['pr_name']), 'date_pr_line': str(value['date_pr_line']),
                                 'pr_line_name': str(value['pr_line_name']),
                                 'pc_name': str(value['pc_name']),
                                 'product_id': str(purchase_req_id.product_id.name),
                                 'qty': str(value['qty']), 'qty_rfq': str(purchase_req_id.qty_rfq),
                                 'qty_po': str(value['qty_po']), 'po_price': str(purchase_req_id.price_total),
                                 'invoice_total_price': str(purchase_req_id.invoice_total_price), 'vendors': str(vals),
                                 'qty_received': str(value['qty_received']),
                                 'iss_qty': str(purchase_req_id.iss_qty),
                                 'qty_returned': str(purchase_req_id.qty_returned),
                                 'qty_net_received': str(purchase_req_id.qty_net_received),
                                 'department_display_name': str(purchase_req_id.department_id.display_name),
                                 'branch_name': str(value['branch_name']),
                                 'request_type': str(value['request_type']),
                                 'fleet_num': str(purchase_req_id.fleet_num),
                                 'pr_line_state': str(value['pr_line_state'])})
                    data_dict_totals = {'total_qty': total_qty, 'total_qty_rfq': total_qty_rfq,
                                        'total_qty_po': total_qty_po, 'total_po_price': total_po_price,
                                        'total_invoice_price': total_invoice_price,
                                        'total_qty_received': total_qty_received,
                                        'total_iss_qty': total_iss_qty, 'total_qty_returned': total_qty_returned,
                                        'total_qty_net_received': total_qty_net_received}
                if docs.pr_filter_by == 'pr_has_po':
                    for key, value in bsg_pr_lines.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id', '=', int(value['pr_line_id']))],
                                                                               limit=1)
                        if float(value['qty_po']) > 0:
                            total_qty += value['qty']
                            total_qty_rfq += purchase_req_id.qty_rfq
                            total_qty_po += value['qty_po']
                            total_po_price += purchase_req_id.price_total
                            total_invoice_price += purchase_req_id.invoice_total_price
                            vals_list = purchase_req_id.partner_ids.mapped('name')
                            vals = ",".join(vals_list)
                            total_qty_received += value['qty_received']
                            total_iss_qty += purchase_req_id.iss_qty
                            total_qty_returned += purchase_req_id.qty_returned
                            total_qty_net_received += purchase_req_id.qty_net_received
                            data_dict_list.append(
                                {'pr_name': str(value['pr_name']), 'date_pr_line': str(value['date_pr_line']),
                                 'pr_line_name': str(value['pr_line_name']),
                                 'pc_name': str(value['pc_name']),
                                 'product_id': str(purchase_req_id.product_id.name),
                                 'qty': str(value['qty']), 'qty_rfq': str(purchase_req_id.qty_rfq),
                                 'qty_po': str(value['qty_po']), 'po_price': str(purchase_req_id.price_total),
                                 'invoice_total_price': str(purchase_req_id.invoice_total_price), 'vendors': str(vals),
                                 'qty_received': str(value['qty_received']),
                                 'iss_qty': str(purchase_req_id.iss_qty),
                                 'qty_returned': str(purchase_req_id.qty_returned),
                                 'qty_net_received': str(purchase_req_id.qty_net_received),
                                 'department_display_name': str(purchase_req_id.department_id.display_name),
                                 'branch_name': str(value['branch_name']),
                                 'request_type': str(value['request_type']),
                                 'fleet_num': str(purchase_req_id.fleet_num),
                                 'pr_line_state': str(value['pr_line_state'])})
                    data_dict_totals = {'total_qty': total_qty, 'total_qty_rfq': total_qty_rfq,
                                        'total_qty_po': total_qty_po, 'total_po_price': total_po_price,
                                        'total_invoice_price': total_invoice_price,
                                        'total_qty_received': total_qty_received,
                                        'total_iss_qty': total_iss_qty, 'total_qty_returned': total_qty_returned,
                                        'total_qty_net_received': total_qty_net_received}
                if docs.pr_filter_by == 'pr_done_by_store_dept':
                    for key, value in bsg_pr_lines.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id', '=', int(value['pr_line_id']))],
                                                                               limit=1)
                        if value['pr_line_state'] in ['done', 'close'] and float(
                                value['qty_po']) == 0 and purchase_req_id.qty_rfq == 0:
                            data_dict_list.append(
                                {'pr_name': str(value['pr_name']), 'date_pr_line': str(value['date_pr_line']),
                                 'pr_line_name': str(value['pr_line_name']),
                                 'pc_name': str(value['pc_name']),
                                 'product_id': str(purchase_req_id.product_id.name),
                                 'qty': str(value['qty']), 'qty_rfq': str(purchase_req_id.qty_rfq),
                                 'qty_po': str(value['qty_po']), 'qty_received': str(value['qty_received']),
                                 'iss_qty': str(purchase_req_id.iss_qty),
                                 'qty_returned': str(purchase_req_id.qty_returned),
                                 'qty_net_received': str(purchase_req_id.qty_net_received),
                                 'department_display_name': str(purchase_req_id.department_id.display_name),
                                 'branch_name': str(value['branch_name']),
                                 'request_type': str(value['request_type']),
                                 'fleet_num': str(purchase_req_id.fleet_num),
                                 'pr_line_state': str(value['pr_line_state'])})
                    data_dict_totals = {'total_qty': total_qty, 'total_qty_rfq': total_qty_rfq,
                                        'total_qty_po': total_qty_po, 'total_qty_received': total_qty_received,
                                        'total_iss_qty': total_iss_qty, 'total_qty_returned': total_qty_returned,
                                        'total_qty_net_received': total_qty_net_received}
                if docs.pr_filter_by == 'pr_not_received_by_store':
                    for key,value in bsg_pr_lines.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id','=',int(value['pr_line_id']))],limit=1)
                        if float(value['qty_po']) > 0 and float(value['qty_received']) == 0:
                            total_qty += value['qty']
                            total_qty_rfq += purchase_req_id.qty_rfq
                            total_qty_po += value['qty_po']
                            total_qty_received += value['qty_received']
                            total_iss_qty += purchase_req_id.iss_qty
                            total_qty_returned += purchase_req_id.qty_returned
                            total_qty_net_received += purchase_req_id.qty_net_received
                            data_dict_list.append(
                                {'pr_name': str(value['pr_name']), 'date_pr_line': str(value['date_pr_line']),
                                 'pr_line_name': str(value['pr_line_name']),
                                 'pc_name': str(value['pc_name']),
                                 'product_id': str(purchase_req_id.product_id.name),
                                 'qty': str(value['qty']), 'qty_rfq': str(purchase_req_id.qty_rfq),
                                 'qty_po': str(value['qty_po']), 'qty_received': str(value['qty_received']),
                                 'iss_qty': str(purchase_req_id.iss_qty),
                                 'qty_returned': str(purchase_req_id.qty_returned),
                                 'qty_net_received': str(purchase_req_id.qty_net_received),
                                 'department_display_name': str(purchase_req_id.department_id.display_name),
                                 'branch_name': str(value['branch_name']),
                                 'request_type': str(value['request_type']),
                                 'fleet_num': str(purchase_req_id.fleet_num),
                                 'pr_line_state': str(value['pr_line_state'])})
                    data_dict_totals = {'total_qty': total_qty, 'total_qty_rfq': total_qty_rfq,
                                        'total_qty_po': total_qty_po, 'total_qty_received': total_qty_received,
                                        'total_iss_qty': total_iss_qty, 'total_qty_returned': total_qty_returned,
                                        'total_qty_net_received': total_qty_net_received}
                if docs.pr_filter_by == 'pr_has_iss':
                    for key,value in bsg_pr_lines.iterrows():
                        purchase_req_id = self.env['purchase.req.line'].search([('id','=',int(value['pr_line_id']))],limit=1)
                        if purchase_req_id.iss_qty > 0:
                            total_qty += value['qty']
                            total_qty_rfq += purchase_req_id.qty_rfq
                            total_qty_po += value['qty_po']
                            total_qty_received += value['qty_received']
                            total_iss_qty += purchase_req_id.iss_qty
                            total_qty_returned += purchase_req_id.qty_returned
                            total_qty_net_received += purchase_req_id.qty_net_received
                            data_dict_list.append(
                                {'pr_name': str(value['pr_name']), 'date_pr_line': str(value['date_pr_line']),
                                 'pr_line_name': str(value['pr_line_name']),
                                 'pc_name': str(value['pc_name']), 'product_id': str(purchase_req_id.product_id.name),
                                 'qty': str(value['qty']), 'qty_rfq': str(purchase_req_id.qty_rfq),
                                 'qty_po': str(value['qty_po']), 'qty_received': str(value['qty_received']),
                                 'iss_qty': str(purchase_req_id.iss_qty), 'qty_returned': str(purchase_req_id.qty_returned),
                                 'qty_net_received': str(purchase_req_id.qty_net_received),
                                 'department_display_name': str(purchase_req_id.department_id.display_name),
                                 'branch_name': str(value['branch_name']), 'request_type': str(value['request_type']),
                                 'fleet_num': str(purchase_req_id.fleet_num), 'pr_line_state': str(value['pr_line_state'])})



            return {
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,
                'filter_by': filter_by,
                'data_dict_totals': data_dict_totals,
                'data_dict_list': data_dict_list
            }
