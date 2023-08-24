# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ReportHistoryDelivery(models.Model):
  _name = 'report.history.delivery'
  _description = "Delivery Report History"
  _inherit = ['mail.thread']
  _rec_name = "dr_print_no"

  active = fields.Boolean(string="Active", track_visibility=True, default=True)
  dr_print_no = fields.Char( string='Seq#',)
  dr_user_id = fields.Many2one(string="User Name", comodel_name="res.users")
  dr_print_date = fields.Datetime( string='Print Date',)
  cargo_so_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', string='CSO line') 
  number = fields.Char(string="Number" , related="cargo_so_line_id.delivery_note_no")
  act_receiver_name = fields.Char(string="Actual Receiver Name")
  exit_by = fields.Many2one(string="Exit By", comodel_name="res.partner")
  exit_date = fields.Datetime(string='Exit Date')

  @api.onchange('exit_by')
  def change_exit_date(self):
    self.exit_date = fields.Date.today()
