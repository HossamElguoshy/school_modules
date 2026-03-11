from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SchoolAttendanceSession(models.Model):
    _name = "school.attendance.session"
    _description = "Attendance Session"
    _order = "date desc"

    name = fields.Char()

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

    @api.onchange("section_id")
    def _onchange_section_id(self):
        """Auto-populate attendance lines when section is changed"""
        if self.section_id:
            students = self.env["school.student"].search([
                ("section_id", "=", self.section_id.id)
            ])
            lines = []  # Clear existing lines
            for student in students:
                lines.append((0, 0, {
                    "student_id": student.id,
                    "status": "present"
                }))
            self.line_ids = lines




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
