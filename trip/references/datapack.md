# 数据包结构规范（data/<目的地>/）

## config.json — 住宿序列（必须闭环）

```json
{
  "trip": "显示名",
  "start_date": "YYYY-MM-DD",
  "days": [
    {"d": 1, "date": "YYYY-MM-DD", "label": "显示标签",
     "start_node": "hotel_a", "end_node": "hotel_a_out"},
    {"d": 2, "date": "...", "label": "...",
     "start_node": "hotel_a_out", "end_node": "hotel_b"}
  ],
  "day_start_min": 450,
  "day_end_min": 1290,
  "beta_drive": 0.08
}
```

- 闭环铁律: `days[n].start_node == days[n-1].end_node`
- 同日往返(住宿不变): end 用 `hotel_x_out` 虚拟节点, 在 hubs.hotels 里映射到同一城镇
- 纯赶路日是合法天(hotel->hotel), 不要强行塞景点

## pois.json — 景点池

```json
{"pois": [{
  "id": "pinyin_id", "name": "中文名", "hub": "城镇id",
  "lon": 0.0, "lat": 0.0,          // 粗略值即可, fetch_amap 会覆盖
  "visit_hours": 2.5,
  "open_min": 480, "close_min": 1080,   // 分钟制 480=08:00
  "score": 85, "must": false,
  "allowed_days": [2, 3],           // 可选日(天号), 冻结点给 []
  "cost": 100,
  "weather": "any",                 // sunny | rain_ok | any
  "closed_weekdays": [0],           // 0=周一, 可选
  "reservation": {"platform": "xx小程序", "lead_days": "提前1-15天"},
  "notes": "避坑/玩法/店铺,渲染到作战卡"
}]}
```

## hubs.json — 城镇图

```json
{
  "hotels": {"hotel_a": "citya", "hotel_a_out": "citya"},
  "hub_drive_min": {"citya-cityb": 120},   // 无序对,一条即可
  "poi_offset_min": {"poi1": 10},          // POI 距住宿锚点的加时
  "default_same_hub_min": 15
}
```

## preferences.json — 方案族（可选,缺省用 engine 内置 7 套）

```json
{
  "presets": [
    {"key": "planA", "name": "全收录", "desc": "...",
     "exclude": ["凑数点"],        // 或用 "only": [...] 白名单
     "must": ["huangguoshu"],
     "day_start": 450,             // 出门时间(分钟)
     "beta": 0.08}                 // 车程惩罚: 0.08宽松 ~ 0.5极简
  ],
  "same_day_pairs": [["tangan", "zhaoxing"]]   // 绑定同日
}
```

## 生成文件（脚本自动,勿手改）

- `matrix_amap.json` — fetch_amap 产物: 全节点两两真实车程(分钟)
- `legs_planX.json` — fetch_legs_multi 产物: 每段路线几何(高德 polyline 抽稀150点)
- `pois_amap.json` — 节点精确坐标 {"id": [lon, lat]}

## 冻结/砍点操作

- 暂时不去(如换动线): `allowed_days: []`, 保留数据
- 彻底不要: 从 pois.json 删除
