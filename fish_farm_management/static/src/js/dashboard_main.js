// Fish Farm Dashboard component for Fish Farm Management

import { Component, xml, onWillStart, useRef, onMounted } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";               // ← استيراد registry
import { Layout } from "@web/core/layout";                 // ← استيراد Layout
import Chart from '../lib/chart/chart.umd.js';

export class FishFarmDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.rpc = jsonrpc;
        this.action = useService("action");

        this.kpis = {};
        this.charts = {};
        this.recentAlerts = { water_quality: [] };

        this.costChartRef = useRef("costChart");
        this.harvestChartRef = useRef("harvestChart");
        this.pondStatusChartRef = useRef("pondStatusChart");

        onWillStart(async () => {
            await this._fetchDashboardData();
        });

        onMounted(() => {
            this._renderCharts();
        });
    }

    async _fetchDashboardData() {
        try {
            const data = await this.rpc(
                '/fish_farm_management/dashboard_data', {}
            );
            this.kpis = data.kpis;
            this.charts = data.charts;
            this.recentAlerts = data.recent_alerts;
        } catch (error) {
            console.error(
                "Error fetching dashboard data:", error
            );
        }
    }

    _renderCharts() {
        // Costs by type
        if (
            this.charts.cost_by_type && this.costChartRef.el
        ) {
            new Chart(this.costChartRef.el, {
                type: 'bar',
                data: this.charts.cost_by_type,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: _t(
                                'Costs by Type (Last 6 Months)'
                            ),
                        },
                    },
                    scales: { x: { stacked: true }, y: { stacked: true } },
                },
            });
        }

        // Harvest by month
        if (
            this.charts.harvest_by_month && this.harvestChartRef.el
        ) {
            new Chart(this.harvestChartRef.el, {
                type: 'line',
                data: this.charts.harvest_by_month,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: _t(
                                'Monthly Harvest (Last 12 Months)'
                            ),
                        },
                    },
                    scales: { y: { beginAtZero: true } },
                },
            });
        }

        // Pond status distribution
        if (
            this.charts.pond_status_distribution &&
            this.pondStatusChartRef.el
        ) {
            new Chart(this.pondStatusChartRef.el, {
                type: 'pie',
                data: this.charts.pond_status_distribution,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: _t('Pond Status Distribution'),
                        },
                    },
                },
            });
        }
    }
}

FishFarmDashboard.template = xml`
    <Layout class="o_fish_farm_dashboard">
        <!-- template content unchanged -->
    </Layout>
`;

registry.category("actions").add(
    "fish_farm_management.dashboard",
    FishFarmDashboard
);