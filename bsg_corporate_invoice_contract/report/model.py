# -*- coding:utf-8 -*-

from odoo import api, models
from num2words import num2words
import base64
import re


class Reportmonthcollection(models.AbstractModel):
    _name = 'report.bsg_corporate_invoice_contract.credit_collection_report'
    _description = "Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['credit.customer.collection'].browse(docids)
        user = self.env['res.users'].search([('id', '=', self._uid)])

        print('.................docs..............',docs)
        def number_to_spell(attrb):
            if self.env.user.lang == "en_US":
                rword = num2words((attrb))
                rword = rword.title() + " " + "SAR Only"
            else:
                currency_id = self.env.user.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).company_id.currency_id
                rword = num2words(float("%.2f" % attrb), lang='ar')
                rword = rword.title()
                warr = str(("%.2f" % attrb)).split('.')
                if currency_id.name == 'SAR':
                    ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
                    rword = str(rword).replace(',', ' ريال و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                elif currency_id.name == 'AED':
                    ar = ' درهم' if str(warr[1]) == '00' else ' فلس'
                    rword = str(rword).replace(',', ' درهم و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                elif currency_id.name == 'JOD':
                    ar = ' دينار' if str(warr[1]) == '00' else ' فلس'
                    rword = str(rword).replace(',', ' دينار و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                elif currency_id.name == 'OMR':
                    ar = ' ريال' if str(warr[1]) == '00' else ' بيسة'
                    rword = str(rword).replace(',', ' ريال و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                else:
                    ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
                    rword = str(rword).replace(',', ' ريال و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
            return rword

        report_value = 0

        lang_id = 0
        user_id = self.env['res.users'].search([('id', '=', self._uid)])
        if user_id.lang != 'en_US':
            lang_id = 1

        cust_info = []
        if docs.invoice_to:
            cust_info = docs.invoice_to
        else:
            cust_info = docs.customer_id

        cargo_ids = []
        for d in docs.cargo_sale_line_ids:
            cargo_ids.append(d)

        if docs.report_branch_wise:
            cargo_ids = sorted(cargo_ids, key=lambda k: (int(k.loc_from.loc_branch_id.branch_no), k.id))
        elif docs.report_branch_wise_delivery:
            cargo_ids = sorted(cargo_ids, key=lambda k: (int(k.loc_to.loc_branch_id.branch_no), k.id))
        else:
            cargo_ids = sorted(cargo_ids, key=lambda k: k.report_seq)

        num_of_recs = len(cargo_ids)

        net = 0
        tax = 0
        total = 0
        unittotal = 0
        other_service_total = 0
        for tot in cargo_ids:
            net = net + tot.charges + sum(tot.other_service_ids.mapped('cost')) + sum(
                tot.other_service_ids.mapped('tax_amount'))
            other_service_total = other_service_total + sum(tot.other_service_ids.mapped('cost'))
            tax = tax + tot.tax_amount + sum(tot.other_service_ids.mapped('tax_amount'))
            total = total + tot.total_without_tax + sum(tot.other_service_ids.mapped('cost'))
            unittotal = unittotal + tot.unit_charge + tot.additional_ship_amount

        # if lang_id == 0:
        def get_cargo_ids(attr):
            len_check = 18 * int(attr)
            if len(cargo_ids) <= len_check:
                start_range = int(len_check - 18)
                return cargo_ids[start_range:]
            if len(cargo_ids) > len_check:
                start_range = int(len_check - 18)
                return cargo_ids[start_range:len_check]

        check_loops = len(cargo_ids) % 18

        runing_loop = 1
        exact_loop = 1
        if cargo_ids:
            runing_loop = float(int(len(cargo_ids)) / 18)
            runing_loop = format(runing_loop, '.2f')
            runing_loop = float(runing_loop)
            txt = str(runing_loop)
            txt = (txt.split("."))
            txt = int(txt[-1])
            if txt > 50 or txt == 0:
                report_value = 1
                int_value = int(runing_loop)
                if runing_loop > int_value:
                    exact_loop = int_value + 2
                else:
                    exact_loop = int_value + 1

            else:
                report_value = 2
                int_value = int(runing_loop)
                if runing_loop > int_value:
                    exact_loop = int_value + 1
                else:
                    exact_loop = int_value

        # else:

        # 	print ("3333333333333333333333")
        # 	print ("3333333333333333333333")
        # 	print ("3333333333333333333333")
        # 	print ("3333333333333333333333")

        # 	report_value = 2

        # 	runing_loop = 1
        # 	exact_loop = 1
        # 	if cargo_ids:
        # 		runing_loop = int(len(cargo_ids)) / 18
        # 		int_value = int(runing_loop)
        # 		if runing_loop > int_value:
        # 			exact_loop = int_value + 1
        # 		else:
        # 			exact_loop = int_value

        # else:
        # 	def get_cargo_ids(attr):
        # 		len_check = 34 * int(attr)
        # 		if len(cargo_ids) <= len_check:
        # 			start_range = int(len_check - 34)
        # 			return cargo_ids[start_range:]
        # 		if len(cargo_ids) > len_check:
        # 			start_range = int(len_check - 34)
        # 			return cargo_ids[start_range:len_check]

        # 	check_loops = len(cargo_ids) % 34
        # 	if check_loops > 17:

        # 		report_value = 1

        # 		runing_loop = 1
        # 		exact_loop = 1
        # 		if cargo_ids:
        # 			runing_loop = int(len(cargo_ids)) / 34
        # 			int_value = int(runing_loop)
        # 			if runing_loop > int_value:
        # 				exact_loop = int_value + 2
        # 			else:
        # 				exact_loop = int_value + 1

        # 	else:

        # 		report_value = 2

        # 		runing_loop = 1
        # 		exact_loop = 1
        # 		if cargo_ids:
        # 			runing_loop = int(len(cargo_ids)) / 34
        # 			int_value = int(runing_loop)
        # 			if runing_loop > int_value:
        # 				exact_loop = int_value + 1
        # 			else:
        # 				exact_loop = int_value

        page_numz = []
        for ex in range(exact_loop):
            page_numz.append(ex + 1)

        comp_partner_id = self.env.user.company_id.partner_id.id
        # ir_translation_arr = self.env['ir.translation'].search(
        #     [('name', '=', 'res.partner,street'),('res_id', '=', comp_partner_id), ('lang', '=', 'ar_001')]).value
        # ir_translation_eng = self.env['ir.translation'].search(
        #     [('name', '=', 'res.partner,street'),('res_id', '=', comp_partner_id), ('lang', '=', 'en_US')]).source
        print('..............report_value.............',report_value)
        return {
            # 'company_address': ir_translation_arr if self.env.user.lang == 'ar_001' else ir_translation_eng,
            'doc_ids': docids,
            'doc_model': 'credit.customer.collection',
            'data': data,
            'docs': docs,
            'user': user,
            'number_to_spell': number_to_spell,
            'lang_id': lang_id,
            'cargo_ids': cargo_ids,
            'page_numz': page_numz,
            'get_cargo_ids': get_cargo_ids,
            'exact_loop': exact_loop,
            'cust_info': cust_info,
            'num_of_recs': num_of_recs,
            'net': net,
            'other_service_total': other_service_total,
            'tax': tax,
            'total': total,
            'unittotal': unittotal,
            'report_value': report_value,
            # 'get_prf': get_prf,
            # 'get_po': get_po,
        }


class Reporttaxcollection(models.AbstractModel):
    _name = 'report.bsg_corporate_invoice_contract.credit_collect_qr_report'
    _description = "Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['credit.customer.collection'].browse(docids)
        user = self.env['res.users'].search([('id', '=', self._uid)])

        def number_to_spell(attrb):
            if self.env.user.lang == "en_US":
                rword = num2words((attrb))
                rword = rword.title() + " " + "SAR Only"
            else:
                currency_id = self.env.user.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).company_id.currency_id
                rword = num2words(float("%.2f" % attrb), lang='ar')
                rword = rword.title()
                warr = str(("%.2f" % attrb)).split('.')
                if currency_id.name == 'SAR':
                    ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
                    rword = str(rword).replace(',', ' ريال و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                elif currency_id.name == 'AED':
                    ar = ' درهم' if str(warr[1]) == '00' else ' فلس'
                    rword = str(rword).replace(',', ' درهم و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                elif currency_id.name == 'JOD':
                    ar = ' دينار' if str(warr[1]) == '00' else ' فلس'
                    rword = str(rword).replace(',', ' دينار و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                elif currency_id.name == 'OMR':
                    ar = ' ريال' if str(warr[1]) == '00' else ' بيسة'
                    rword = str(rword).replace(',', ' ريال و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
                else:
                    ar = ' ريال' if str(warr[1]) == '00' else ' هلله'
                    rword = str(rword).replace(',', ' ريال و ') + ar
                    # rword = str(rword).replace('ريال و ', 'فاصلة')
            return rword

        report_value = 0

        lang_id = 0
        user_id = self.env['res.users'].search([('id', '=', self._uid)])
        if user_id.lang != 'en_US':
            lang_id = 1

        cust_info = []
        if docs.invoice_to:
            cust_info = docs.invoice_to
        else:
            cust_info = docs.customer_id

        cargo_ids = []
        for d in docs.cargo_sale_line_ids:
            cargo_ids.append(d)

        if docs.report_branch_wise:
            cargo_ids = sorted(cargo_ids, key=lambda k: (int(k.loc_from.loc_branch_id.branch_no), k.id))
        elif docs.report_branch_wise_delivery:
            cargo_ids = sorted(cargo_ids, key=lambda k: (int(k.loc_to.loc_branch_id.branch_no), k.id))
        else:
            cargo_ids = sorted(cargo_ids, key=lambda k: k.report_seq)

        num_of_recs = len(cargo_ids)

        net = 0
        tax = 0
        total = 0
        unittotal = 0
        other_service_total = 0
        for tot in cargo_ids:
            net = net + tot.charges + sum(tot.other_service_ids.mapped('cost')) + sum(
                tot.other_service_ids.mapped('tax_amount'))
            other_service_total = other_service_total + sum(tot.other_service_ids.mapped('cost'))
            tax = tax + tot.tax_amount + sum(tot.other_service_ids.mapped('tax_amount'))
            total = total + tot.total_without_tax + sum(tot.other_service_ids.mapped('cost'))
            unittotal = unittotal + tot.unit_charge + tot.additional_ship_amount

        # if lang_id == 0:
        def get_cargo_ids(attr):
            len_check = 18 * int(attr)
            if len(cargo_ids) <= len_check:
                start_range = int(len_check - 18)
                return cargo_ids[start_range:]
            if len(cargo_ids) > len_check:
                start_range = int(len_check - 18)
                return cargo_ids[start_range:len_check]

        check_loops = len(cargo_ids) % 18

        runing_loop = 1
        exact_loop = 1
        if cargo_ids:
            runing_loop = float(int(len(cargo_ids)) / 18)
            runing_loop = format(runing_loop, '.2f')
            runing_loop = float(runing_loop)
            txt = str(runing_loop)
            txt = (txt.split("."))
            txt = int(txt[-1])
            if txt > 50 or txt == 0:
                report_value = 1
                int_value = int(runing_loop)
                if runing_loop > int_value:
                    exact_loop = int_value + 2
                else:
                    exact_loop = int_value + 1

            else:
                report_value = 2
                int_value = int(runing_loop)
                if runing_loop > int_value:
                    exact_loop = int_value + 1
                else:
                    exact_loop = int_value

        # else:

        # 	print ("3333333333333333333333")
        # 	print ("3333333333333333333333")
        # 	print ("3333333333333333333333")
        # 	print ("3333333333333333333333")

        # 	report_value = 2

        # 	runing_loop = 1
        # 	exact_loop = 1
        # 	if cargo_ids:
        # 		runing_loop = int(len(cargo_ids)) / 18
        # 		int_value = int(runing_loop)
        # 		if runing_loop > int_value:
        # 			exact_loop = int_value + 1
        # 		else:
        # 			exact_loop = int_value

        # else:
        # 	def get_cargo_ids(attr):
        # 		len_check = 34 * int(attr)
        # 		if len(cargo_ids) <= len_check:
        # 			start_range = int(len_check - 34)
        # 			return cargo_ids[start_range:]
        # 		if len(cargo_ids) > len_check:
        # 			start_range = int(len_check - 34)
        # 			return cargo_ids[start_range:len_check]

        # 	check_loops = len(cargo_ids) % 34
        # 	if check_loops > 17:

        # 		report_value = 1

        # 		runing_loop = 1
        # 		exact_loop = 1
        # 		if cargo_ids:
        # 			runing_loop = int(len(cargo_ids)) / 34
        # 			int_value = int(runing_loop)
        # 			if runing_loop > int_value:
        # 				exact_loop = int_value + 2
        # 			else:
        # 				exact_loop = int_value + 1

        # 	else:

        # 		report_value = 2

        # 		runing_loop = 1
        # 		exact_loop = 1
        # 		if cargo_ids:
        # 			runing_loop = int(len(cargo_ids)) / 34
        # 			int_value = int(runing_loop)
        # 			if runing_loop > int_value:
        # 				exact_loop = int_value + 1
        # 			else:
        # 				exact_loop = int_value

        page_numz = []
        for ex in range(exact_loop):
            page_numz.append(ex + 1)

        comp_partner_id = self.env.user.company_id.partner_id.id
        # ir_translation_arr = self.env['ir.translation'].search(
        #     [('name', '=', 'res.partner,street'),('res_id', '=', comp_partner_id), ('lang', '=', 'ar_001')]).value
        # ir_translation_eng = self.env['ir.translation'].search(
        #     [('name', '=', 'res.partner,street'),('res_id', '=', comp_partner_id), ('lang', '=', 'en_US')]).source
        return {
            # 'company_address': ir_translation_arr if self.env.user.lang == 'ar_001' else ir_translation_eng,
            'doc_ids': docids,
            'doc_model': 'credit.customer.collection',
            'data': data,
            'docs': docs,
            'user': user,
            'number_to_spell': number_to_spell,
            'lang_id': lang_id,
            'cargo_ids': cargo_ids,
            'page_numz': page_numz,
            'get_cargo_ids': get_cargo_ids,
            'exact_loop': exact_loop,
            'cust_info': cust_info,
            'num_of_recs': num_of_recs,
            'net': net,
            'other_service_total': other_service_total,
            'tax': tax,
            'total': total,
            'unittotal': unittotal,
            'report_value': report_value,
            # 'get_prf': get_prf,
            # 'get_po': get_po,
        }
