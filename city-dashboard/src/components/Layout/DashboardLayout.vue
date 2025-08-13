<template>
  <div class="dashboard-layout">
    <DashboardHeader />
    
    <div class="screen-main">
      <splitpanes class="default-theme">
        <pane size="75">
          <div class="map-container">
            <SuperMapViewer />
          </div>
        </pane>
        <pane size="25">
          <div class="right-panel-container">
            <RightPanel />
          </div>
        </pane>
      </splitpanes>
    </div>
  </div>
</template>

<script setup lang="ts">
import DashboardHeader from './DashboardHeader.vue'
import SuperMapViewer from '../Map/SuperMapViewer.vue'
import RightPanel from './RightPanel.vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
</script>

<style>
.splitpanes__pane {
  background-color: transparent !important;
}
.splitpanes__splitter {
  background-color: transparent !important;
  position: relative;
  width: 5px !important;
  border: none !important;
  transition: background-color 0.2s ease-in-out;
}
.splitpanes__splitter:before {
  content: '';
  position: absolute;
  left: -2px;
  top: 0;
  width: 10px;
  height: 100%;
  background: transparent;
  z-index: 1;
  transition: background-color 0.2s ease-in-out;
}
.splitpanes__splitter:hover:before {
  background-color: rgba(66, 165, 245, 0.2) !important;
}
.splitpanes__splitter:hover {
    background-color: var(--primary-color) !important;
}

</style>

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
  width: 100%;
  padding: 16px;
}

.map-container {
  width: 100%;
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
  width: 100%;
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
