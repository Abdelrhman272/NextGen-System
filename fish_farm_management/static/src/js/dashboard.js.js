/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Fish Farm Dashboard Client‑Action
 * --------------------------------
 * يسجل Client‑Action بالاسم «fish_farm_dashboard» ويعرض تملبْلة  QWeb
 * `fish_farm_dashboard` المُعرَّفة فى `dashboard_views.xml`.
 * بعد التحميل، يجلب البيانات من الـ Endpoint المخصّص ويُظهر KPIs
 * ومخطّطات Chart.js.
 */

export class FishFarmDashboard extends Component {
    static template = "fish_farm_dashboard"; // اسم التمبلِت QWeb

    setup() {
        // خدمات Odoo القياسية
        this.rpc         = useService("rpc");
        this.notification = useService("notification");

        // حالة (state) مبدئية فارغة؛ تُحدَّث بعد استدعاء الـ RPC
        this.state = {
            total_production: 0,
            monthly_production: { labels: [], values: [] },
            pond_status:       { labels: [], values: [] },
        };

        // حمل البيانات عند البدء
        this._loadDashboardData();
    }

    //--------------------------------------------------------------------------
    // RPC
    //--------------------------------------------------------------------------

    async _loadDashboardData() {
        try {
            const result = await this.rpc("/fish_farm/dashboard/data", {});
            this.state   = { ...this.state, ...result };
            // بعد جلب البيانات ارسم المخططات
            this.render();
            this._renderCharts();
        } catch (err) {
            this.notification.add("Cannot load dashboard data", {
                type: "danger",
            });
            // اكتب الخطأ فى الـ Console للمطوّر
            console.error(err);
        }
    }

    //--------------------------------------------------------------------------
    // UI helpers
    //--------------------------------------------------------------------------

    // إعادة تحميل البيانات عند الضغط على زر Refresh (اختيارى)
    onRefreshClick() {
        this._loadDashboardData();
    }

    _renderCharts() {
        // Chart.js يجب أن يكون متاحًا عالميًا فى الصفحة (مثلاً عبر asset bundle)
        if (typeof Chart === "undefined") {
            console.warn("Chart.js not found – charts will not render.");
            return;
        }

        //------------------------------------------------------------------
        // مخطط الإنتاج الشهرى (Bar Chart)
        //------------------------------------------------------------------
        const mp = this.state.monthly_production;
        const mpCanvas = this.el.querySelector("#monthly_production_chart");
        if (mpCanvas && mp.labels.length) {
            new Chart(mpCanvas, {
                type: "bar",
                data: {
                    labels: mp.labels,
                    datasets: [{
                        label: this.env._t("Production (kg)"),
                        data: mp.values,
                        borderWidth: 1,
                    }],
                },
                options: { scales: { y: { beginAtZero: true } } },
            });
        }

        //------------------------------------------------------------------
        // مخطط حالة الأحواض (Doughnut Chart)
        //------------------------------------------------------------------
        const ps = this.state.pond_status;
        const psCanvas = this.el.querySelector("#pond_status_chart");
        if (psCanvas && ps.labels.length) {
            new Chart(psCanvas, {
                type: "doughnut",
                data: {
                    labels: ps.labels,
                    datasets: [{
                        data: ps.values,
                    }],
                },
            });
        }
    }
}

// تسجيل الـ Client‑Action فى الـ Registry
registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);
