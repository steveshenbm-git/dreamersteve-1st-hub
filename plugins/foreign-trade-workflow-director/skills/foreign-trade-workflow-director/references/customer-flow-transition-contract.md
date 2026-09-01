# 客户流程硬链接合同

本合同约束 `candidate_development` 与 `customer_operations` 内部的跨技能交接。业务大阶段不新增；客户开发、客户运营、客户沟通和控制器只按登记状态协作。任何一段缺少前一段验收、绑定哈希或所需人工决定，都必须返回 `FAIL`，不得从后续技能补造前序事实。

机器权威清单是 `../assets/customer-flow-transition-registry.v1.json`。它登记来源包根名、来源状态字段、绑定角色对应的合同根名、允许的人工决定类型、载荷根名和精确下一动作。本文解释人可读含义；若文字与机器清单不一致，停止并修复两者，不能任选一个继续。

## 固定状态

- `DEVELOPMENT_READY`：客户开发已经形成可交接的开发结果。
- `THREAD_ACCEPTED`：运营已验收开发交接并建立客户线程。
- `INBOUND_OR_SUSPECTED_REPLY_CAPTURED`：开发侧捕获了回复或疑似回复证据，尚未由运营判断。
- `ACTUAL_INTERACTION_EVIDENCE_CAPTURED`：控制器接收到独立的实际发送、回复或其他互动证据；它不是草稿或批准记录。
- `INTERACTION_ACCEPTED`：运营已验收互动证据并暂停可能冲突的冷开发动作。
- `OPERATION_DECISION_READY`：运营已完成线程状态、下一动作和商业边界判断。
- `COMMUNICATION_BRIEF_ACCEPTED`：沟通技能已验收运营简报和前序接收凭证。
- `COMMUNICATION_CANDIDATE_READY`：沟通技能已形成候选正文；仍未批准、未发送。
- `CANDIDATE_REVIEW_PENDING`：控制器已接收候选并等待业务员审核。
- `REVISION_REQUEST_CONFIRMED`：业务员已对既有候选提出边界内修订要求。
- `REVISION_BRIEF_ACCEPTED`：沟通技能已验收修订凭证和原候选哈希。

## 不可跳跃的主链

```text
DEVELOPMENT_READY
→ THREAD_ACCEPTED
→ OPERATION_DECISION_READY
→ COMMUNICATION_BRIEF_ACCEPTED
→ COMMUNICATION_CANDIDATE_READY
→ CANDIDATE_REVIEW_PENDING
```

收到回复或疑似回复时使用：

```text
INBOUND_OR_SUSPECTED_REPLY_CAPTURED
→ INTERACTION_ACCEPTED
→ OPERATION_DECISION_READY
→ COMMUNICATION_BRIEF_ACCEPTED
→ COMMUNICATION_CANDIDATE_READY
→ CANDIDATE_REVIEW_PENDING
```

唯一允许不从开发技能开始的入口是可验证的外部实际事件：

```text
ACTUAL_INTERACTION_EVIDENCE_CAPTURED
→ INTERACTION_ACCEPTED
```

这个入口只接收实际互动证据，不把草稿、审核、批准或计划发送变成实际发送。进入运营后仍必须完成后续每一道状态和验收门。

修订链只允许：

```text
CANDIDATE_REVIEW_PENDING
→ REVISION_REQUEST_CONFIRMED
→ REVISION_BRIEF_ACCEPTED
→ COMMUNICATION_CANDIDATE_READY
→ CANDIDATE_REVIEW_PENDING
```

若修订涉及价格、交期、责任、赔偿、产品选择或其他商业范围变化，沟通技能返回 `return_scope_change_to_operations`，不得在正文层自行决定。

## 绑定结构

外部实际事件进入控制器时先冻结：

```text
actual_interaction_capture_v1:
  company_id
  customer_id
  capture_id
  state: ACTUAL_INTERACTION_EVIDENCE_CAPTURED
  interaction_evidence_reference
  interaction_evidence_sha256
  captured_at
```

机器登记中的绑定角色只接受下列顶层合同名，并且每份记录都必须含有匹配的 `company_id` 与 `customer_id`：

