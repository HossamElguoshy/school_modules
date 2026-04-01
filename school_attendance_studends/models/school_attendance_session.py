from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SchoolAttendanceSession(models.Model):
    _name = "school.attendance.session"
    _description = "Attendance Session"
    _order = "date desc"

    name = fields.Char(compute="_compute_name", store=True)

    section_id = fields.Many2one(
        "school.section",
        required=True
    )

    date = fields.Date(
        required=True,
        default=fields.Date.today
    )

    line_ids = fields.One2many(
        "school.attendance.line",
        "session_id"
    )

    present_count = fields.Integer(compute="_compute_counts", store=True)
    absent_count = fields.Integer(compute="_compute_counts", store=True)
    late_count = fields.Integer(compute="_compute_counts", store=True)
    excused_count = fields.Integer(compute="_compute_counts", store=True)

    _sql_constraints = [
        (
            "section_date_unique",
            "unique(section_id, date)",
            "Attendance session already exists for this section on this date."
        ),
    ]

    @api.depends("section_id", "date")
    def _compute_name(self):
        for rec in self:
            if rec.section_id and rec.date:
                rec.name = f"Attendance - {rec.section_id.name} - {rec.date}"
            else:
                rec.name = "New Attendance"

    @api.depends("line_ids.status")
    def _compute_counts(self):
        for rec in self:
            rec.present_count = len(rec.line_ids.filtered(lambda l: l.status == "present"))
            rec.absent_count = len(rec.line_ids.filtered(lambda l: l.status == "absent"))
            rec.late_count = len(rec.line_ids.filtered(lambda l: l.status == "late"))
            rec.excused_count = len(rec.line_ids.filtered(lambda l: l.status == "excused"))

    @api.constrains("line_ids", "section_id")
    def _check_students_belong_to_section(self):
        for rec in self:
            for line in rec.line_ids:
                if line.student_id.section_id != rec.section_id:
                    raise ValidationError(_("All students must belong to the selected section."))

    @api.onchange("section_id")
    def _onchange_section_id(self):
        if self.section_id:
            students = self.env["school.student"].search([
                ("section_id", "=", self.section_id.id),
                ("active", "=", True)
            ])
            self.line_ids = [(5, 0, 0)] + [(0, 0, {
                "student_id": student.id,
                "status": "present"
            }) for student in students]


class SchoolAttendanceLine(models.Model):
    _name = "school.attendance.line"
    _description = "Student Attendance Line"

    session_id = fields.Many2one(
        "school.attendance.session",
        required=True,
        ondelete="cascade"
    )

    student_id = fields.Many2one(
        "school.student",
        required=True
    )

    status = fields.Selection([
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ], default="present", required=True)

    note = fields.Text()

    _sql_constraints = [
        (
            "session_student_unique",
            "unique(session_id, student_id)",
            "Student cannot appear twice in the same attendance session."
        ),
    ]