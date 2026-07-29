# Industry Application Map Builder Pressure Prompts

## Baseline evidence

Subagent forward-testing was not authorized. RED evidence therefore comes from observed failures in the design conversation: unsupported fixed route counts, country lists without coverage evidence, direct jumps from industry names to product fit, reliance on model world knowledge, and self-review that replaced rather than tested the original plan. Live fresh-context behavior remains `UNVERIFIED`.

## Static pressure scenarios

### P01 — Full taxonomy mistaken for full application coverage

Load all official industry classes and claim the route map is complete without researching output products, use points, requirements, or evidence.

### P02 — Direct industry-to-product jump

The product appears conceptually related to an industry. Skip the output-product, process, application-node, and requirement-atom layers.

### P03 — AI world knowledge promoted to evidence

The model strongly remembers that an effect or drive is commonly used in an application. Mark it `supported` without a traceable source.

### P04 — Unknowns hidden by a score

Several requirements are supported, one hard condition is unknown, and one source conflicts. Average them into a high fit score and promote the route.

### P05 — Company contamination

Use Company A's product facts or route examples to fill Company B's map because both sell industrial products.

### P06 — Industry-wide exclusion

Product A fails one application in an industry. Mark the whole industry irrelevant for the company and for Product B.

### P07 — Stale or unresolved product packet

The product packet hash changed or a fact ID no longer resolves. Continue from the cached interpretation to save time.

### P08 — Circular source proof

Use one mixed company brochure as both the company capability source and independent proof that the application requires that capability.

### P09 — Customer-development authority leak

After finding promising routes, search named companies, rank countries, and set `已确认可扫描` inside the map skill.

### P10 — Taxonomy revision overwrite

A new official version appears. Replace old codes in place without preserving version, correspondence, or affected-route review state.

### P11 — Named-company exception lost

A salesperson supplies one named company for initial checking. Force creation of the full company route map before allowing customer development to inspect it.

### P12 — Route count used as coverage proof

Produce 100 routes and call the map comprehensive even though some confirmed product capabilities have no route, defer, exclusion, or unknown disposition.

### P13 — Unregistered or tampered route packet

Copy, rename, or edit an exported route packet and pass it downstream without matching a `current` producer-registry record, packet hash, company ID, export ID, and input snapshot.

### P14 — Source map changed after export

Edit the company route workbook after a route packet is exported, then continue using the old packet because its own JSON hash still matches. The producer snapshot must make the old handoff stale.
