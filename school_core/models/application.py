from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolApplication(models.Model):
    _name = "school.application"
    _description = "Admission Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(readonly=True, copy=False, index=True, default=lambda self: _("New"))
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("review", "Under Review"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ], default="draft", tracking=True)

    # Guardian (bill-to عادة)
    guardian_partner_id = fields.Many2one("res.partner", required=True, tracking=True, ondelete="restrict")

    # Student info (will create partner + student)
    student_name = fields.Char(required=True, tracking=True)
    student_birthdate = fields.Date(tracking=True)

    academic_year_id = fields.Many2one("school.academic.year", required=True, tracking=True)
    grade_id = fields.Many2one("school.grade", required=True, tracking=True)
    section_id = fields.Many2one("school.section", tracking=True)

    note = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", string="Documents")

    student_id = fields.Many2one("school.student", copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name") in (False, _("New")):
                vals["name"] = self.env["ir.sequence"].next_by_code("school.application") or _("New")
        return super().create(vals_list)

    @api.onchange("grade_id")
    def _onchange_grade_id(self):
        if self.grade_id and self.section_id and self.section_id.grade_id != self.grade_id:
            self.section_id = False

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                continue
            rec.state = "submitted"

    def action_review(self):
        for rec in self:
            if rec.state not in ("submitted", "draft"):
                continue
            rec.state = "review"

    def action_reject(self):
        for rec in self:
            if rec.state == "accepted":
                raise ValidationError(_("Cannot reject an accepted application."))
            rec.state = "rejected"

    def action_accept_create_student(self):
        """Accept application and create Student + Partner, link guardian."""
        Student = self.env["school.student"].sudo()
        Partner = self.env["res.partner"].sudo()

        for rec in self:
            if rec.state not in ("submitted", "review"):
                raise ValidationError(_("Only submitted/review applications can be accepted."))
            if rec.student_id:
                rec.state = "accepted"
                continue

            # Create partner for student (child)
            student_partner = Partner.create({
                "name": rec.student_name,
                "type": "contact",
                "parent_id": rec.guardian_partner_id.id,  # optional: make guardian parent contact
            })

            student = Student.create({
                "name": rec.student_name,
                "partner_id": student_partner.id,
                "guardian_partner_ids": [(6, 0, [rec.guardian_partner_id.id])],
                "academic_year_id": rec.academic_year_id.id,
                "grade_id": rec.grade_id.id,
                "section_id": rec.section_id.id if rec.section_id else False,
            })

            rec.student_id = student.id
            rec.state = "accepted"