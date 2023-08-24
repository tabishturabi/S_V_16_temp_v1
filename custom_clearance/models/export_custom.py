# -*- coding: utf-8 -*-

from odoo import fields,models,api,_
from datetime import date
from datetime import datetime
from odoo.addons import decimal_precision as dp

class ExportCustom(models.Model):
    _name= 'export.custom'
    _description = "Export Custom Clearance"
    _rec_name= 'name'
    
    
    name = fields.Char('Name')
    number = fields.Char(string='SR No')
    our_job_no = fields.Char(string='Our Job No')
    date = fields.Date('Date',default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pre', 'Pre Bayan'),
        ('initial', 'Initial Bayan'),
        ('final', 'Final Bayan'),
        ('custom_exam','Custom Examination'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done'),
        ], string='State', default='draft')
    site = fields.Many2one('bsg_route_waypoints',string='Site')
    customer = fields.Many2one('res.partner',string="Customer",domain = [('parent_id','=',False),('supplier_rank','=',0),('customer_rank','>',0)])
    # acc_link = fields.Many2one('account.move',string='Invoice')
    bill_types = fields.Char('Billing Type')
    customer_ref = fields.Char('Customer Ref')
    customer_ref_inv = fields.Char('Customer Ref Inv No')
    shipment_type = fields.Selection([
            ('lcl','LCL'),
            ('fcl','FCL'),
        ],string='Shipment Type')
    shipper_date = fields.Date('DOC Received Date',default=fields.Date.today)
    eta = fields.Date('ETA')
    etd = fields.Date('ETD')
    vessel_date = fields.Date('Vessel Arrival Date')
    vessel_name = fields.Char('Vessel Name')
    rot_number = fields.Char('Rotation Number/Sequence Number')
    rot = fields.Binary('Rotation No Attach')
    s_supplier = fields.Many2one(comodel_name='res.partner', string='Shipping Line')
    fri_id = fields.Many2one('freight.forward',string='Freight Link')
    
    contain_info = fields.Boolean('Container Info.')
    car_info = fields.Boolean('Car Carrier')
    export_line = fields.One2many('export.tree','export_id', string='Export Lines')
    car_line = fields.One2many('export.car.carrier','car_import',string='Car Line')
    export_other_line = fields.One2many('export.other_charges','export_other_charges',string='Export Other Line')
    export_gov_line = fields.One2many('export.gov.charges','export_gov_charges',string='Export Gov Line')
    remark = fields.Text('Remarks')
    
    mani_date = fields.Date('Manifest Received Date')
    bill_no = fields.Char('B/L Number')
    bayan_no = fields.Char('Bayan No')
    bayan = fields.Binary('Bayan Attach')
    pre_bayan = fields.Date('Pre Bayan Date')
    
    bayan_date = fields.Date('Initial Bayan Date')
    field_office = fields.Many2one('field.officer',string='Assign To')
    shutl_start_date = fields.Date('Shuttling Start Date')
    fin_bayan_date = fields.Date('Final Bayan Date')
    final_attach = fields.Binary('Final Bayan')
    custom_exam = fields.Boolean('Open Custom Examination')
    
    status = fields.Many2one('import.status',string='Status')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    no = fields.Char('#',compute='_compute_sequence')
    # invoice_count = fields.Integer(string='Invoice Count', readonly=True)

    # @api.multi
    def _compute_sequence(self):
        no = 1
        for rec in self:
            rec.no = no
            no = no + 1
    
    @api.model
    def create(self,vals):
        res = super(ExportCustom, self).create(vals)
        if res.site:
            res.name = 'EXP'+ str(res.site.branch_no) + self.env['ir.sequence'].next_by_code('export.custom') or _('New')
        else:
            res.name = 'EXP' + self.env['ir.sequence'].next_by_code('export.custom')
        return res

    # @api.multi
    def action_view_invoice(self):
        xml_id = 'account.invoice_tree_with_onboarding'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'account.view_move_form'
        form_view_id = self.env.ref(xml_id).id
        return {
                'name': _('Employee log'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'res_model': 'account.move',
                'domain': [('id', 'in', self.invoice_id.ids)],
                'type': 'ir.actions.act_window',
                }
    # @api.multi
    def action_move_pre_bayan(self):
        for rec in self:
            rec.state = 'pre'
    
    # @api.multi
    def action_move_initial_bayan(self):
        for rep in self:
            rep.state = 'initial'
    
    # @api.multi
    def action_move_final_bayan(self):
        for rec in self:
            rec.state = 'final'
    
    # @api.multi
    def action_custom_exam(self):
        self.state = 'custom_exam'
        
    # @api.multi
    def action_cancelled(self):
        self.state = 'cancelled'

    # @api.multi
    def action_create_export_custom_invoice(self):
        for rec in self:
            invoice = self.env['account.move'].create({'partner_id':rec.customer.id,
                                            'invoice_date':rec.date,
                                            'name':rec.name
                                        })
            for line_other in rec.export_other_line:
                line = {
                    'product_id':line_other.product_id.id,
                    'name':line_other.description,
                    'price_unit':line_other.cost,
                    'price_subtotal': line_other.without_tax_amount,
                    'invoice_line_tax_ids': [(6, 0, line_other.tax_ids.ids)] or False,
                    'account_id':line_other.product_id.property_account_income_id.id or False,
                    'invoice_id':invoice.id
                }
                self.env['account.move.line'].create(line)
            for line_gov in rec.export_gov_line:
                line = {
                    'product_id':line_gov.product_id.id,
                    'name':line_gov.description,
                    'price_unit':line_gov.cost,
                    'price_subtotal': line_gov.without_tax_amount,
                    'invoice_line_tax_ids':[(6, 0, line_gov.tax_ids.ids)] or False,
                    'account_id':line_gov.product_id.property_account_income_id.id or False,
                    'invoice_id':invoice.id
                }
                self.env['account.move.line'].create(line)
            invoice._onchange_invoice_line_ids()
            invoice._compute_amount()
            invoice.action_post()
            rec.write({'invoice_id':invoice.id,'state':'done'})
    

class ByCustomer(models.Model):
    _name = 'by.customer'
    _description = 'Export By Customer'
    
class ToQuote(models.Model):
    _name = 'to.quote'
    _description = 'Export To Quote'
    
    name = fields.Char('To Name')
    active = fields.Boolean('Active',default=True)
    
class FromQuote(models.Model):
    _name = 'from.quote'
    _description = 'Export From Quote'
    
    name = fields.Char('From Name')
    active = fields.Boolean('Active',default=True)
        
class Fleet(models.Model):
    _name = 'fleet.type'
    _description = 'Export Fleet'
    
    name = fields.Char('Fleet Type')
    active = fields.Boolean('Active',default=True)

class ExportTree(models.Model):
    _name = 'export.tree'
    _description = 'Export Tree'
#     def _get_line_numbers(self):
#             line_num = 1
#             if self.ids:
#                 first_line_rec = self.browse(self.ids[0])    
#          
#                 for line_rec in first_line_rec.export_id.export_line:
#                     line_rec.line_no = line_num
#                     line_num += 1
#  
#     line_no = fields.Integer(compute='_get_line_numbers', string='Serial Number',readonly=False, default=False)
     
    export_id = fields.Many2one('export.custom',string="Export Reference", ondelete='cascade', index=True, copy=False)
    seq = fields.Char(string='Seq#',compute='_compute_sequence')
    crt_no = fields.Char('Container No.')
    des = fields.Text('Description')
    types = fields.Selection([('20ft','20ft'),('40ft','40ft')],string='Size')
    form = fields.Many2one('bsg_route_waypoints',string='Form')
    to = fields.Many2one('bsg_route_waypoints',string='To')
    fleet_type = fields.Many2one('bsg.vehicle.type.table',string='Fleet Type')
    transporter = fields.Many2one('res.partner',string='Transporter')
    trans_chrg = fields.Float('Transporter Charges')
    custom_chrg = fields.Float('Customer Charges')
    contact_info = fields.Text('Contact Info')
    
    
    # @api.multi
    def _compute_sequence(self):
        seq = 1
        for rec in self:
            rec.seq = seq
            seq = seq + 1
    
    
class ExportOtherCharges(models.Model):
    _name = 'export.other_charges'
    _description = 'Export Other Charges Des'
    
    # 
    @api.depends('cost', 'tax_ids')
    def _get_price(self):
        if self.product_id:
            if self.tax_ids:
                currency = self.currency_id or None
                quantity = 1
                product = self.product_id
                taxes = self.tax_ids.compute_all((self.cost), currency, quantity,
                                                 product=product)#, partner=self.cargo_sale_id.customer_id
                self.tax_amount = taxes['total_included'] - taxes['total_excluded']

    # 
    @api.depends('tax_amount','cost')
    def _get_without_tax_price(self):
        if self.tax_amount:
            self.without_tax_amount = self.cost + self.tax_amount
        else:
            self.without_tax_amount = self.cost

    @api.onchange('product_id')
    def _onchange_amont(self):
        if self.product_id:
            self.tax_ids = [(6,0,self.product_id.taxes_id.ids)]
    
    export_other_charges = fields.Many2one('export.custom',string ='Export Other Charge')
    product_id = fields.Many2one('product.product',string="Other Charges Description",domain="[('sale_ok','=',True)]")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    cost = fields.Float(string="Price")
    description = fields.Text(string="Desription")
#     cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string="Cargo Sale ID")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    tax_amount = fields.Float(compute='_get_price', digits=dp.get_precision('Export'))
    without_tax_amount = fields.Float(compute="_get_without_tax_price",string='Total Amount', digits=dp.get_precision('Export'))
    charges = fields.Float('Amount')
    
class ExportGovCharges(models.Model):
    _name='export.gov.charges'
    _description = 'Export Gov Charges'
    
    # 
    @api.depends('cost', 'tax_ids')
    def _get_price(self):
        if self.product_id:
            if self.tax_ids:
                currency = self.currency_id or None
                quantity = 1
                product = self.product_id
                taxes = self.tax_ids.compute_all((self.cost), currency, quantity,
                                                 product=product)#, partner=self.cargo_sale_id.customer_id
                self.tax_amount = taxes['total_included'] - taxes['total_excluded']

    # 
    @api.depends('tax_amount','cost')
    def _get_without_tax_price(self):
        if self.tax_amount:
            self.without_tax_amount = self.cost + self.tax_amount
        else:
            self.without_tax_amount = self.cost

    @api.onchange('product_id')
    def _onchange_amont(self):
        if self.product_id:
            self.tax_ids = [(6,0,self.product_id.taxes_id.ids)]
    
    export_gov_charges = fields.Many2one('export.custom',string='Export Gov Charge') 
    product_id = fields.Many2one('product.product',string="Gov Charges Description",domain="[('sale_ok','=',True)]")
    currency_id = fields.Many2one(string="Currency", comodel_name="res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    cost = fields.Float(string="Price")
    description = fields.Text(string="Desription")
#     cargo_sale_id = fields.Many2one('bsg_vehicle_cargo_sale',string="Cargo Sale ID")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    tax_amount = fields.Float(compute='_get_price', digits=dp.get_precision('Export'))
    without_tax_amount = fields.Float(compute="_get_without_tax_price",string='Total Amount', digits=dp.get_precision('Export'))
    gov_charges = fields.Float('Amount')
    
    
class CarTree(models.Model):
    _name = 'export.car.carrier'
    _description = 'Export Car Carrier'
    _order = 'seq'

    car_import = fields.Many2one('export.custom',string='Car Import')
    seq = fields.Char(string='Seq#',compute='_compute_sequence' )
    car_maker = fields.Many2one('bsg_car_make',string='Car Maker')
    model = fields.Many2one('bsg_car_config',string='Model')
    car_size = fields.Many2one('bsg_car_size',string='Car Size')
    year = fields.Many2one('bsg.car.year',string='Year')
    color = fields.Many2one('bsg_vehicle_color',string='Color')
    plate_registration = fields.Selection(
        [('saudi', 'لوحة سعودية'), ('non-saudi', 'لوحة أخرى '), ('new_vehicle', 'بدون لوحة')],
        default='saudi',string='Registration Type')
    plat_no = fields.Char(string='Plate No#')
    chassis = fields.Char('Chassis No#') 
        
    # @api.multi
    def _compute_sequence(self):
        seq = 1
        for rec in self:
            rec.seq = seq
            seq = seq + 1
    
class FieldOfficer(models.Model):
    _name = 'field.officer'
    _description = 'Export Field Officer'
    
    name = fields.Char('Field Officer Name')
    
    
    


        
        
        
