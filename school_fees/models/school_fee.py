from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SchoolFee(models.Model):
    _name = 'school.fee'
    _description = 'Student Fees'

    student_id = fields.Many2one('school.student', required=True)
    fee_line_ids = fields.One2many('school.fee.line', 'fee_id', string="Fee Lines")
    total_amount = fields.Float(compute="_compute_total", store=True)
    invoice_id = fields.Many2one('account.move', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
    ], default='draft')

    @api.depends('fee_line_ids.amount')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.fee_line_ids.mapped('amount'))

    def action_create_invoice(self):
        for rec in self:
            if rec.invoice_id:
                raise ValidationError(_("Invoice already exists for this fee record."))

            if not rec.fee_line_ids:
                raise ValidationError(_("Please add at least one fee line."))

            partner = rec.student_id.invoice_partner_id or rec.student_id.partner_id
            if not partner:
                raise ValidationError(_("No invoice partner found for this student."))

            lines = []
            for line in rec.fee_line_ids:
                lines.append((0, 0, {
                    'name': line.fee_structure_id.name,
                    'quantity': 1,
                    'price_unit': line.amount,
                }))

            move = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_line_ids': lines,
            })

            rec.invoice_id = move.id
            rec.state = 'invoiced'

    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise ValidationError(_("No invoice created yet."))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }

    def action_update_state_from_invoice(self):
        for rec in self:
            if not rec.invoice_id:
                rec.state = 'draft'
                continue

            invoice = rec.invoice_id

            if invoice.payment_state == 'paid':
                rec.state = 'paid'
            elif invoice.payment_state in ['partial', 'in_payment']:
                rec.state = 'partial'
            elif invoice.state == 'posted':
                rec.state = 'invoiced'
            else:
                rec.state = 'draft'




class SchoolFeeStructure(models.Model):
    _name = 'school.fee.structure'
    _description = 'Fee Structure'

    name = fields.Char(required=True)

    amount = fields.Float(
        string="Amount",
        required=True
    )

    description = fields.Text()


class SchoolFeeLine(models.Model):
    _name = 'school.fee.line'
    _description = 'Fee Line'

    fee_id = fields.Many2one(
        'school.fee'
    )

    fee_structure_id = fields.Many2one(
        'school.fee.structure',
        required=True
    )

    amount = fields.Float()

    @api.onchange('fee_structure_id')
    def _onchange_fee_structure(self):
        if self.fee_structure_id and not self.amount:
            self.amount = self.fee_structure_id.amount