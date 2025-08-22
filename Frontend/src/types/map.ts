export interface WuhanLayer {
  name: string
  type: 'point' | 'line' | 'polygon' | 'raster'
  visible: boolean
  group?: string
  datasetName?: string
  dataService?: string
}

export interface APIConfig {
  baseUrl: string
  mapService: string
  dataService: string
  datasetName: string
  wuhanLayers: WuhanLayer[]
  timeout: number
  retryCount: number
  devMode: boolean
}

export interface MapConfig {
  baseUrl: string;
  dataUrl: string;
  datasetName: string;
  vectorLayers: VectorLayerConfig[];
  center: [number, number];
  zoom: number;
  projection: string;
  extent: [number, number, number, number];
}

export interface VectorLayerConfig {
  name: string
  style?: {
    stroke?: { width: number; color?: string }
    fill?: { color: string }
  }
}

export interface Coordinate {
  lon: number | null;
  lat: number | null;
}

export interface MapLayer {
  id: string;
  name: string;
  layer: any; // ol.layer.Base
  visible: boolean;
  type: 'vector' | 'raster' | 'tile';
  source?: 'supermap' | 'local' | 'external';
  error?: string;
}

export interface FeatureInfo {
  id: string;
  name: string;
  type: string;
  geometry: any; // ol.geom.Geometry
}

export interface ServiceResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  code?: number
}
