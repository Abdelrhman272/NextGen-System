/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FishFarmDashboard extends Component {
  static template = "fish_farm_management.Dashboard";

  setup() {
    this.rpc = useService("rpc");
    this.notification = useService("notification");

    this.state = useState({
      loading: true,
      productionData: null,
      pondData: null,
    });

    onWillStart(async () => {
      await this.loadDashboardData();
    });

    onMounted(() => {
      if (!this.state.loading) {
        this.renderCharts();
      }
    });
  }

  async loadDashboardData() {
    try {
      const data = await this.rpc("/fish_farm/dashboard/data");
      this.state.productionData = data.production;
      this.state.pondData = data.pondStatus;
      this.state.loading = false;
    } catch (error) {
      this.notification.add("Failed to load dashboard data", {
        type: "danger",
      });
      console.error("Dashboard error:", error);
    }
  }

  renderCharts() {
    if (typeof window.Chart === "undefined") {
      console.error("Chart.js is not loaded");
      return;
    }

    // Production Chart
    const productionCtx = this.el
      .querySelector("#productionChart")
      ?.getContext("2d");
    if (productionCtx && this.state.productionData) {
      new window.Chart(productionCtx, {
        type: "bar",
        data: this.state.productionData,
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true },
          },
        },
      });
    }

    // Pond Status Chart
    const pondCtx = this.el.querySelector("#pondChart")?.getContext("2d");
    if (pondCtx && this.state.pondData) {
      new window.Chart(pondCtx, {
        type: "doughnut",
        data: this.state.pondData,
        options: { responsive: true },
      });
    }
  }
}

registry.category("actions").add("fish_farm_dashboard", FishFarmDashboard);
