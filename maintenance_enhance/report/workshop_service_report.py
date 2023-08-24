#-*- coding:utf-8 -*-
from odoo import api, models, fields


class WorkshopServiceReport(models.AbstractModel):
    _name = 'report.maintenance_enhance.report_workshop_service'

    def get_workshop_lines(self, workorder, workshop):
        lines = workorder.wo_child_ids.filtered(lambda x: x.workshop_name == workshop)
        return lines

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['maintenance.request.enhance'].browse(docids)
        workshops = docs.mapped("wo_child_ids.workshop_name")
        return {
            'doc_ids': docids,
            'docs': docs,
            'doc_model': 'maintenance.request.enhance',
            'workshops': workshops,
            'get_workshop_lines': self.get_workshop_lines,
            # 'print_date': form,
            # 'to': to,
            # 'head': head,
            # 'records': records,
            # 'types': types,
        }


