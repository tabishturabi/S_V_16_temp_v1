# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError

class ItemsGatepass(models.Model):
    _name = 'item.gatepass'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Items Gatepass'
    _rec_name="name"

    name = fields.Char(string='Sequence', track_visibility='onchange')
    company_id = fields.Many2one('res.partner', 'Company', required=True)
    driver_name = fields.Char(string='Driver Name',track_visibility='onchange')
    project_name = fields.Char(string='Project Name',track_visibility='onchange')
    work_order = fields.Char(string='Work Order',track_visibility='onchange')
    delivery_note_no = fields.Char(string='Delivery Note Number',track_visibility='onchange')
    delivery_name = fields.Char(string='Delivery Name',track_visibility='onchange')
    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    pass_from = fields.Selection(string="From", default="plant1", selection= [('plant1', 'Plant 1'), ('plant2', 'Plant 2')], required=True,track_visibility='onchange')
    pass_to = fields.Selection(string="To", default="customer", selection= [('customer', 'Customer'), ('vendor_manufacture', 'Vendor Manufacture'), ('plant1', 'Plant 1'), ('plant2', 'Plant 2')], required=True,track_visibility='onchange')
    status = fields.Selection(string="Status", default="delivery", selection= [('returnable', 'Returnable'), ('non_returnable', 'Non-Returnable'), ('modification', 'Modification'), ('galvanizing', 'Galvanizing'), ('transfer', 'Transfer'), ('delivery', 'Delivery')],track_visibility='onchange', required=True)
    state = fields.Selection(string="State", default="draft", selection= [('draft', 'Draft'),('finanace_approval', ' Finance Approval'),('op_manager_approval', 'Operation Manager Approval'),('done', 'Done')],track_visibility='onchange')
    line_ids = fields.One2many(comodel_name="item.gatepass.line", inverse_name="gatepass_id", string="Gatepass Lines")
    refusal_reason = fields.Text(string="Refuse Reason",track_visibility='onchange')
    notes = fields.Text(string='Notes', track_visibility=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('items_gatepass_code') or _('New')
        res = super(ItemsGatepass, self).create(vals)
        return res

    @api.constrains('pass_from','pass_to','status')
    def pass_validation(self):
        for rec in self:
            if (rec.pass_from == 'plant1' and rec.pass_to == 'plant1') or (rec.pass_from == 'plant2' and rec.pass_to == 'plant2'):
                raise ValidationError("Pass From and Pass To Can hold same Destinations")
            if rec.pass_from in ['plant2','plant1'] and rec.pass_to in ['plant2','plant1'] and rec.status in ['galvanizing','delivery']:
                raise ValidationError("Status Can not be galvanizing or delivery for these Passes")


    def action_confirm(self):
        for rec in self:
            if rec.pass_to == 'customer':
                rec.state = 'finanace_approval'
            else:
                rec.state = 'op_manager_approval'

    def action_finance_approve(self):
        for rec in self:
            rec.state = 'done'

    def action_op_manager_approve(self):
        for rec in self:
            rec.state = 'done'



class ItemsGatePassLine(models.Model):
    _name = 'item.gatepass.line'

    gatepass_id = fields.Many2one('item.gatepass',string='Gatepass Line')
    item_description = fields.Char(string='Item Description',required=True)
    item_qty = fields.Float(string='Qty')
    item_weight = fields.Float(string='Item Weight')
    remarks = fields.Char(string='Remarks')





