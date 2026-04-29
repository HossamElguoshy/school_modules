{
    "name": "School Core ",
    "version": "18.0.1.0.0",
    "category": "Education",
    "summary": "Academic structure, Students/Guardians, Admissions (Community-first)",
    "depends": ["base", "mail", "contacts", "portal","school_base"],
    "data": [

        "security/school_groups.xml",
        "security/school_rules.xml",
        "security/ir.model.access.csv",

        "data/sequences.xml",

        "views/menus.xml",
        "views/academic_view.xml",
        "views/student.xml",
        "views/application_views.xml",

    ],
    "application": True,
    "license": "LGPL-3",
}