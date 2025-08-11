export interface MapConfig {
  baseUrl: string;
  dataUrl: string;
  datasetName: string;
  center: [number, number];
  zoom: number;
  projection: string;
  extent: [number, number, number, number];
}

export interface Coordinate {
  lon: number | null;
  lat: number | null;
}

export interface MapLayer {
  id: string;
  name: string;
  layer: any; // ol.layer.Layer - 稍后会处理
  visible: boolean;
}

export interface FeatureInfo {
  [key: string]: any;
}
