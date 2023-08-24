# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
# from connect_mssql import get_log


def upset_datetime(datetime_wo_tz, tzone):
    """"  takes naive datetime (datetime_wo_tz) and it's timezone (tzone)
            returns the datetime aware with timezone changed to UTC
        """
    localized_datetime = pytz.UTC.localize(fields.Datetime.from_string(datetime_wo_tz))
    datetime_with_tz = localized_datetime.astimezone(timezone(tzone))
    return datetime_with_tz

import logging

_logger = logging.getLogger(__name__)


class BiometricMachine(models.Model):
    _name = 'biometric.machine'
    _description = "Biometric Machine"
    _inherit = ['mail.thread']

    MAKE_SEL = [
        ('zk', 'ZK'),
        ('suprema', 'Suprema'),
    ]

    AUTH_TYPE_SEL = [
        ('finger', 'Finger Print'),
        ('face', 'Face Print'),

    ]



    @api.model
    def _tz_get(self):
        return [
            (tz, tz) for tz in
            sorted(pytz.all_timezones,
                   key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

    name = fields.Char("Machine name")
    location = fields.Char("Location")
    make = fields.Selection(MAKE_SEL, string="Manufacturer", default="zk")
    ip_address = fields.Char("Machine IP", default='192.168.1.40')
    port = fields.Integer("Port Number", default='4370')
    company_id = fields.Many2one("res.company", "Company Name", default=lambda self: self.env.user.company_id)
    auth_type = fields.Selection(AUTH_TYPE_SEL, string="Authentication Type", default="finger")
    time_zone = fields.Selection('_tz_get', string='Timezone', required=True,
                                 default=lambda self: self.env.user.tz or 'UTC')
    last_download_date = fields.Datetime(string="Last Download On")
    database_ip = fields.Char("Database IP", default='192.168.1.7')
    database_port = fields.Integer(string="Database Port")
    database_name = fields.Char(name="Database Name")
    database_username = fields.Char(string="Database Username", )
    database_password = fields.Char(string="Database Password", )

    _sql_constraints = [
        ('name_company_id_uniq', 'unique (name, company_id)',
         _("You cannot have two machines with the same name in the same company")),
        ('ip_company_id_uniq', 'unique (ip_address, company_id)',
         _("You cannot have two machines with the same ip_address in the same company")),
    ]

    #################################
    # Functions used by cron        #
    #################################

    def send_connection_issue_email(self):
        """
        send email to admin in case device was not able to connect
        """
        body = (_("Error in connection to attendance machine: %s for company %s on %s <br/>") %
                (self.name, self.company_id.name, str(datetime.now())))
        self.message_post(body=body, partner_ids=[self.sudo().env.user.partner_id.id])
    #
    # def download_attendance_suprema(self):
    #     server = self.database_ip
    #     database = self.database_name
    #     username = self.database_username
    #     password = self.database_password
    #     machine_tz = self.time_zone
    #
    #     if server and database and username and password:
    #         last_download_date = self.last_download_date or str(datetime.today().replace(microsecond=0) + timedelta(days=-1))
    #         query_date = (datetime.strptime(last_download_date, DEFAULT_SERVER_DATETIME_FORMAT)).replace(microsecond=0)
    #         query_date = upset_datetime(str(query_date), machine_tz)
    #         query_date.strftime("%Y-%m-%d %H:%M:%S")
    #         logs = get_log(server, database, username, password, query_date)
    #         if logs:
    #             attend_log_obj = self.env['hr.attendance.log']
    #             for log in logs:
    #                 time = datetime.strptime(log[0], DEFAULT_SERVER_DATETIME_FORMAT)
    #                 aware_attend_datetime_machine_tz = pytz.timezone(machine_tz).localize(time)
    #                 aware_attend_datetime_utc = aware_attend_datetime_machine_tz.astimezone(pytz.UTC)
    #                 employee = self.env['hr.employee'].search([('employee_code', '=', log[1])])
    #                 log_vals = {
    #                    'employee_code':  log[1],
    #                    'employee_id': employee.id or '',
    #                    'time': aware_attend_datetime_utc,
    #                    'machine_id': self.id,
    #                    'time_zone': machine_tz,
    #                    'add_by_cron': True,
    #                 }
    #                 attend_log_obj.create(log_vals)
    #             return True
    #         else:
    #             self.send_connection_issue_email()
    #             return False

    # def download_attendance_zk(self):
    #     """ download attendance for zk machines """
    #     machine_ip = self.ip_address
    #     machine_tz = self.time_zone
    #     port = self.port
    #     zk = zklib.ZKLib(machine_ip, int(port))
    #     connected = zk.connect()
    #     if connected:
    #         zk.enableDevice()
    #         users = zk.getUser()
    #         logs = zk.getAttendance()
    #         if logs:
    #             attend_log_obj = self.env['hr.attendance.log']
    #             for log in logs:
    #                 aware_attend_datetime_machine_tz = pytz.timezone(machine_tz).localize(log[2])
    #                 aware_attend_datetime_utc = aware_attend_datetime_machine_tz.astimezone(pytz.UTC)
    #                 employee = self.env['hr.employee'].search([('employee_code', '=', str(log[0]))])
    #                 for user in users.items():
    #                     if log[0] == user[1][0]:
    #                         machine_user = user[1][1]
    #                 log_vals = {
    #                     'employee_code': str(log[0]),
    #                     'employee_id': employee.id or '',
    #                     'time': aware_attend_datetime_utc,
    #                     'machine_id': self.id,
    #                     'machine_user': machine_user,
    #                     'time_zone': machine_tz,
    #                     'add_by_cron': True,
    #                 }
    #                 attend_log_obj.create(log_vals)
    #         self.zk_clear_attendance()
    #         return True
    #     else:
    #         self.send_connection_issue_email()
    #         return False

    #@api.multi
    def download_attendance(self):
        """ downloads all attendance logs from all machine """
        all_machines = self.env['biometric.machine'].search([])
        for machine in all_machines:
            machine_make = machine.make
            if machine_make == "zk":
                success = machine.download_attendance_zk()
            elif machine_make == "suprema":
                success = machine.download_attendance_suprema()
            if success:
                machine.write({'last_download_date': datetime.today()})

    # #@api.multi
    # def zk_clear_attendance(self):
    #     """" clear machine after getting log for performance reasons """
    #     machine_ip = self.ip_address
    #     port = self.port
    #     zk = zklib.ZKLib(machine_ip, int(port))
    #     connected = zk.connect()
    #     if connected:
    #         zk.clearAttendance()
    #         zk.disconnect()
    #         return True
    #     else:
    #         self.send_connection_issue_email()

#################################################################################

    #@api.multi
    def copy(self):
        raise UserError(_('You cannot duplicate machine.'))

