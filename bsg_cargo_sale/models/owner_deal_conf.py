# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class OwnerDealConf(models.Model):
    _name = 'owner_deal_conf'
    _description = "Owner Deal"
    _inherit = ['mail.thread']
    _rec_name = 'owner_deal_name'

    owner_deal_name = fields.Char(string="Owner Deal Name", required=True, track_visibility=True)
    commercial_number = fields.Char(string="Commercial Number", track_visibility=True)

    @api.constrains('commercial_number')
    def commercial_number_constraints(self):
        for data in self:
            if data.commercial_number:
                commercial_number = str(data.commercial_number)
                search_param = commercial_number.casefold()
                search_param_upper = commercial_number.upper()
                search_id = self.search(
                    ['|', ('commercial_number', '=', search_param_upper), ('commercial_number', '=', search_param)])
                if len(search_id) > 1:
                    raise UserError('Commercial Number Must Be Unique..!')
