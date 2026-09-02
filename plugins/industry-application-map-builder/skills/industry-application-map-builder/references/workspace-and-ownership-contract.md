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
│   └── 行业语义研究/<research_contract_id>/
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
| `salesperson_workbench` 六页业务前台 | `foreign-trade-workflow-director` | 只输出带来源引用的业务投影；不直接写入 |

根索引只保存版本、哈希、公司编号和路径。共享底座不得成为跨公司产品事实通道。跨公司比较只能写入单独获授权的工作区。

本技能的 4/8/8 页工作簿是机器证据后台。不得通过改名、删页或把业务员决定直接塞入共享底座来制造“业务前台”。协调器的业务工作簿位于公司工作区，由稳定编号和包引用回溯本技能记录，不属于本地图根的事实所有权。

## 行业语义研究工作区

每个冻结合同使用独立的 `05-工作区/行业语义研究/<research_contract_id>/`，包含合同、节点快照、校准案例、baseline/candidate原始运行、模型交接、证据包、反向审计、报告和隔离失败返回。

初始化器拒绝覆盖。原始运行、模型返回和审计记录追加保存；合同版本变化创建新运行，不原地改历史。校准阶段 `allowed_writes` 只能指向本研究工作区，禁止写 `02-共享应用知识/industry-application-base.xlsx`。正式底座写入必须另有显式 `application_base_write_authorization = true`。

## 初始化与回滚

初始化器拒绝覆盖现有根目录或公司目录，并为公司创建空的 `route-pool-export-registry.json`。共享来源文件一旦封存不得原地修改；新版本作为新来源加入。派生地图可恢复到变更记录中的先前版本，但不得删除原始来源和历史记录。

## 输入快照

公司地图必须记录单产品事实包，或多产品 `company_product_packet_manifest`，以及 `facts.json`、行业骨架和应用底座的绝对路径与SHA-256。业务确认路线还必须记录 `business_validated_industry_register` 的路径与SHA-256。任一哈希变化都使依赖路线进入待复核状态；在完成复核前不得导出为当前路线候选或有限方向验证输入。

每个路线池导出包也必须保存在本公司目录，并由同目录生产者登记记录哈希和输入快照。下游只能读取登记状态为 `current` 且哈希、公司、导出ID和快照均一致的包；登记缺失或包被篡改时不得继续。
