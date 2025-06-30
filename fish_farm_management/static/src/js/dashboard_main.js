/** @odoo-module **/

import { Component, xml, onWillStart, useRef, onMounted } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";

// Import Chart.js (assuming it's loaded in Odoo's web.assets_backend)
// If not, you might need to add it to your manifest's assets as a direct link or dependency
// e.g., 'web_editor.assets_libraries' or specific path
import Chart from 'chart.js/auto'; // This assumes Chart.js is properly available

export class FishFarmDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.rpc = jsonrpc; // Direct access to jsonrpc
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
            const data = await this.rpc('/fish_farm_management/dashboard_data', {});
            this.kpis = data.kpis;
            this.charts = data.charts;
            this.recentAlerts = data.recent_alerts;
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            // Handle error, e.g., show a message to the user
        }
    }

    _renderCharts() {
        if (this.charts.cost_by_type && this.costChartRef.el) {
            new Chart(this.costChartRef.el, {
                type: 'bar',
                data: this.charts.cost_by_type,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: _t('Costs by Type (Last 6 Months)'),
                        }
                    },
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true, beginAtZero: true }
                    }
                }
            });
        }

        if (this.charts.harvest_by_month && this.harvestChartRef.el) {
            new Chart(this.harvestChartRef.el, {
                type: 'line',
                data: this.charts.harvest_by_month,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: _t('Monthly Harvest Production (Last 12 Months)'),
                        }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        if (this.charts.pond_status_distribution && this.pondStatusChartRef.el) {
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
                        }
                    }
                }
            });
        }
    }
}

// Define the XML template for the dashboard
FishFarmDashboard.template = xml`
    <Layout class="o_fish_farm_dashboard">
        <div class="o_dashboard_header">
            <h1><i class="fa fa-fish"></i> <t t-esc="_t('Fish Farm Overview')"/></h1>
        </div>

        <div class="o_dashboard_content">
            <div class="row o_kpis">
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="o_kpi_card bg-primary text-white">
                        <div class="o_kpi_value"><t t-esc="kpis.active_ponds_count"/></div>
                        <div class="o_kpi_label"><t t-esc="_t('Active Ponds')"/></div>
                        <i class="o_kpi_icon fa fa-pond"></i>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="o_kpi_card bg-success text-white">
                        <div class="o_kpi_value"><t t-esc="kpis.total_harvest_month ? kpis.total_harvest_month.toFixed(2) : 0"/> kg</div>
                        <div class="o_kpi_label"><t t-esc="_t('Harvest This Month')"/></div>
                        <i class="o_kpi_icon fa fa-balance-scale"></i>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="o_kpi_card bg-warning text-dark">
                        <div class="o_kpi_value"><t t-esc="kpis.total_costs_month ? kpis.total_costs_month.toFixed(2) : 0"/> <t t-esc="env.company.currency.symbol"/></div>
                        <div class="o_kpi_label"><t t-esc="_t('Costs This Month')"/></div>
                        <i class="o_kpi_icon fa fa-money"></i>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="o_kpi_card bg-info text-white">
                        <div class="o_kpi_value"><t t-esc="kpis.total_feed_consumed_month ? kpis.total_feed_consumed_month.toFixed(2) : 0"/> kg</div>
                        <div class="o_kpi_label"><t t-esc="_t('Feed Consumed This Month')"/></div>
                        <i class="o_kpi_icon fa fa-cutlery"></i>
                    </div>
                </div>
            </div>

            <div class="row o_charts">
                <div class="col-lg-6 mb-4">
                    <div class="o_chart_card">
                        <canvas t-ref="costChart"></canvas>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="o_chart_card">
                        <canvas t-ref="harvestChart"></canvas>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="o_chart_card">
                        <canvas t-ref="pondStatusChart"></canvas>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="o_chart_card">
                        <h4><t t-esc="_t('Recent Water Quality Alerts')"/></h4>
                        <table class="table table-sm mt-3">
                            <thead>
                                <tr>
                                    <th><t t-esc="_t('Pond')"/></th>
                                    <th><t t-esc="_t('Date')"/></th>
                                    <th><t t-esc="_t('Reason')"/></th>
                                </tr>
                            </thead>
                            <tbody>
                                <t t-if="recentAlerts.water_quality and recentAlerts.water_quality.length > 0">
                                    <t t-foreach="recentAlerts.water_quality" t-as="alert" t-key="alert_index">
                                        <tr>
                                            <td><t t-esc="alert.pond_name"/></td>
                                            <td><t t-esc="alert.reading_date"/></td>
                                            <td><t t-esc="alert.alert_reason"/></td>
                                        </tr>
                                    </t>
                                </t>
                                <t t-else="">
                                    <tr>
                                        <td colspan="3" class="text-center"><t t-esc="_t('No recent alerts.')"/></td>
                                    </tr>
                                </t>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </Layout>
`;

// Register the dashboard component in the client actions registry
registry.category("actions").add("fish_farm_management.dashboard", FishFarmDashboard);