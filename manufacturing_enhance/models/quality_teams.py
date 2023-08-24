# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class QualityAlertTeamExt(models.Model):
    _name = "bsg.quality.alert.team"
    _description = "Quality Team"
    _inherit = ['mail.alias.mixin', 'mail.thread']
    _order = "sequence, id"

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    sequence = fields.Integer('Sequence')
    # check_count = fields.Integer('# Quality Checks', compute='_compute_check_count')
    # alert_count = fields.Integer('# Quality Alerts', compute='_compute_alert_count')
    color = fields.Integer('Color', default=1)
    # alias_id = fields.Many2one('mail.alias', 'Alias', ondelete="restrict", required=True)

    # @api.multi
    # def _compute_check_count(self):
    #     check_data = self.env['quality.check'].read_group([('team_id', 'in', self.ids), ('quality_state', '=', 'none')],
    #                                                       ['team_id'], ['team_id'])
    #     check_result = dict((data['team_id'][0], data['team_id_count']) for data in check_data)
    #     for team in self:
    #         team.check_count = check_result.get(team.id, 0)
    #
    # @api.multi
    # def _compute_alert_count(self):
    #     alert_data = self.env['quality.alert'].read_group([('team_id', 'in', self.ids), ('stage_id.done', '=', False)],
    #                                                       ['team_id'], ['team_id'])
    #     alert_result = dict((data['team_id'][0], data['team_id_count']) for data in alert_data)
    #     for team in self:
    #         team.alert_count = alert_result.get(team.id, 0)
