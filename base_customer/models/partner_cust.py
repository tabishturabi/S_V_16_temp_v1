from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_parents = fields.Boolean('is a Parent')
    has_parents = fields.Boolean('Has a Parent')
    partner_parent = fields.Many2one("res.partner", string="Parent")
    partner_types = fields.Many2one("partner.type", string="Partner Type", track_visibility='always')
    is_dealer = fields.Boolean(string="Is Dealer", related="partner_types.is_dealer", store=True)

    # for add validation as need of Internal Reference  should be unique
    @api.constrains('ref')
    def _ref_constrains(self):
        if self.ref:
            ref = str(self.ref)
            search_param = ref.casefold()
            search_param_upper = ref.upper()
            search_id = self.search(['|', ('ref', '=', search_param_upper), ('ref', '=', search_param)])
            if len(search_id) > 1:
                raise UserError('Internal Reference Must Be Unique..!')

    @api.onchange('company_type', 'parent_id')
    def onchange_company_type(self):
        self.is_company = (self.company_type == 'company')
        if self.company_type == 'company':
            self.is_parents = True
            self.has_parents = False
        else:
            self.has_parents = True
            self.is_parents = False
            self.partner_parent = self.parent_id.id

    # for appliy the dynamic domain on partner type field
    @api.onchange('customer', 'supplier')
    def onchange_customer_supplier(self):
        if self.customer:
            search_id = False
            domain = []
            domain_count = 0
            if self.env.user.has_group('base_customer.group_credit_customer'):
                domain_count += 1
            if self.env.user.has_group('base_customer.group_staff'):
                domain_count += 1
            if self.env.user.has_group('base_customer.group_dealer_customer'):
                domain_count += 1
            if self.env.user.has_group('base_customer.group_customer'):
                domain_count += 1

            if domain_count >= 2:
                if domain_count == 2:
                    domain = ['|']
                elif domain_count == 3:
                    domain = ['|', '|']
                elif domain_count == 4:
                    domain = ['|', '|', '|']
            if self.env.user.has_group('base_customer.group_credit_customer'):
                domain += [('is_credit_customer', '=', True)]
            if self.env.user.has_group('base_customer.group_staff'):
                domain += [('is_staff', '=', True)]
            if self.env.user.has_group('base_customer.group_dealer_customer'):
                domain += [('is_dealer', '=', True)]
            if self.env.user.has_group('base_customer.group_customer'):
                domain += [('is_custoemer', '=', True)]
            if not self.env.user.has_group('base_customer.group_credit_customer') and not self.env.user.has_group(
                    'base_customer.group_staff') \
                    and not self.env.user.has_group(
                'base_customer.group_dealer_customer') and not self.env.user.has_group('base_customer.group_customer'):
                domain = False
            # else:
            #     search_id = self.env['partner.type'].search(['|','|',('is_custoemer','=',True),('is_dealer','=',True),('is_credit_customer','=',True)])
            if domain:
                search_id = self.env['partner.type'].search(domain)

            if search_id:
                return {'domain': {
                    'partner_types': [('id', 'in', search_id.ids)],
                }}
            else:
                return {'domain': {
                    'partner_types': [('id', 'in', [])],
                }}
        if self.supplier:
            search_id = self.env['partner.type'].search([('is_vendor', '=', True)])
            return {'domain': {
                'partner_types': [('id', 'in', search_id.ids)],
            }}

    @api.onchange('partner_types')
    def _onchange_partner_types(self):
        for data in self:
            if data.partner_types:
                data.property_account_receivable_id = data.partner_types.accont_rec.id
                data.property_account_payable_id = data.partner_types.accont_payable.id


class PartnerTypes(models.Model):
    _name = "partner.type"
    _description = "Partner Type"

    @api.constrains('name')
    def _code_constrains(self):
        search_id = self.env['partner.type'].search([('name', '=', self.name)])
        if len(search_id) > 1:
            raise UserError('Name Should be Unique..!')

    name = fields.Char('Name')
    accont_rec = fields.Many2one("account.account", string='Account Receivable')
    accont_payable = fields.Many2one("account.account", string='Account Payable')
    is_custoemer = fields.Boolean("Customer")
    restrict_partner_from_cargo = fields.Boolean("Restrict Partner From Cargo")
    is_vendor = fields.Boolean("Vendor")
    is_staff = fields.Boolean(string="IS Staff")
    is_dealer = fields.Boolean(string="Is Dealer")
    is_credit_customer = fields.Boolean(string="Is Credit Customer")
    is_construction = fields.Boolean(string="Is Construction")
    pricing_type = fields.Selection([('individual', 'General price'), ('corporate', 'Dealers price')])
    discount = fields.Float(string="Discount(%)")
    customer_type = fields.Selection(string='Customer Type', selection=[
        ('individual', 'Individual'),
        ('corporate', 'Corporate')
    ])

    # overriding for changes account receivable and payable should update on partner
    
    def write(self, vals):
        update_changes = False
        if vals.get('accont_rec') or vals.get('accont_payable'):
            update_changes = True
        res = super(PartnerTypes, self).write(vals)
    #     if update_changes:
    #         search_partner = self.env['res.partner'].search([('partner_types', '=', self.id)])
    #         for partner in search_partner:
    #             search_partner._onchange_partner_types()
        return res

    
    def unlink(self):
        for data in self:
            search_id = self.env['res.partner'].search([('partner_types', '=', data.id)])
            if search_id:
                raise UserError(_('You can only delete a record if the Customer Type is Used..!'))
        return super(PartnerTypes, self).unlink()
