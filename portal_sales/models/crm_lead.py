# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class crmLead(models.Model):
    _inherit = 'crm.lead'

    loc_from = fields.Many2one("bsg_route_waypoints","Location From", track_visibility=True)
    loc_to = fields.Many2one("bsg_route_waypoints", "Location To",track_visibility=True)
    car_make = fields.Many2one(
        string="Car Maker", comodel_name="bsg_car_config", track_visibility=True)
    car_model = fields.Many2one("bsg_car_model",string="Car Model",track_visibility=True)
    car_size = fields.Many2one("bsg_car_size","Car Size",track_visibility=True,compute="_get_car_size",store=True,compute_sudo=True)
    car_classfication = fields.Many2one(string="Car Classfication", comodel_name="bsg_car_classfication",
                                        compute="_get_car_size",store=True,compute_sudo=True)
    partner_type = fields.Selection([('individual', 'Individual'), (
        'corporate', 'Corporates')], string='Partner Type')
    contract_id = fields.Many2one('bsg_customer_contract', string='Contract')
    car_count = fields.Integer("Car Count")
    attachment_ids = fields.Many2many('ir.attachment')
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",compute="_compute_order_currency",store=True,compute_sudo=True)

    def get_portal_url(self):
        portal_link = "%s/my/requests/%s" % (self.env['ir.config_parameter'].sudo().get_param('web.base.url'), self.id)
        return portal_link

    @api.depends("car_model")
    def _get_car_size(self):
        if self.car_model and self.car_make:
            for car_line in self.car_make.car_line_ids:
                if car_line.car_model.id == self.car_model.id:
                    self.car_size = car_line.car_size.id
                    self.car_classfication = car_line.car_classfication.id


    @api.depends("loc_from","company_id")
    def _compute_order_currency(self):
        if self.company_id and self.loc_from:
            if self.loc_from.is_international:
                self.currency_id = self.loc_from.loc_branch_id.currency_id.id
            else:
                self.currency_id = self.company_id.currency_id.id    