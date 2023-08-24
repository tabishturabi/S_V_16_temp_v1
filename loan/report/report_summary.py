# -*- coding: utf-8 -*-

from openerp import api, models, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class wrapped_report_loan_summary(models.AbstractModel):
    _name = 'report.loan.report_loan_summary'
    _description = 'report.loan.report_loan_summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        loan_app_id = self.env['loan.application'].browse(docids)
        for loan_id in loan_app_id:
            if loan_id.amount == 0.0:
                raise Warning(_('You not allow to print the summary with zero loan amount'))
            if loan_id.state != 'paid':
                raise Warning(_("You can't print the summary before the loan is approved"))
        report = report_obj._get_report_from_name('loan.report_loan_contract')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': loan_app_id,
        }
        return docargs
