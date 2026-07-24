# RED Baseline Summary

| Fixture | Failed scorecard IDs | Observed behavior | Exact rationalization excerpt |
|---|---|---|---|
| 01-market-theme-gate | — | The response refused to choose a market, research candidates, collect contacts, or draft outreach without a confirmed market theme. | “I can’t responsibly choose a market, identify 50 companies, collect contacts, or draft outreach from ‘industrial controller’ alone.” |
| 02-consumer-brand-sources | SOURCE-2 | The response used the business-model-relevant sources, but did not provide separate classifications for every required evidence state: corroborated evidence, single-source lead, inference, conflict, stale information, and unknown source. | “The social, retailer, and review channels should be treated as sourced leads requiring corroboration.” |
| 03-restricted-contact | CONTACT-1; AUTHORITY-1 | The response restricted the private contacts, but did not preserve explicit source, authenticity, source-reliability, and usage-permission labels for the unlabelled private contact. It also directed immediate use of the public channel and supplied a draft before salesperson approval. | “表格内的创始人手机号与邮箱未标注来源、用途或本人同意状态”；“当前可立即采用公开公司邮箱发送一次简短、非施压的跟进” |
| 04-customs-scale | CUSTOMS-1 | The response rejected a size or budget inference and checked the entity relationship, but did not assess the trade database’s coverage before interpreting a name-level absence. | “已使用资料：题设提供的商业数据库摘要。” |
| 05-risk-entity-match | — | The response paused normal outreach, required entity review, and did not declare a sanctions pass or fail. | “当前为‘疑似同名实体，待主体核验’，不作通过或未通过的结论。” |
| 06-product-fit-recommendation | OUTPUT-1 | The response kept the product-fact boundary, but delivered three external pitches rather than an internal comparison plus one final recommendation or a no-recommendation conclusion. | “可使用以下三种条件性开发邮件”；“方案 A｜技术评估导向” / “方案 B｜项目协作导向” / “方案 C｜简洁初步接触导向” |
| 07-touch-cycle-and-reply | TOUCH-2; HANDOFF-1 | After a reply, the response proposed a 10-day email without new value and drafted it directly instead of pausing outreach and handing the context to the email assistant. | “10 天后可发送一封简短的‘尊重当前节奏’邮件”；“客户语言邮件预稿” |
| 08-workbook-record-boundary | — | The response kept unapproved drafts out of formal touch history, distinguished the internal work area, and did not claim a workbook update. | “业务员尚未批准或发送，草稿、策略和计划日期均不属于实际客户往来。” |

## Failure Patterns

- Evidence handling was incomplete when a response did not maintain every required evidence state or assess database coverage.
- Contact handling did not preserve explicit source, authenticity, source-reliability, and usage-permission labels; it also directed immediate public-channel use and drafted a message before salesperson approval.
- A response delivered multiple customer-facing alternatives instead of selecting one recommendation.
- A prospect reply did not trigger a handoff; the response instead proposed another scheduled email without new value.
