# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID,_
from lxml import etree
import json


class BsgEmployee(models.Model):
    _inherit = "hr.employee"

    
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.employee'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for employee in self:
            employee.attachment_number = attachment.get(employee.id, 0)

    
    def open_attach_wizard(self):
        view_id = self.env.ref('bsg_employee_attachment.view_attachment_form2').id
        return {
            'name': _('Attachments'),
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id),
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('bsg_employee_attachment.action_attachment')
        return res

    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')


class IrAttachmentExt(models.Model):
    _inherit = "ir.attachment"

    bsg_type = fields.Many2one('hr.emp.doc.type', string="Document Type")
    education_doc_type = fields.Many2one('hr.education.type', string="Education Document Type")
    doc_type = fields.Selection([('education', 'Education'),('other', 'Other')],'Doc Type')
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(IrAttachmentExt, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        has_my_group1 = self.env.user.has_group('bsg_employee_attachment.group_employee_attachment_delete')
        bool_check = has_my_group1 or self.env.user._is_admin()
        if self.env.context.get('active_model') == 'hr.employee':
            if not bool_check:
                root = etree.fromstring(res['arch'])
                root.set('delete', 'false')
                root.set('duplicate', 'false')
                root.set('edit', 'false')
                root.set('create', 'false')
                root.set('copy', 'false')
                res['arch'] = etree.tostring(root)

        return res
    
    #Cron initial state in active
    @api.model
    def gc_mail_data(self):
        query_bassami_inspection = "delete from bassami_inspection where id in  (select id from bassami_inspection limit 1000);"
        self.env.cr.execute(query_bassami_inspection)
        self.env.cr.commit()
        return True
