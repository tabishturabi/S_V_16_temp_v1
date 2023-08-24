from odoo import models, fields, api

class ApiLog(models.Model):
    _name = 'api.log'

    endpoint = fields.Char('End Point')
    request_payload = fields.Text('Payload')
    exception_message = fields.Text('Exception String')


    @api.model
    def create(self, vals):
        res = super(ApiLog, self).create(vals)
        base_url =  self.env['ir.config_parameter'].sudo().with_context(force_company=self.env.user.company_id.id, company_id=self.env.user.company_id.id).get_param('web.base.url')
        record_url = '%s/web?debug#id=%d&action=1933&model=api.log&view_type=form&menu_id=4'%(base_url,res.id)
        body = ('Click  the following link to open Mobile API Error log record: <br/> <a href="%s">%s</a><br> <b/> Thanks.') % (record_url , ' '.join(res.endpoint.split('/')))
        self.env['mail.mail'].sudo().create({
            'body_html': body,
            'subject': 'Mobile Api Error',
            'email_to': 'muhammad.yousef@albassami.com,hamdan@albassami.com,zain.alabdin@albassami.com',
            'auto_delete': True,
            # 'references': msg_dict.get('message_id'),
        }).send()
        return res