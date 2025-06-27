/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FishFarmDashboard extends Component {
    static template = "fish_farm_management.fish_farm_dashboard";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            loading: true,
            total_production: 0,
            monthly_production: { labels: [], values: [] },
            pond_status: { labels: [], values: [] }
        });

        onMounted(() => this._loadDashboardData());
    }

    async _loadDashboardData() {
        try {
            const data = await this.rpc("/fish_farm/dashboard/data");
            Object.assign(this.state, data);
            this.state.loading = false;
            this._renderCharts();
        } catch (error) {
            this.notification.add(this.env._t("Failed to load dashboard data"), {
                type: "danger"
            });
            console.error("Dashboard error:", error);
        }
    }

    _renderCharts() {
        if (typeof Chart === "undefined") return;

        // Monthly Production Chart
        const mpCtx = document.getElementById('monthly_production_chart')?.getContext('2d');
        if (mpCtx) {
            new Chart(mpCtx, {
                type: 'bar',
                data: {
                    labels: this.state.monthly_production.labels,
                    datasets: [{
                        label: this.env._t("Production (kg)"),
                        data: this.state.monthly_production.values,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)'
                    }]
                },
                options: { responsive: true }
            });
        }

        // Pond Status Chart
        const psCtx = document.getElementById('pond_status_chart')?.getContext('2d');
        if (psCtx) {
            new Chart(psCtx, {
                type: 'doughnut',
                data: {
                    labels: this.state.pond_status.labels,
                    datasets: [{
                        data: this.state.pond_status.values,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.5)',
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(255, 206, 86, 0.5)'
                        ]
                    }]
                }
            });
        }
    }
}

registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);