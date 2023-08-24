# -*- coding: utf-8 -*-

import time
from datetime import datetime
import tempfile
import binascii
import xlrd
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging

_logger = logging.getLogger(__name__)
import io

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportProducts(models.TransientModel):
    _name = "import.products"
    _description = "Import products"

    File_slect = fields.Binary(string="Select Excel File")
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='csv')

    # @api.multi
    def imoport_file(self, default_code=None, standard_price=None, field=None, type=None, taxes_id=None,
                     supplier_taxes_id=None):

        # -----------------------------
        global res
        if self.import_option == 'csv':

            keys = ['type', 'name', 'categ_id']

            try:
                csv_data = base64.b64decode(self.File_slect)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                values = {}
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)

            except:

                raise Warning(_("Invalid file!"))

            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({
                            'name': field[0],
                            'purchase_ok': field[1],
                            'default_code': field[2],
                            'standard_price': field[3],
                            'type': field[4],
                            'uom_id': field[5],
                            'uom_po_id': field[6],
                            'categ_id': field[7],
                            'taxes_id': field[8],
                            'supplier_taxes_id': field[9],
                            'sale_ok': field[10],

                        })
                        res = self.create_products(values)

        # ---------------------------------------
        elif self.import_option == 'xls':
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.File_slect))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)

            except:
                raise Warning(_("Invalid file!"))

            for row_no in range(sheet.nrows):
                values = {}
                if row_no <= 0:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:

                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))

                    values.update({
                        'name': field[0],
                        'purchase_ok': field[1],
                        'default_code': field[2],
                        'standard_price': field[3],
                        'type': field[4],
                        'uom_id': field[5],
                        'uom_po_id': field[6],
                        'categ_id': field[7],
                        'taxes_id': field[8],
                        'supplier_taxes_id': field[9],
                        'sale_ok': field[10],

                    })
                    res = self.create_products(values)
        # ------------------------------------------------------------
        else:
            raise Warning(_("Please select any one from xls or csv formate!"))

        return res

    # @api.multi
    def create_products(self, values, tax_ids=None):
        if values.get("name") == "":
            raise Warning(_('Name field cannot be empty.'))

        if values.get("type") == "":
            raise Warning(_('Type field cannot be empty.'))
        if values.get("taxes_id") == "":
            values['taxes_id'] = False
        if values.get("supplier_taxes_id") == "":
            values['supplier_taxes_id'] = False

        if values.get("categ_id") == "":
            raise Warning(_('Category field cannot be empty.'))
        product_obj = self.env['product.template']
        # product_obj.search([
        #     ('name', '=', values.get('name'))
        # ])

        purchase_ok = False
        sale_ok = False

        if values.get("purchase_ok") == 'TRUE' or values.get("purchase_ok") == "1":
            purchase_ok = True

        if values.get("sale_ok") == 'TRUE' or values.get("sale_ok") == "1":
            sale_ok = True
        product_types = {
            'Storable Product': 'product',
            'Consumable': 'consu',
            'Service': 'service'

        }
        uom_id = self.find_product_uom(values.get('uom_id'))
        uom_po_id = self.find_product_po_uom(values.get('uom_po_id'))
        product_type = values.get('type', False) and product_types.get(values.get('type'), False) or False
        if not product_type:
            raise Warning(_('Field product Type is not correctly set.'))

        parent_id = self.find_parent_id(values.get('categ_id'))
        tax_cus = self.find_tac_cus_id(values.get('taxes_id'))
        # if not tax_cus:
        #     raise Warning(_('Field Tax Type is not correctly set.'))
        tax_sup = self.find_tac_cus_id(values.get('supplier_taxes_id'))
        # if not tax_sup:
        #     raise Warning(_('Field Tax Type is not correctly set.'))

        data = dict(name=values.get('name'),
                    purchase_ok=purchase_ok,
                    standard_price=values.get('standard_price') or False,
                    default_code=values.get('default_code') or False,
                    uom_id=uom_id.id or False,
                    uom_po_id=uom_po_id.id or False,
                    type=product_type or False,
                    categ_id=parent_id or False,
                    taxes_id=[(6, 0, [y.id for y in tax_cus])] if tax_cus else False,
                    supplier_taxes_id=[(6, 0, [y.id for y in tax_sup])] if tax_sup else False,
                    sale_ok=sale_ok)

        pro_id = product_obj.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).create(data)
        # if values.get('parent_id'):
        #  if parent_id:
        # pro_id.parent_id = parent_id
        return pro_id

    # ---------------------------uom-----------------

    # @api.multi
    def find_product_uom(self, uom_id):
        user_type = self.env["uom.uom"]
        user_search = user_type.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('name', '=', uom_id)], limit=1)
        if user_search:
            return user_search
        else:
            raise Warning(_('Field product uom is not correctly set.'))

    # ---------------------------uom for purchase-----------------

    # @api.multi
    def find_product_po_uom(self, uom_po_id):
        user_type = self.env["uom.uom"]
        user_search = user_type.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('name', '=', uom_po_id)], limit=1)
        if user_search:
            return user_search
        else:
            raise Warning(_('Field product purchase uom not correctly set'))

    # ---------------------------parent-----------------

    # @api.multi
    def find_parent_id(self, parent=None):
        accounts = self.env["product.category"]
        parent_search = accounts.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('complete_name', '=', parent)], limit=1)
        if parent_search:
            return parent_search.id
        else:
            return False

    # --------------------Type------------------

    # @api.multi
    # def find_product_type(self, name):
    #     product_obj = self.env['product.template']
    #     type_search = product_obj.search([('type', '=', name)], limit=1)
    #     if type_search:
    #         return type_search.id
    #     else:
    #         return False
    # @api.multi
    def find_tac_cus_id(self, tax):
        accounts = self.env['account.tax']
        tax_search = accounts.sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).search([('id', '=', tax)], limit=1)
        if tax_search:
            return tax_search
        else:
            return False
