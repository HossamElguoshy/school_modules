# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class SchoolPortal(http.Controller):

        @http.route('/my/students', type='http', auth='user', website=True)
        def portal_my_students(self):
            partner = request.env.user.partner_id

            students = request.env['school.student'].sudo().search([
                ('guardian_partner_ids', 'in', partner.id)
            ])

            print("Partner ID:", partner.id)
            print("Student IDs:", students.ids)

            return request.render('school_portal.portal_my_students', {
                'students': students
            })

        @http.route('/my/student/<int:student_id>', type='http', auth='user', website=True)
        def portal_student_detail(self, student_id):
            partner = request.env.user.partner_id

            student = request.env['school.student'].sudo().search([
                ('id', '=', student_id),
                ('guardian_partner_ids', 'in', partner.id)
            ], limit=1)

            if not student:
                return request.redirect('/my')

            exams = request.env['school.exam.line'].sudo().search([
                ('student_id', '=', student.id)
            ])

            fees = request.env['school.fee'].sudo().search([
                ('student_id', '=', student.id)
            ])
            # من fees جلب الفواتير المرتبطة فقط
            invoices = fees.mapped('invoice_id')

            return request.render('school_portal.portal_student_detail', {
                'student': student,
                'exams': exams,
                'invoices': invoices
            })