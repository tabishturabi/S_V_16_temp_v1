from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import UserError,ValidationError
import xlsxwriter

class VehicleDriverAssignReportPdf(models.AbstractModel):
    _name = 'report.bsg_vehicle_driver_assign_reports.driver_assign_pdf'


    @api.model
    def _get_report_values(self, docids, data=None):
        model=self.env.context.get('active_model')
        docs=self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs':docs
        }




























