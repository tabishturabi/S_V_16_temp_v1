from odoo import api, fields, models, _

class BSG_Branches(models.Model):
    _inherit = "bsg_branches.bsg_branches"
    
    account = fields.Many2one("account.account",string="Account")
    
    # @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for bsg in self:
            current = bsg
            name = current.branch_ar_name
            res.append((bsg.id, name))
        return res
    
class Accountmove(models.Model):
    _inherit = "account.move"
    
    
    branches = fields.Many2one("bsg_branches.bsg_branches",string="Branch")
    
    
class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    
    branches = fields.Many2many("bsg_branches.bsg_branches",string="Branch")
    paym_type = fields.Selection([('receipt','Receipt'),
                                  ('payment','Payment')
                                  ])

class AccountJournal(models.Model):
    _inherit = "account.payment"
    
    branch_ids = fields.Many2one('bsg_branches.bsg_branches',string="Branch")
