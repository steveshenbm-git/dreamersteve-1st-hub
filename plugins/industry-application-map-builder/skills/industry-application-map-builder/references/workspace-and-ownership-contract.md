# 工作区与所有权合同

## 固定目录

```text
industry-application-map-root/
├── AGENTS.md
├── 00-管理/map-registry.json
├── 00-管理/change-log.json
├── 01-共享行业骨架/industry-taxonomy.xlsx
├── 02-共享应用知识/industry-application-base.xlsx
├── 03-共享来源封存/
├── 04-公司地图/<company_id>/
│   ├── company-industry-application-map.xlsx
│   ├── company-route-pool-packet.json
│   ├── route-pool-export-registry.json
│   └── review-log.json
├── 05-工作区/
└── 06-风险隔离/
```

## 所有权

| 数据 | 所有者 | 本技能权限 |
|---|---|---|
| 公司原始资料、事实、证据等级、产品体系 | `company-product-knowledge-builder` | 只读引用 |
| 官方行业骨架、产品中性应用事实 | 本技能共享底座 | 获授权后新增或修订 |
| 公司能力映射、路线、覆盖、排除与暂缓 | 本技能单公司目录 | 获授权后新增或修订 |
| 开发方向、客户扫描、背调 | `foreign-trade-customer-development` | 只输出交接包 |
| 方向确认、优先级、客户选择 | 业务员 | 不得代写 |

根索引只保存版本、哈希、公司编号和路径。共享底座不得成为跨公司产品事实通道。跨公司比较只能写入单独获授权的工作区。

## 初始化与回滚

初始化器拒绝覆盖现有根目录或公司目录，并为公司创建空的 `route-pool-export-registry.json`。共享来源文件一旦封存不得原地修改；新版本作为新来源加入。派生地图可恢复到变更记录中的先前版本，但不得删除原始来源和历史记录。

## 输入快照

公司地图必须记录产品事实包、`facts.json`、行业骨架和应用底座的绝对路径与SHA-256。任一哈希变化都使依赖路线进入待复核状态；在完成复核前不得导出为当前路线候选。

每个路线池导出包也必须保存在本公司目录，并由同目录生产者登记记录哈希和输入快照。下游只能读取登记状态为 `current` 且哈希、公司、导出ID和快照均一致的包；登记缺失或包被篡改时不得继续。
