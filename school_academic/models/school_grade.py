from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SchoolGrade(models.Model):
    _name = 'school.grade'
    _description = 'Student Grade'

    student_id = fields.Many2one(
        'res.partner',
        string="Student",

        required=True
    )

    subject_id = fields.Many2one(
        'school.subject',
        required=True
    )

    teacher_id = fields.Many2one(
        'school.teacher',
        string="Teacher"
    )

    exam_date = fields.Date()
    score = fields.Float()
    max_score = fields.Float(default=100)

    percentage = fields.Float(compute="_compute_percentage", string="Percentage")

    @api.depends('score','max_score')
    def _compute_percentage(self):
        for rec in self:
            rec.percentage = (rec.score / rec.max_score) * 100 if rec.max_score else 0

    @api.constrains('score','max_score')
    def _check_score(self):
        for rec in self:
            if rec.score > rec.max_score:
                raise ValidationError("Score cannot exceed Max Score")