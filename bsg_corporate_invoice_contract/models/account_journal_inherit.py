from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime

class AccountJournal(models.Model):
    _inherit = 'account.journal'
  
    is_cc_journal = fields.Boolean(string="IS CC JOURNAL", default=False)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    #override for restrict when credit customer collection

    def create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic account or an analytic distribution.
        """
        for obj_line in self:
            if obj_line.payment_id.state == 'draft' or not obj_line.payment_id.state:
                for tag in obj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
                    for distribution in tag.analytic_distribution_ids:
                        vals_line = obj_line._prepare_analytic_distribution_line(distribution)
                        if obj_line.invoice_id:
                            vals_line['branch_id'] = obj_line.invoice_id.loc_from.loc_branch_id.id
                        elif obj_line.payment_id:
                            if obj_line.payment_id.branch_ids:
                                vals_line['branch_id'] = obj_line.payment_id.branch_ids.id
                        self.env['account.analytic.line'].create(vals_line)
                if obj_line.analytic_account_id and not obj_line.invoice_id.credit_collection_id:
                    vals_line = obj_line._prepare_analytic_line()[0]
                    if obj_line.invoice_id:
                        vals_line['branch_id'] = obj_line.invoice_id.loc_from.loc_branch_id.id
                    elif obj_line.payment_id:
                        if obj_line.payment_id.branch_ids:
                            vals_line['branch_id'] = obj_line.payment_id.branch_ids.id
                    self.env['account.analytic.line'].create(vals_line)
