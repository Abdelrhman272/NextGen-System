/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class FishFarmDashboard extends Component {
    static template = "fish_farm_management.template_fish_farm_dashboard";
    static props = {};

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            productionData: null,
            pondData: null,
            activities: [],
        });

        onWillStart(async () => {
            await this.fetchDashboardData();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async fetchDashboardData() {
        this.state.loading = true;
        try {
            const data = await this.rpc("/fish_farm/dashboard/data");
            
            this.state.productionData = {
                labels: data.production.months,
                datasets: [{
                    label: 'Production (Kg)',
                    data: data.production.values,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            };
            
            this.state.pondData = {
                labels: data.pondStatus.statuses,
                datasets: [{
                    data: data.pondStatus.counts,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56'
                    ],
                    borderWidth: 1
                }]
            };
            
            this.state.activities = data.activities;
        } catch (error) {
            console.error("Dashboard error:", error);
            this.notification.add("Failed to load dashboard data", {
                type: 'danger',
                title: 'Error'
            });
        } finally {
            this.state.loading = false;
        }
    }

    async refreshData() {
        await this.fetchDashboardData();
        this.renderCharts();
    }

    renderCharts() {
        if (this.state.loading || !window.Chart) return;

        try {
            // Production Chart (Bar)
            new Chart(
                document.getElementById('productionChart').getContext('2d'),
                {
                    type: 'bar',
                    data: this.state.productionData,
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                }
            );

            // Pond Chart (Doughnut)
            new Chart(
                document.getElementById('pondChart').getContext('2d'),
                {
                    type: 'doughnut',
                    data: this.state.pondData,
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'right' }
                        }
                    }
                }
            );
        } catch (error) {
            console.error("Chart error:", error);
        }
    }
}

registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);