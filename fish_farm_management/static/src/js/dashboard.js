/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";

export class FishFarmDashboard extends Component {
    static template = "fish_farm_management.Dashboard";

    setup() {
        this.state = useState({
            loading: true,
            chartData: {}
        });

        onWillStart(async () => {
            await this.loadChartData();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async loadChartData() {
        // جلب البيانات من الخادم
        this.state.chartData = await this.env.services.rpc({
            route: "/fish_farm/dashboard/data",
        });
        this.state.loading = false;
    }

    renderCharts() {
        // تأكد من توفر Chart.js
        if (typeof window.Chart === 'undefined') {
            console.error("Chart.js is not loaded");
            return;
        }

        // مخطط الإنتاج الشهري
        const productionCtx = document.getElementById('productionChart')?.getContext('2d');
        if (productionCtx) {
            new window.Chart(productionCtx, {
                type: 'bar',
                data: this.state.chartData.production,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                    }
                }
            });
        }

        // مخطط حالة الأحواض
        const pondCtx = document.getElementById('pondChart')?.getContext('2d');
        if (pondCtx) {
            new window.Chart(pondCtx, {
                type: 'doughnut',
                data: this.state.chartData.pondStatus,
                options: {
                    responsive: true
                }
            });
        }
    }
}

registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);