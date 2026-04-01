from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SchoolAcademicYear(models.Model):
    _name = "school.academic.year"
    _description = "Academic Year"
    _order = "date_start desc"

    name = fields.Char(required=True, index=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active = fields.Boolean(default=True)

    term_ids = fields.One2many("school.term", "academic_year_id", string="Terms")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(("Start date must be before end date."))

    _sql_constraints = [
        ("academic_year_name_unique", "unique(name)", "Academic year name must be unique."),
    ]

class SchoolTerm(models.Model):
    _name = "school.term"
    _description = "Term"
    _order = "date_start asc"

    name = fields.Char(required=True)
    academic_year_id = fields.Many2one("school.academic.year", required=True, ondelete="cascade")
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active = fields.Boolean(default=True)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(_("Start date must be before end date."))


class SchoolGrade(models.Model):
    _name = "school.grade"
    _description = "Grade"
    _order = "sequence, name"

    name = fields.Char(required=True, index=True)
    code = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    section_ids = fields.One2many("school.section", "grade_id", string="Sections")

    _sql_constraints = [
        ("grade_name_unique", "unique(name)", "Grade name must be unique."),
    ]
class SchoolSection(models.Model):
    _name = "school.section"
    _description = "Section/Class"
    _order = "grade_id, sequence, name"

    name = fields.Char(required=True, index=True)
    grade_id = fields.Many2one("school.grade", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)

    capacity = fields.Integer(default=30)
    active = fields.Boolean(default=True)

    student_count = fields.Integer(compute="_compute_student_count", store=False)

    def _compute_student_count(self):
        Student = self.env["school.student"].sudo()
        for rec in self:
            rec.student_count = Student.search_count([("section_id", "=", rec.id), ("active", "=", True)])

    _sql_constraints = [
        ("section_grade_name_unique", "unique(name, grade_id)", "Section name must be unique per grade."),
    ]
class SchoolSubject(models.Model):
    _name = "school.subject"
    _description = "Subject"
    _order = "name"

    name = fields.Char(required=True, index=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ("subject_name_unique", "unique(name)", "Subject name must be unique."),
    ]