from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime

class BsgVehicleCargoSaleLine(models.Model):
    _inherit = 'bsg_vehicle_cargo_sale_line'
  
    #cron job method
    def _update_credit_collection_id(self):
        for data in self.search([('add_to_cc','=',True),('credit_collection_id','=',False)],limit=500):
            if data.add_to_cc and not data.credit_collection_id:
                credit_collection_id = self.env['credit.customer.collection'].search([('cargo_sale_line_ids','=',data.id)])
                data.update({'credit_collection_id' : credit_collection_id.id})

    #for couting total number of collection has been userd
    
    def _get_total_collection(self):
        self.customer_collection_count = self.env['credit.customer.collection'].search_count([('cargo_sale_line_ids','=',self.id)])
    
    add_to_cc = fields.Boolean(string="ADD TO CC", default=False)
    customer_collection_count = fields.Integer(string="Total Customer Collection", compute="_get_total_collection")
    credit_collection_id = fields.Many2one('credit.customer.collection',string="Credit Customer Collection")
    credit_collection_ids = fields.Many2many('credit.customer.collection',string="Credit Collections")
    report_seq = fields.Integer(string="Collection Report Seq.")
    has_pickup_other_services = fields.Boolean(compute='_has_pickup_and_delivery_other_services',store=True,compute_sudo=True)
    has_delivery_other_services = fields.Boolean(compute='_has_pickup_and_delivery_other_services',store=True,compute_sudo=True)

    
    @api.depends('other_service_ids.product_id')
    def _has_pickup_and_delivery_other_services(self):
        for rec in self:
            if rec.bsg_cargo_sale_id.customer_contract and rec.bsg_cargo_sale_id.customer_contract.internal_shipment_pirce > 0:
                if not rec.other_service_ids.filtered(lambda s:s.product_id.is_home_pickup):
                    rec.has_pickup_other_services = False
                else: 
                    rec.has_pickup_other_services = True   
                if not rec.other_service_ids.filtered(lambda s:s.product_id.is_home_delivery):
                    rec.has_delivery_other_services = False
                else:
                    rec.has_delivery_other_services = True    
            else:  
                rec.has_pickup_other_services = True  
                rec.has_delivery_other_services = True

    # View Customer collection
    
    def action_view_customer_collection(self):
        credit_collection_id = self.env['credit.customer.collection'].search([('cargo_sale_line_ids','=',self.id)])
        action = self.env.ref('bsg_corporate_invoice_contract.action_credit_customer_collection').read()[0]
        if len(credit_collection_id) > 1:
            action['domain'] = [('id', 'in', credit_collection_id.ids)]
        elif len(credit_collection_id) == 1:
            action['views'] = [(self.env.ref('bsg_corporate_invoice_contract.view_credit_customer_form').id, 'form')]
            action['res_id'] = credit_collection_id.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    
    def cc_create_delivery_history(self):
        seq = 1
        next_seq_code = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code('bsg_vehicle_cargo_sale_line_delivery')
        if self.loc_to:
            if not self.delivery_note_no:
                self.release_date = fields.datetime.now()
                self.delivery_note_no = "99" + str(next_seq_code)
        if self.return_loc_to:
            if not self.delivery_note_no:
                self.release_date = fields.datetime.now()
                self.delivery_note_no = "99" + str(next_seq_code)
        if not self.delivery_report_history_ids:
            self.delivery_report_history_ids.create({
                'dr_print_no': seq,
                'dr_user_id': 1,
                'dr_print_date': datetime.now(),
                'cargo_so_line_id': self.id,
                'act_receiver_name': self.receiver_name,
                'number': self.delivery_note_no,
            })
        else:
            seq = self.delivery_report_history_ids[-1].dr_print_no
            self.delivery_report_history_ids.create({
                'dr_print_no': int(seq) + 1,
                'dr_user_id': 1,
                'dr_print_date': datetime.now(),
                'cargo_so_line_id': self.id,
                'act_receiver_name': self.receiver_name,
                'number': self.delivery_note_no,
            })
        self.write({'state':'done'})
