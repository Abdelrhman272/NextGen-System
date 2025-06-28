/** @odoo-module **/

// Import necessary components and hooks from Owl and Odoo's web core.
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// Define the dashboard component.
class FishFarmDashboard extends Component {
    // The static template name MUST match the t-name in your XML file exactly.
    static template = "fish_farm_management.fish_farm_dashboard_template";

    setup() {
        // Initialize standard component setup.
        super.setup();

        // Use the standard RPC service from Odoo's core.
        this.rpc = useService("rpc");

        // Set up the component's reactive state.
        this.state = useState({
            loading: true,
            productionData: {},
            pondData: {},
        });

        // Use onWillStart hook to fetch data before the component renders.
        onWillStart(async () => {
            await this.fetchDashboardData();
        });

        // Use onMounted hook to render charts after the component is in the DOM.
        onMounted(() => {
            this.renderCharts();
        });
    }

    /**
     * Fetches all necessary data from the backend via a single RPC call.
     */
    async fetchDashboardData() {
        this.state.loading = true;
        try {
            // Call the Python method on the backend to get dashboard data.
            const data = await this.rpc("/fish_farm/dashboard/data");
            
            // Prepare and assign data to the component's state.
            this.state.productionData = this._prepareChartData(
                data.production.months,
                'Monthly Production',
                data.production.values,
                '#4CAF50' // Green
            );
            this.state.pondData = this._prepareChartData(
                data.pondStatus.statuses,
                'Pond Status',
                data.pondStatus.counts,
                ['#FF6384', '#36A2EB', '#FFCE56'] // Red, Blue, Yellow
            );
        } catch (error) {
            console.error("Odoo Dashboard Error: Could not fetch data.", error);
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * A helper function to prepare chart data configuration.
     */
    _prepareChartData(labels, datasetLabel, data, backgroundColor) {
        return {
            labels: labels,
            datasets: [{
                label: datasetLabel,
                data: data,
                backgroundColor: backgroundColor,
                borderWidth: 1
            }]
        };
    }

    /**
     * Renders all charts once the component is mounted and data is available.
     */
    renderCharts() {
        // Check if Chart.js library is loaded.
        if (typeof window.Chart === 'undefined') {
            console.error("Chart.js is not loaded. Make sure it's included in the assets.");
            return;
        }

        // Render both charts.
        this._renderChart('productionChart', 'bar', this.state.productionData, 'Monthly Production');
        this._renderChart('pondChart', 'doughnut', this.state.pondData, 'Pond Status');
    }

    /**
     * Generic function to render a single chart.
     */
    _renderChart(canvasId, type, data, title) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (ctx) {
            new window.Chart(ctx, {
                type: type,
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: title }
                    },
                    scales: (type === 'bar') ? { y: { beginAtZero: true } } : {}
                }
            });
        }
    }
}

// Register the component in Odoo's action registry so it can be called from an action.
registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);
