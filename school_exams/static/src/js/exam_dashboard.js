/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ExamDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            filters: {
                academic_year_id: "",
                grade_id: "",
                section_id: "",
                subject_id: "",
                exam_id: "",
            },
            options: {
                academic_years: [],
                grades: [],
                sections: [],
                subjects: [],
                exams: [],
            },
            kpis: {},
            charts: {
                status: [],
                grade_distribution: [],
                subject_average: [],
            },
        });

        onWillStart(async () => {
            await this.loadDashboard();
        });
    }

    async loadDashboard() {
        const data = await this.orm.call("school.exam", "get_exam_dashboard_data", [this.state.filters]);
        this.state.kpis = data.kpis;
        this.state.charts = data.charts;
        this.state.options = data.filters;
    }

    async onFilterChange(ev) {
        const key = ev.target.name;
        const value = ev.target.value;
        this.state.filters[key] = value ? Number(value) : "";
        await this.loadDashboard();
    }
}

ExamDashboard.template = "school_exams.ExamDashboard";
registry.category("actions").add("school_exams.exam_dashboard", ExamDashboard);
