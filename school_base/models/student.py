from odoo import models, fields

class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Student'

    partner_id = fields.Many2one('res.partner', string="Student Partner", required=True)
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender")
    parent_id = fields.Many2one('school.parent', string="Parent")
    class_id = fields.Many2one('school.class', string="Class")
    section_id = fields.Many2one('school.section', string="Section")
