/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class FishFarmDashboard extends Component {
    static template = "fish_farm_management.FishFarmDashboard";
    
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            loading: true,
            productionData: null,
            pondData: null
        });

        onWillStart(async () => await this.fetchDashboardData());
        onMounted(() => this.renderCharts());
    }

    async fetchDashboardData() {
        this.state.loading = true;
        try {
            const data = await this.rpc("/fish_farm/dashboard/data");
            this.state.productionData = this.prepareChartData(data.production);
            this.state.pondData = this.prepareChartData(data.pondStatus);
        } catch (error) {
            this.notification.add("Failed to load dashboard data", {
                type: 'danger',
                title: 'Error'
            });
            console.error("Dashboard error:", error);
        } finally {
            this.state.loading = false;
        }
    }

    prepareChartData(data) {
        return {
            labels: data.labels,
            datasets: [{
                label: data.label,
                data: data.values,
                backgroundColor: data.backgroundColor,
                borderWidth: 1
            }]
        };
    }

    async refreshData() {
        await this.fetchDashboardData();
        this.renderCharts();
    }

    renderCharts() {
        if (this.state.loading || typeof Chart === 'undefined') return;
        
        try {
            this.renderChart('productionChart', 'bar', this.state.productionData);
            this.renderChart('pondChart', 'doughnut', this.state.pondData);
        } catch (error) {
            console.error("Chart rendering error:", error);
        }
    }

    renderChart(canvasId, type, data) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (ctx) {
            new Chart(ctx, {
                type: type,
                data: data,
                options: this.getChartOptions(type)
            });
        }
    }

    getChartOptions(type) {
        const commonOptions = {
            responsive: true,
            plugins: { legend: { position: 'top' } }
        };
        
        if (type === 'bar') {
            commonOptions.scales = { y: { beginAtZero: true } };
        }
        
        return commonOptions;
    }
}

registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);