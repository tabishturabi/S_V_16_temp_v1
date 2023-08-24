# -*- coding: utf-8 -*-

# from datetime import datetime

from odoo import api, fields, models, _
# from odoo.exceptions import AccessError, UserError, ValidationError


class QualityCheck(models.Model):
    _name = "bsg.quality.check"
    _description = "Bsg Quality Check"
    _inherit = ['mail.thread']

    name = fields.Char('Name', default=lambda self: _('New'))
    title = fields.Char('Title')
    # production_state = fields.Selection([
    #     ('1', 'Draft'),
    #     ('2', 'Preparation Cutting/ Drilling'),
    #     ('3', 'Assembly & Tack Welding'),
    #     ('4', 'Finishing / Grinding'),
    #     ('5', 'Welding Inspection (Visual/MPI/UT)'),
    #     ('6', 'Blasting/Painting'),
    #     ('5', 'Done)'), ], string='State',
    #     copy=False, default='1', track_visibility='onchange')
    # quality_state = fields.Selection([
    #     ('none', 'To do'),
    #     ('pass', 'Passed'),
    #     ('fail', 'Failed')], string='Status', track_visibility='onchange',
    #     default='none', copy=False)
    # control_date = fields.Datetime('Control Date', track_visibility='onchange')
    # # product_id = fields.Many2one(
    # #     'product.product', 'Product',
    # #     domain="[('type', 'in', ['consu', 'product'])]", required=True)
    # project_id = fields.Many2one('bsg.mrp.project', 'Project', readonly=True)
    # user_id = fields.Many2one('res.users', 'Responsible', track_visibility='onchange',
    #                           default=lambda self: self.env.user.id)
    # company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    # manufacturing_order_id = fields.Many2one('bsg.mrp.production', 'Manufacturing Order')
    # note = fields.Html("Notes")
    # company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    # @api.model
    # def create(self, vals):
    #     if 'name' not in vals or vals['name'] == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('bsg.mrp.production.qc.seq') or _('New')
    #     return super(QualityCheck, self).create(vals)
    #
    # # @api.multi
    # def do_fail(self):
    #     if self.manufacturing_order_id:
    #         self.manufacturing_order_id.write({'is_send_to_qc': False})
    #     self.write({
    #         'quality_state': 'fail',
    #         'user_id': self.env.user.id,
    #         'control_date': datetime.now()})
    #     return self.redirect_after_pass_fail()
    #
    # # @api.multi
    # def do_pass(self):
    #     if self.manufacturing_order_id:
    #         self.manufacturing_order_id.write({'is_send_to_qc': True})
    #     self.write({'quality_state': 'pass',
    #                 'user_id': self.env.user.id,
    #                 'control_date': datetime.now()})
    #     return self.redirect_after_pass_fail()
    #
    # def redirect_after_pass_fail(self):
    #     return {'type': 'ir.actions.act_window_close'}
    #
    # # @api.multi
    # def unlink(self):
    #     for rec in self:
    #         if rec.manufacturing_order_id.state == '7':
    #             raise ValidationError(_('You can not delete a record! with Order in Done state created'))
    #         else:
    #             rec.manufacturing_order_id.write({'is_send_to_qc': False})
    #     return super(QualityCheck, self).unlink()
