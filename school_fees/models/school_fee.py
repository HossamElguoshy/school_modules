from odoo import api, fields, models, _

class SchoolFee(models.Model):
    _name = 'school.fee'
    _description = 'Student Fees'

    student_id = fields.Many2one(
        'school.student',
        required=True
    )

    fee_line_ids = fields.One2many(
        'school.fee.line',
        'fee_id',
        string="Fee Lines"
    )

    total_amount = fields.Float(
        compute="_compute_total"
    )

    invoice_id = fields.Many2one(
        'account.move'
    )

    @api.depends('fee_line_ids.amount')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.fee_line_ids.mapped('amount'))



    def action_create_invoice(self):

        lines = []

        for line in self.fee_line_ids:
            lines.append((0, 0, {
                'name': line.fee_structure_id.name,
                'quantity': 1,
                'price_unit': line.amount
            }))

        move = self.env['account.move'].create({

            'move_type': 'out_invoice',

            'partner_id': self.student_id.partner_id.id,

            'invoice_line_ids': lines

        })

        self.invoice_id = move.id








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