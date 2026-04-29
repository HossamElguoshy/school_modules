{
    "name": "School exams",
    "version": "18.0.1.0.0",
    "depends": ["school_core", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/school_exam_views.xml",
        "views/exam_dashboard_views.xml",
        "views/menu.xml",
		"report/school_exam_report.xml",
],
    "assets": {
        "web.assets_backend": [
            "school_exams/static/src/scss/exam_dashboard.scss",
            "school_exams/static/src/xml/exam_dashboard.xml",
            "school_exams/static/src/js/exam_dashboard.js",
        ],
    },
    "application": False,
}
