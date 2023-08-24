# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SurveyQuestionCategory(models.Model):
	_name = 'survey.question.category'
	_description = "Survey Question"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(string="Category Name")

class SurveyQuestionMaster(models.Model):
	_name = 'surver.question.config'
	_description = "Survey Question"
	_inherit = ['mail.thread','mail.activity.mixin']

	name = fields.Char(string="Question")
	category_id = fields.Many2one('survey.question.category',string="Penalty Type")
	dedcution_way = fields.Selection([('percentage','Percentage'),('fixed_amt','Fixed Amt'),('not_apply','Not Apply')],string="Deduction Way")
	deserving = fields.Selection([('yes','Yes'),('no','No'),('stop_deserving','Stop Deserving'),('not_apply','Not Apply')],string="DeservIng")
	pecentage_amount = fields.Float(string="Percentage(%)")
	fixed_amount = fields.Float(string="Fixed Amount")
