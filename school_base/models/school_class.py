from odoo import models, fields, api

class SchoolClass(models.Model):
    _name = 'school.class'
    _description = 'School Class'

    name = fields.Char(required=True)

    teacher_ids = fields.Many2many(
        'school.teacher',
        'class_teacher_rel',  # relation table name
        'class_id',  # column referring to class
        'teacher_id',  # column referring to teacher
        string="Teachers")

    student_ids = fields.One2many(
        'school.student',
        'class_id',
        string="Students"
    )

    subject_ids = fields.Many2many(
        'school.subject',
        string="Subjects"
    )

    student_count = fields.Integer(
        string="Students Count",
        compute="_compute_student_count",
        store=True
    )

    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)