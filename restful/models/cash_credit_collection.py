from odoo import models, fields, api, _


class CashCreditCollection(models.Model):
    _name = 'driver.cash.credit.collection'
    _rec_name = 'collection_reference'

    collection_reference = fields.Char('Collection Reference', index=True, copy=False, default='New')
    driver_id = fields.Many2one('hr.employee', string="Driver")
    customer_id = fields.Many2one('res.partner', 'Customer')
    cargo_sale_line_id = fields.Many2one('bsg_vehicle_cargo_sale_line', 'Cargo Sale Line')
    collection_method = fields.Selection(
        [
            ('cash', 'Cash'),
            ('credit', 'Credit'),
        ], string='Collection Method', track_visibility='onchange')
    collected_amount = fields.Float(string="Collected Amount")
    so_total_amount = fields.Float(string="Total Amount")
    so_paid_amount = fields.Float(string="Paid Amount")
    so_due_amount = fields.Float(string="Due Amount")
    reason = fields.Text(string="Reason")
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('processed', 'Processed'), ('declined', 'declined')],
                             default='draft', track_visibility='always')
    payment_id = fields.Many2one('account.payment', readonly=True)

    
    def confirm(self):
        self.write({'state': 'processed'})

    
    def decline(self):
        self.write({'state': 'declined'})

    
    def reset_to_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        # if not vals.get('collection_reference') or vals['collection_reference'] == _('New'):
        vals['collection_reference'] = self.env['ir.sequence'].next_by_code('dcc.collection.seq') or _('New')
        return super(CashCreditCollection, self).create(vals)
        
    
    def register_payment(self):
        sale_id = self.cargo_sale_line_id.bsg_cargo_sale_id
        return sale_id.with_context({'active_id': sale_id.id, 'driver_collection_id': self.id}).register_payment()