from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseRequest(models.Model):
    _inherit = 'purchase.req'

    manufacturing_order_id = fields.Many2one('bsg.mrp.production', string="Manufacturing Order", track_visibility=True)

    def submission_manufacturing(self):
        if not self.preq_line:
            raise UserError(_("Please Add Lines To Submit"))
        if not self.manager_ids:
            raise UserError(_("Please Add Manager"))
        if self.state == 'tsub':
            branch_number = self.branch_no
            if self.name == '/' or str(self.name).__contains__('*'):
                sequence = self.env.ref('purchase_enhanced.ir_sequence_purchasecollection').next_by_id()
                if branch_number:
                    self.name = "PR/%s%s" % (branch_number, sequence)
                else:
                    self.name = "PR/%s" % (sequence)
            self.write({'state': 'tapprove'})
            self.preq_line.write({'state': 'tsub'})
            if all(line.product_id.without_approve for line in self.preq_line):
                self.approved()
        template_id = self.env.ref('purchase_enhanced.email_template_for_purchase_requset_manager')
        template_id.send_mail(self.id, force_send=True, raise_exception=True)
        self.message_post(subject=_('Requset Send To Approve'),
                          body='Requset Sent To : %s' % (self.manager_ids.mapped('name')))
        self.assign_user_ids = self.manager_ids

    @api.model
    def default_get(self, fields):
        result = super(PurchaseRequest, self).default_get(fields)
        if self.env.user.has_group('purchase_enhanced.pr_for_stock'):
            result['request_type'] = 'stock'
        if self.env.user.has_group('purchase_enhanced.pr_for_workshop'):
            result['request_type'] = 'workshop'
        if self.env.user.has_group('purchase_enhanced.pr_for_branch'):
            result['request_type'] = 'branch'
        if self.env.user.has_group('manufacturing_enhance.group_pr_mrp'):
            result['request_type'] = 'manufacture'
        return result

    def _get_request_oprions(self):
        options = []
        if self.env.user.has_group('purchase_enhanced.pr_for_stock'):
            options += [('stock', _('For Stock'))]
        if self.env.user.has_group('purchase_enhanced.pr_for_workshop'):
            options += [('workshop', _('For Workshop'))]
        if self.env.user.has_group('purchase_enhanced.pr_for_branch'):
            options += [('branch', _('For Branch'))]
        if self.env.user.has_group('manufacturing_enhance.group_pr_mrp'):
            options += [('manufacture', _('For Manufacture'))]
        return options

    request_type = fields.Selection(_get_request_oprions,
                                    required=True, track_visibility='always')


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.req.line'

    manufacturing_order_id = fields.Many2one('bsg.mrp.production', string="Manufacturing Order", track_visibility=True)
    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch'),
                                     ('manufacture', 'For Manufacture')],
                                    related='preq.request_type', store=True, track_visibility='always')
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True, related='product_id.uom_id')


class PurchaseReqRecLine(models.Model):
    _inherit = 'purchase.req.rec.line'

    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True, related='product_id.uom_id')


class PurchaseTransfer(models.Model):
    _inherit = 'purchase.transfer'

    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch'),
                                     ('manufacture', 'For Manufacture')], store=True, track_visibility='always')
    manufacturing_order_id = fields.Many2one('bsg.mrp.production', string="Manufacturing Order", track_visibility=True)


class PurchaseTransferLine(models.Model):
    _inherit = 'purchase.transfer.line'

    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True, related='product_id.uom_id')


class PurchaseRequisitionReceived(models.Model):
    _inherit = 'purchase.req.rec'

    request_type = fields.Selection([('stock', 'For Stock'), ('workshop', 'For Workshop'), ('branch', 'For Branch'),
                                     ('manufacture', 'For Manufacture')], store=True, track_visibility='always')
    manufacturing_order_id = fields.Many2one('bsg.mrp.production', string="Manufacturing Order", track_visibility=True)
