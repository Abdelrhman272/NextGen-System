/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class FishFarmDashboard extends Component {
    /* ─────────────────────────────
       ① السماح لكل الـ props التي يمرّرها الـ ActionController
    ─────────────────────────────── */
    static props = {
        action:            { type: Object,   optional: true },
        actionId:          { type: Number,   optional: true },
        updateActionState: { type: Function, optional: true },
        className:         { type: String,   optional: true },
    };

    /* ② اسم الـ template */
    static template = "fish_farm_management.fish_farm_dashboard_template";

    setup() {
        super.setup();
        this.rpc = useService("rpc");

        this.state = useState({
            loading: true,
            productionData: {},
            pondData: {},
        });

        onWillStart(async () => { await this._fetchData(); });
        onMounted(      ()   => {    this._renderCharts(); });
    }

    /* ‥ fetch ──────────────────────────────────────────── */
    async _fetchData() {
        this.state.loading = true;
        try {
            const data = await this.rpc("/fish_farm/dashboard/data");

            this.state.productionData = this._chartData(
                data.production.months,
                "Monthly Production",
                data.production.values,
                "#4CAF50",
            );
            this.state.pondData = this._chartData(
                data.pondStatus.statuses,
                "Pond Status",
                data.pondStatus.counts,
                ["#FF6384", "#36A2EB", "#FFCE56"],
            );
        } catch (err) {
            console.error("FishFarmDashboard - RPC error:", err);
        } finally {
            this.state.loading = false;
        }
    }

    /* ‥ helpers ────────────────────────────────────────── */
    _chartData(labels, label, data, color) {
        return {
            labels,
            datasets: [{ label, data, backgroundColor: color, borderWidth: 1 }],
        };
    }

    _renderCharts() {
        if (!window.Chart) { return console.warn("Chart.js missing"); }
        this._makeChart("productionChart", "bar",      this.state.productionData);
        this._makeChart("pondChart",       "doughnut", this.state.pondData);
    }

    _makeChart(canvasId, type, data) {
        const ctx = document.getElementById(canvasId)?.getContext("2d");
        if (!ctx) { return; }
        new Chart(ctx, {
            type,
            data,
            options: {
                responsive: true,
                plugins: { legend:{ position:"top" } },
                scales: type === "bar" ? { y:{ beginAtZero:true } } : {},
            },
        });
    }
}

/* ③ تسجيل الـ action */
registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);
export default FishFarmDashboard;
