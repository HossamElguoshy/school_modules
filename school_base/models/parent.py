from odoo import models, fields

class SchoolParent(models.Model):
    _name = 'school.parent'
    _description = 'Parent'

    partner_id = fields.Many2one('res.partner', string="Parent Partner", required=True)
    child_ids = fields.One2many('school.student', 'parent_id', string="Children")