from odoo import models, fields

class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'School Teacher'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        ondelete='cascade'
    )

    subject_id = fields.Many2one(
        'school.subject',
        string="Main Subject"
    )

    class_ids = fields.Many2many(
        'school.class',
        'class_teacher_rel',
        'teacher_id',
        'class_id',
        string="Classes"
    )

    active = fields.Boolean(default=True)