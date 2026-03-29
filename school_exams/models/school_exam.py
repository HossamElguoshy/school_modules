from odoo import api, fields, models, _
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

    max_mark = fields.Float(default=100, required=True)

    line_ids = fields.One2many(
        "school.exam.line",
        "exam_id",
        string="Students"
    )

    @api.onchange("grade_id")
    def _onchange_grade_id(self):
        if self.section_id and self.section_id.grade_id != self.grade_id:
            self.section_id = False

    @api.onchange("section_id")
    def _onchange_section_id(self):
        if self.section_id:
            students = self.env["school.student"].search([
                ("section_id", "=", self.section_id.id),
                ("active", "=", True)
            ])
            self.line_ids = [(5, 0, 0)] + [
                (0, 0, {"student_id": student.id}) for student in students
            ]

    @api.constrains("section_id", "grade_id")
    def _check_section_grade(self):
        for rec in self:
            if rec.section_id and rec.grade_id and rec.section_id.grade_id != rec.grade_id:
                raise ValidationError(_("Section must belong to the selected grade."))

    @api.constrains("max_mark")
    def _check_max_mark(self):
        for rec in self:
            if rec.max_mark <= 0:
                raise ValidationError(_("Max mark must be greater than zero."))


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

    grade_letter = fields.Selection([
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("F", "F"),
    ], compute="_compute_grade_letter", store=True)

    _sql_constraints = [
        ("exam_student_unique", "unique(exam_id, student_id)", "Student cannot appear twice in the same exam."),
    ]

    @api.depends("mark", "max_mark")
    def _compute_percentage(self):
        for rec in self:
            rec.percentage = (rec.mark / rec.max_mark) * 100 if rec.max_mark else 0

    @api.depends("percentage")
    def _compute_status(self):
        for rec in self:
            rec.status = "pass" if rec.percentage >= 50 else "fail"

    @api.depends("percentage")
    def _compute_grade_letter(self):
        for rec in self:
            if rec.percentage >= 85:
                rec.grade_letter = "A"
            elif rec.percentage >= 75:
                rec.grade_letter = "B"
            elif rec.percentage >= 65:
                rec.grade_letter = "C"
            elif rec.percentage >= 50:
                rec.grade_letter = "D"
            else:
                rec.grade_letter = "F"

    @api.constrains("mark", "max_mark")
    def _check_mark(self):
        for rec in self:
            if rec.mark < 0:
                raise ValidationError(_("Mark cannot be negative."))
            if rec.mark > rec.max_mark:
                raise ValidationError(_("Mark cannot exceed max mark."))

    @api.constrains("student_id", "exam_id")
    def _check_student_section(self):
        for rec in self:
            if rec.exam_id.section_id and rec.student_id.section_id != rec.exam_id.section_id:
                raise ValidationError(_("Student must belong to the exam section."))