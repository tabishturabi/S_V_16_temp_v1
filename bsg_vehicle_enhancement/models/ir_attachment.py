from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class IrAttachmentExt(models.Model):
    _inherit = "ir.attachment"

    fleet_doc_type = fields.Many2one('documents.type', string="Document Type")
    check_fleet = fields.Boolean(string='Check Fleet')

    def delete_attachement(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['ir.attachment'].browse(selected_ids)
        if selected_records:
            for attach_id in selected_records:
                if attach_id:
                    if (self.env.user.has_group(
                            'bsg_vehicle_enhancement.group_fleet_attachment_delete') and attach_id.res_model == "fleet.vehicle") or (
                            self.env.user.has_group(
                                    'bsg_employee_attachment.group_employee_attachment_delete') and attach_id.res_model == "hr.employee") or (
                            self.env.user.has_group(
                                    'bsg_hr_payroll.group_payslip_batch_delete') and attach_id.res_model == "hr.payslip.run") or (
                            self.env.user.has_group(
                                    'bsg_customer_contract.group_cust_contract_attachment_delete') and attach_id.res_model == "bsg_customer_contract") or (
                            self.env.user.has_group(
                                    'bsg_tranport_bx_credit_customer_collection.group_bx_ccc_attachment_delete') and attach_id.res_model == "bx.credit.customer.collection"):
                        attach_id.unlink()
                    else:
                        raise ValidationError(
                            _('This user is not allowed to delete the Document of model %s' % attach_id.res_model))

    @api.model
    def create(self, vals):
        res = super(IrAttachmentExt, self).create(vals)
        if res.res_model == 'fleet.vehicle':
            fleet_id = self.env[res.res_model].search([('id', '=', res.res_id)])
            doc_id = self.env['document.info.fleet'].search([('id', 'in', fleet_id.document_ids.ids)], limit=1)

            if res.check_fleet:
                msg = _(
                    """<div class="o_thread_message_content">
                        <p>New Added Document</p>
                        <ul class="o_mail_thread_message_tracking">
                        <li>Document Name : <span>{name}</span></li>
                        <li>Document Type : <span>{type}</span></li>
                        <li>Attachement : <span>{attachement}</span></li>
                        </ul>
                        </div>
                        """.format(
                        name=res.name,
                        type=doc_id.document_type_id.name,
                        attachement=res.store_fname
                    )
                )
                doc_id.message_post(body=msg)
            else:
                msg = _(
                    """<div class="o_thread_message_content">
                        <p>New Added Document</p>
                        <ul class="o_mail_thread_message_tracking">
                        <li>Document Name : <span>{name}</span></li>
                        <li>Document Type : <span>{type}</span></li>
                        <li>Attachement : <span>{attachement}</span></li>
                        </ul>
                        </div>
                        """.format(
                        name=res.name,
                        type=res.fleet_doc_type.document_type_id,
                        attachement=res.store_fname
                    )
                )
                fleet_id.message_post(body=msg)
        if res.res_model == 'hr.employee':
            employee_id = self.env[res.res_model].search([('id', '=', res.res_id)], limit=1)
            msg = _(
                """<div class="o_thread_message_content">
                    <p>New Added Document</p>
                    <ul class="o_mail_thread_message_tracking">
                    <li>Document Name : <span>{name}</span></li>
                    <li>Document Type : <span>{type}</span></li>
                    <li>Attachement : <span>{attachement}</span></li>
                    </ul>
                    </div>
                    """.format(
                    name=res.name,
                    type=res.bsg_type.bsg_name,
                    attachement=res.store_fname
                )
            )
            employee_id.message_post(body=msg)
        if res.res_model == 'hr.payslip.run':
            batch_id = self.env[res.res_model].search([('id', '=', res.res_id)], limit=1)
            msg = _(
                """<div class="o_thread_message_content">
                    <p>New Added Document</p>
                    <ul class="o_mail_thread_message_tracking">
                    <li>Document Name : <span>{name}</span></li>
                    <li>Document Type : <span>{type}</span></li>
                    <li>Attachement : <span>{attachement}</span></li>
                    </ul>
                    </div>
                    """.format(
                    name=res.name,
                    type=res.bsg_type.bsg_name,
                    attachement=res.store_fname
                )
            )
            batch_id.message_post(body=msg)
        if res.res_model == 'bsg_customer_contract':
            cust_contract_id = self.env[res.res_model].search([('id', '=', res.res_id)], limit=1)
            msg = _(
                """<div class="o_thread_message_content">
                    <p>New Added Document</p>
                    <ul class="o_mail_thread_message_tracking">
                    <li>Document Name : <span>{name}</span></li>
                    <li>Document Type : <span>{type}</span></li>
                    <li>Attachement : <span>{attachement}</span></li>
                    </ul>
                    </div>
                    """.format(
                    name=res.name,
                    type=res.cus_contract_doc_type.document_type_id,
                    attachement=res.store_fname
                )
            )
            cust_contract_id.message_post(body=msg)
        if res.res_model == 'bx.credit.customer.collection':
            bx_ccc_id = self.env[res.res_model].search([('id', '=', res.res_id)], limit=1)
            msg = _(
                """<div class="o_thread_message_content">
                    <p>New Added Document</p>
                    <ul class="o_mail_thread_message_tracking">
                    <li>Document Name : <span>{name}</span></li>
                    <li>Document Type : <span>{type}</span></li>
                    <li>Attachement : <span>{attachement}</span></li>
                    </ul>
                    </div>
                    """.format(
                    name=res.name,
                    type=res.bx_ccc_doc_type.document_type_id,
                    attachement=res.store_fname
                )
            )
            bx_ccc_id.message_post(body=msg)
        return res

    # @api.multi
    def unlink(self):
        for attach_id in self:
            if attach_id:
                if attach_id.res_model == 'fleet.vehicle':
                    fleet_id = self.env[attach_id.res_model].search([('id', '=', attach_id.res_id)])
                    doc_id = self.env['document.info.fleet'].search([('id', 'in', fleet_id.document_ids.ids)],
                                                                    limit=1)

                    if attach_id.check_fleet:

                        msg = _(
                            """<div class="o_thread_message_content">
                                <p>Deleted Document</p>
                                <ul class="o_mail_thread_message_tracking">
                                <li>Document Name : <span>{name}</span></li>
                                <li>Document Type : <span>{type}</span></li>
                                <li>Attachement : <span>{attachement}</span></li>
                                </ul>
                                </div>
                                """.format(
                                name=attach_id.name,
                                type=doc_id.document_type_id.name,
                                attachement=attach_id.store_fname
                            )
                        )
                        doc_id.message_post(body=msg)
                    else:
                        msg = _(
                            """<div class="o_thread_message_content">
                                <p>Deleted Document</p>
                                <ul class="o_mail_thread_message_tracking">
                                <li>Document Name : <span>{name}</span></li>
                                <li>Document Type : <span>{type}</span></li>
                                <li>Attachement : <span>{attachement}</span></li>
                                </ul>
                                </div>
                                """.format(
                                name=attach_id.name,
                                type=attach_id.fleet_doc_type.document_type_id,
                                attachement=attach_id.store_fname
                            )
                        )
                        fleet_id.message_post(body=msg)
                if attach_id.res_model == 'hr.employee':
                    employee_id = self.env[attach_id.res_model].search([('id', '=', attach_id.res_id)], limit=1)
                    msg = _(
                        """<div class="o_thread_message_content">
                            <p>Deleted Document</p>
                            <ul class="o_mail_thread_message_tracking">
                            <li>Document Name : <span>{name}</span></li>
                            <li>Document Type : <span>{type}</span></li>
                            <li>Attachement : <span>{attachement}</span></li>
                            </ul>
                            </div>
                            """.format(
                            name=attach_id.name,
                            type=attach_id.bsg_type.bsg_name,
                            attachement=attach_id.store_fname
                        )
                    )
                    employee_id.message_post(body=msg)
                if attach_id.res_model == 'hr.payslip.run':
                    employee_id = self.env[attach_id.res_model].search([('id', '=', attach_id.res_id)], limit=1)
                    msg = _(
                        """<div class="o_thread_message_content">
                            <p>Deleted Document</p>
                            <ul class="o_mail_thread_message_tracking">
                            <li>Document Name : <span>{name}</span></li>
                            <li>Document Type : <span>{type}</span></li>
                            <li>Attachement : <span>{attachement}</span></li>
                            </ul>
                            </div>
                            """.format(
                            name=attach_id.name,
                            type=attach_id.bsg_type.bsg_name,
                            attachement=attach_id.store_fname
                        )
                    )
                    employee_id.message_post(body=msg)
                if attach_id.res_model == 'bsg_customer_contract':
                    cust_contract_id = self.env[attach_id.res_model].search([('id', '=', attach_id.res_id)], limit=1)
                    msg = _(
                        """<div class="o_thread_message_content">
                            <p>Deleted Document</p>
                            <ul class="o_mail_thread_message_tracking">
                            <li>Document Name : <span>{name}</span></li>
                            <li>Document Type : <span>{type}</span></li>
                            <li>Attachement : <span>{attachement}</span></li>
                            </ul>
                            </div>
                            """.format(
                            name=attach_id.name,
                            type=attach_id.cus_contract_doc_type.document_type_id,
                            attachement=attach_id.store_fname
                        )
                    )
                    cust_contract_id.message_post(body=msg)
                if attach_id.res_model == 'bx.credit.customer.collection':
                    bx_ccc_id = self.env[attach_id.res_model].search([('id', '=', attach_id.res_id)], limit=1)
                    msg = _(
                        """<div class="o_thread_message_content">
                            <p>Deleted Document</p>
                            <ul class="o_mail_thread_message_tracking">
                            <li>Document Name : <span>{name}</span></li>
                            <li>Document Type : <span>{type}</span></li>
                            <li>Attachement : <span>{attachement}</span></li>
                            </ul>
                            </div>
                            """.format(
                            name=attach_id.name,
                            type=attach_id.bx_ccc_doc_type.document_type_id,
                            attachement=attach_id.store_fname
                        )
                    )
                    bx_ccc_id.message_post(body=msg)
        res = super(IrAttachmentExt, self).unlink()
        return res



