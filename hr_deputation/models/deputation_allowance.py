from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrDeputationsAllownce(models.Model):
    _name = 'hr.deputations.allownce'

    _inherit = ['mail.thread']
    _rec_name = 'counter_group'

    counter_group = fields.Many2one('country.groups', string='Country Group')

    deputation_type = fields.Selection([('internal', 'Internal'), ('external', 'External')], string='Deputation Type',
                                       default='internal')
    days_before = fields.Integer(string='Days Before')
    days_after = fields.Integer(string='Days After')
    line_ids = fields.One2many('hr.basic.allownce.lines', 'allownce_id',
                               string='Allownce Lines', tracking=True, track_visibility='onchange')
    job_ids = fields.Many2many('hr.job', string='Job Positions')
    other_allownce_ids = fields.One2many('hr.deput.other.allownce', 'basic_allownce_id',
                                         string='Allownce Lines', tracking=True, track_visibility='onchange')

    # @api.depends('line_ids')
    # def compute_jobs(self):
    #     jobs = []
    #     for record in self:
    #         for rec in record.line_ids:
    #             for job in rec.job_ids:
    #                 jobs.append(job.id)
    #         record.write({'job_ids': jobs})

    @api.constrains('line_ids')
    def _check_exist_product_in_line(self):
        jobs = []
        for allownce in self:
            for line in allownce.line_ids:
                for l in line.job_ids:
                    if l in jobs:
                        raise UserError(
                            _('Sorry !!The job position %s \n is repeated in the jobs!! The job position must not be repeated!!') % l.name)
                    else:
                        jobs.append(l)


class HrDeputationsAllownce(models.Model):
    _name = 'hr.basic.allownce.lines'

    _inherit = ['mail.thread']
    allownce_id = fields.Many2one('hr.deputations.allownce', string='Allownce')
    job_ids = fields.Many2many('hr.job', string='Job Positions')

    amount = fields.Float('Amount per day')

# @api.onchange('job_ids')
# def _check_exist_product_in_line (self):
# 	jobs=[]
# 	for allownce in self.parent.line_ids:

# 		for l in allownce.job_ids:
# 			if l in jobs:
# 				raise UserError(_('Sorry !!The job position %s \n is repeated in the jobs!! The job position must not be repeated!!')%l.name)
# 			else:
# 				jobs.append(l)
