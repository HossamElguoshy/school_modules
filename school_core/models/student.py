from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "Student"
    _inherit = ["school.student", "mail.thread", "mail.activity.mixin"]
    _order = "student_code desc"

    name = fields.Char(required=True, tracking=True)
    student_code = fields.Char(readonly=True, copy=False, index=True, tracking=True, default=lambda self: self.env['ir.sequence'].next_by_code('school.student'))

    # الطالب كـ partner لسهولة portal/contacts (ممكن تعمل partner منفصل للطالب)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True, ondelete="restrict", string="student_part")

    guardian_partner_ids = fields.Many2many(
        "res.partner",
        "school_student_guardian_rel",
        "student_id", "partner_id",
        string="Guardians",
        tracking=True
    )

    academic_year_id = fields.Many2one("school.academic.year", required=True, tracking=True)
    grade_id = fields.Many2one("school.grade", required=True, tracking=True)
    section_id = fields.Many2one("school.section", tracking=True)

    state = fields.Selection([
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("graduated", "Graduated"),
    ], default="active", tracking=True)

    active = fields.Boolean(default=True)

    invoice_partner_id = fields.Many2one(
        "res.partner",
        string="Invoice To",
        compute="_compute_invoice_partner",
        store=True,
        help="Default partner to invoice (usually first guardian)."
    )


    @api.depends("guardian_partner_ids", "partner_id")
    def _compute_invoice_partner(self):
        for rec in self:
            rec.invoice_partner_id = (rec.guardian_partner_ids[:1].id or rec.partner_id.id)