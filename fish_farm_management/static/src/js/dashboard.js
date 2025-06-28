/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class FishFarmDashboard extends Component {
    static template = "fish_farm_management.fish_farm_dashboard_template";
    
    setup() {
        super.setup(); // ضروري للإصدارات الحديثة من Owl
        
        // تهيئة حالة المكون
        this.state = useState({
            loading: true,
            productionData: null,
            pondData: null
        });

        // الحصول على خدمات RPC بطريقة متوافقة مع جميع الإصدارات
        try {
            this.rpc = useService("rpc") || this.env.services.rpc;
        } catch (error) {
            console.error("Error initializing RPC service:", error);
            this.rpc = this._createFallbackRPC();
        }

        // تحميل البيانات عند بدء المكون
        onWillStart(async () => {
            await this.loadDashboardData();
        });

        // رسم المخططات بعد تحميل البيانات
        onMounted(() => {
            if (!this.state.loading) {
                this.renderCharts();
            }
        });
    }

    // دالة بديلة لخدمة RPC في حالة فشل الحصول عليها
    _createFallbackRPC() {
        return {
            async route(route, params) {
                try {
                    const response = await fetch(route, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Owlbear': 'true' // لتجنب مشاكل CSRF
                        },
                        body: JSON.stringify(params),
                    });
                    return await response.json();
                } catch (error) {
                    console.error("RPC Fallback failed:", error);
                    throw error;
                }
            }
        };
    }

    async loadDashboardData() {
        try {
            const data = await this.rpc("/fish_farm/dashboard/data", {
                context: this.env.session.user_context
            });
            
            this.state.productionData = this._prepareProductionData(data.production);
            this.state.pondData = this._preparePondData(data.pondStatus);
            this.state.loading = false;
            
        } catch (error) {
            console.error("Failed to load dashboard data:", error);
            this.state.loading = false;
            // يمكنك إضافة معالجة إضافية للأخطاء هنا
        }
    }

    // معالجة بيانات الإنتاج قبل العرض
    _prepareProductionData(rawData) {
        return {
            labels: rawData.months,
            datasets: [{
                label: 'الإنتاج الشهري',
                data: rawData.values,
                backgroundColor: '#4CAF50',
                borderColor: '#388E3C',
                borderWidth: 1
            }]
        };
    }

    // معالجة بيانات الأحواض قبل العرض
    _preparePondData(rawData) {
        return {
            labels: rawData.statuses,
            datasets: [{
                data: rawData.counts,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56'
                ],
                hoverBackgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56'
                ]
            }]
        };
    }

    renderCharts() {
        if (typeof window.Chart === 'undefined') {
            console.warn("Chart.js library not loaded");
            return;
        }

        // رسم مخطط الإنتاج
        this._renderProductionChart();
        
        // رسم مخطط حالة الأحواض
        this._renderPondChart();
    }

    _renderProductionChart() {
        const ctx = document.getElementById('productionChart')?.getContext('2d');
        if (ctx && this.state.productionData) {
            new window.Chart(ctx, {
                type: 'bar',
                data: this.state.productionData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                            rtl: true
                        },
                        title: {
                            display: true,
                            text: 'الإنتاج الشهري'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'الكمية'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'الشهر'
                            }
                        }
                    }
                }
            });
        }
    }

    _renderPondChart() {
        const ctx = document.getElementById('pondChart')?.getContext('2d');
        if (ctx && this.state.pondData) {
            new window.Chart(ctx, {
                type: 'doughnut',
                data: this.state.pondData,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right',
                            rtl: true
                        },
                        title: {
                            display: true,
                            text: 'حالة الأحواض'
                        }
                    }
                }
            });
        }
    }
}

// تسجيل المكون كنوع من الإجراءات
registry.category("actions").add("fish_farm_dashboard", {
    component: FishFarmDashboard,
    // يمكنك إضافة خصائص إضافية هنا إذا لزم الأمر
});