from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SchoolExam(models.Model):
    _name = "school.exam"
    _description = "Exam"

    name = fields.Char(required=True)

    date = fields.Date(required=True)

    academic_year_id = fields.Many2one(
        "school.academic.year",
        required=True
    )

    grade_id = fields.Many2one(
        "school.grade",
        required=True
    )

    section_id = fields.Many2one(
        "school.section",
        string="Section"
    )

    subject_id = fields.Many2one(
        "school.subject",
        required=True
    )

    max_mark = fields.Float(default=100)

    line_ids = fields.One2many(
        "school.exam.line",
        "exam_id",
        string="Students"
    )


    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            students = self.env['school.student'].search([('section_id', '=', self.section_id.id)])
            self.line_ids = [(5,)] + [(0, 0, {'student_id': student.id}) for student in students]






class SchoolExamLine(models.Model):
    _name = "school.exam.line"
    _description = "Exam Line"

    exam_id = fields.Many2one(
        "school.exam",
        required=True,
        ondelete="cascade"
    )

    student_id = fields.Many2one(
        "school.student",
        required=True
    )

    mark = fields.Float()

    max_mark = fields.Float(
        related="exam_id.max_mark",
        store=True
    )

    percentage = fields.Float(
        compute="_compute_percentage",
        store=True
    )

    status = fields.Selection([
        ("pass", "Pass"),
        ("fail", "Fail")
    ], compute="_compute_status", store=True)

    @api.depends("mark", "max_mark")
    def _compute_percentage(self):
        for rec in self:
            if rec.max_mark:
                rec.percentage = (rec.mark / rec.max_mark) * 100
            else:
                rec.percentage = 0

    @api.depends("percentage")
    def _compute_status(self):
        for rec in self:
            rec.status = "pass" if rec.percentage >= 50 else "fail"

    @api.constrains("mark", "max_mark")
    def _check_mark(self):
        for rec in self:
            if rec.mark > rec.max_mark:
                raise ValidationError("Mark cannot exceed max mark.")