```text
customer_selection_receipt -> customer_selection_receipt_v1
inbound_message_evidence -> inbound_message_evidence_v1
actual_interaction_evidence -> actual_interaction_evidence_v1
customer_thread_snapshot -> customer_thread_snapshot_v1
actual_send_evidence -> actual_send_evidence_v1
risk_review_packet -> risk_review_packet
```

每个业务载荷必须内嵌且只内嵌一个：

```text
customer_flow_link_v1:
  contract_version: "1.0"
  transition_id
  company_id
  customer_id
  source_skill
  source_route
  source_state
  target_state
  source_packet_reference
  source_packet_sha256
  source_acceptance_receipt_reference
  source_acceptance_receipt_sha256
  required_bindings:
    - role
      reference
      sha256
  human_decision_receipt_reference
  human_decision_receipt_sha256
  target_skill
  target_route
  allowed_next_actions
```

前序接收凭证使用：

```text
handoff_acceptance_receipt_v1:
  contract_version: "1.0"
  handoff_id
  company_id
  customer_id
  receiver_skill
  receiver_route
  accepted_payload_sha256
  result: PASS
  accepted_at
```

人工决定凭证使用：

```text
human_decision_receipt_v1:
  contract_version: "1.0"
  decision_id
  company_id
  customer_id
  decision_type
  decision_state: CONFIRMED
  recorded_at
```

`source_packet_sha256`、每个 `required_bindings[].sha256`、接收凭证哈希和人工决定凭证哈希都绑定文件原始字节。哈希通过后还必须解析语义：来源包根名、公司、客户和来源状态必须匹配登记；每个绑定文件的顶层合同名、公司和客户必须匹配角色登记；人工决定的 `decision_type` 必须属于当前转换的闭集。

需要前序接收凭证的来源包还必须含有：

```text
accepted_input_handoff_id
accepted_input_payload_reference
accepted_input_payload_sha256
```

`accepted_input_payload_reference` 必须指向同一交接目录内可重算哈希的上一段输入。接收凭证的 `handoff_id` 与 `accepted_payload_sha256` 必须逐项等于来源包中的编号和输入哈希。这样下一段既绑定来源输出字节，也证明来源技能实际验收了生成该输出所依据的上一段输入，不能用同一客户的另一份历史凭证替代。

引用必须位于同一交接目录内，禁止绝对路径、目录逃逸和符号链接。旧包缺少链接时必须从原始事实重新生成新包，不得手工给旧包补字段。

## 生成与验证

发送方只用绑定器生成新的业务包和信封；绑定器拒绝覆盖已有输出：

```bash
python3 scripts/bind_customer_flow_transition.py \
  --transition-id TRANSITION_ID \
  --handoff-id HANDOFF_ID \
  --payload /absolute/unbound-payload.json \
  --source-packet /absolute/source-packet.json \
  --binding role=/absolute/bound-record.json \
  --source-acceptance-receipt /absolute/source-acceptance.json \
  --human-decision-receipt /absolute/human-decision.json \
  --output-payload /absolute/new-bound-payload.json \
  --output-envelope /absolute/new-handoff-envelope.json
```

接收方在读取业务内容前执行只读组合验证：

```bash
python3 scripts/validate_customer_flow_transition.py \
  --envelope /absolute/handoff-envelope.json \
  --expected-company-id COMPANY_ID \
  --expected-target-skill TARGET_SKILL \
  --expected-target-route TARGET_ROUTE \
  --accepted-handoff-registry /absolute/accepted-handoffs.json
```

验证器必须同时通过信封、业务包、登记转换、公司与客户身份、来源包合同及来源状态、目标状态、来源包登记的前序输入编号/哈希与接收凭证、人工决定类型、绑定文件合同及哈希、下一动作闭集和重复交接检查。`validate_handoff_envelope.py` 仅作为兼容入口委托同一组合验证器，不提供仅验信封即可继续的旁路。

验证器不修改接收登记、不写业务包、不写工作簿。只有后续接收动作另获授权且真实完成后，接收方才能创建接收凭证并登记同一个 `handoff_id`。校验 PASS 只证明这一段交接结构与绑定成立，不证明候选正文质量、人工批准、实际发送或客户回复。
