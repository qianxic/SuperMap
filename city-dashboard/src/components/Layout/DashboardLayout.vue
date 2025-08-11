<template>
  <div class="dashboard-layout">
    <DashboardHeader />
    
    <div class="screen-main">
      <div class="map-container">
        <SuperMapViewer />
      </div>
      <div class="right-panel-container">
        <PanelWindow 
          :visible="true" 
          :embed="true" 
          :width="'100%'" 
          :height="'100%'"
        >
          <RightPanel />
        </PanelWindow>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DashboardHeader from './DashboardHeader.vue'
import SuperMapViewer from '../Map/SuperMapViewer.vue'
import RightPanel from './RightPanel.vue'
import PanelWindow from '../UI/PanelWindow.vue'
</script>

<style scoped>
.dashboard-layout {
  height: 100vh;
  width: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: "Segoe UI", PingFang SC, Microsoft YaHei, Arial, sans-serif;
  overflow: hidden;
}

.screen-main {
  height: calc(100vh - 64px);
  padding: 16px;
  display: flex;
  gap: 16px;
}

.map-container {
  flex: 3;
  height: 100%;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  padding: 10px;
  position: relative;
  overflow: hidden;
}

.right-panel-container {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  padding: 10px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.panel:hover {
  transform: translateY(-2px);
  box-shadow: var(--glow), 0 8px 25px rgba(0, 0, 0, 0.3);
  border-color: rgba(66, 165, 245, 0.5);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .screen-main {
    padding: 12px;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .screen-main { 
    padding: 8px; 
    flex-direction: column;
  }
  .map-container { 
    padding: 8px; 
    flex: none;
    height: 60%;
  }
  .right-panel-container {
    flex: none;
    height: 40%;
  }
}
</style>
