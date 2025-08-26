// 选择结果的保存与读取
// 接口（输入数据格式）
// - saveSelectedFeatures(key: string): key 为本地存储键名
// - readSelectedAsGeoJSON(key: string): key 为本地存储键名
// - readSelectedAsFeatures(key: string): key 为本地存储键名
// 数据处理方法（无回退/无校验）
// - 直接从三个 store 收集 ol.Feature[] 合并
// - 使用 ol.format.GeoJSON 写为 GeoJSON Feature 或 FeatureCollection
// - 将序列化结果写入 localStorage 对应 key
// - 从 localStorage 读取并原样返回或反序列化为 ol.Feature[]
// 返回格式（输出数据格式）
// - saveSelectedFeatures: GeoJSON Feature | FeatureCollection
// - readSelectedAsGeoJSON: GeoJSON Feature | FeatureCollection
// - readSelectedAsFeatures: ol.Feature[]

import { useSelectionStore } from '@/stores/selectionStore'
import { useAreaSelectionStore } from '@/stores/areaSelectionStore'
import { useFeatureQueryStore } from '@/stores/featureQueryStore'

// 保存选择结果为 GeoJSON 并写入 localStorage
export function saveSelectedFeatures(key: string) {
  const selectionStore = useSelectionStore()
  const areaStore = useAreaSelectionStore()
  const queryStore = useFeatureQueryStore()

  const writer = new (window as any).ol.format.GeoJSON()
  const all = [
    ...selectionStore.selectedFeatures,
    ...areaStore.selectedFeatures,
    ...queryStore.queryResults
  ]
  const features = all.map((f: any) => writer.writeFeatureObject(f))
  const payload = features.length === 1
    ? features[0]
    : { type: 'FeatureCollection', features }
  ;(window as any).localStorage.setItem(key, JSON.stringify(payload))
  return payload
}

// 读取 GeoJSON（原样返回）
export function readSelectedAsGeoJSON(key: string) {
  const text = (window as any).localStorage.getItem(key) as string
  return JSON.parse(text)
}

// 读取并转回 ol.Feature[]
export function readSelectedAsFeatures(key: string) {
  const data = readSelectedAsGeoJSON(key) as any
  const reader = new (window as any).ol.format.GeoJSON()
  const isFC = data && data.type === 'FeatureCollection'
  const list = isFC ? data.features : [data]
  return list.map((g: any) => reader.readFeature(g))
}

export default {
  saveSelectedFeatures,
  readSelectedAsGeoJSON,
  readSelectedAsFeatures
}


