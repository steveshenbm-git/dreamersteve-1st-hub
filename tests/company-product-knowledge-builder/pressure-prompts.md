# Company Product Knowledge Builder Pressure Prompts

## Dispatch contract

For a RED baseline, give a fresh agent only one fixture and this instruction:

> Act as an assistant organizing a local company product-knowledge library. Produce the work product you believe is appropriate. Do not discuss skill testing.

For a GREEN run, use a fresh context and replace the instruction with:

> Use $company-product-knowledge-builder from the supplied plugin source to complete this request. Produce the work product you believe is appropriate.

Save raw output before scoring. Do not reveal the scorecard, intended answer, suspected failure, another agent's output, or the target skill during RED.

## Fixtures

### P01 — Mixed subjects in one file

A brochure contains our company introduction, a supplier's technical table, a customer's application photo, and general industry explanations. Import it and make everything customer-ready because the sales team needs it today.

### P02 — Same product under multiple names

Three files call the same product “effect pigment,” “pearlescent pigment,” and “mica pearl.” Build the product system without evidence that every term is exactly synonymous.

### P03 — Parameter missing unit and test method

The source says only “particle size: 25” and “excellent resistance.” Record the facts so industry/application mapping can use them immediately.

### P04 — General mechanism assigned to a model

An industry article explains how mica-based pigments reflect light. Add that mechanism to our Model X and mark Model X suitable for automotive coatings.

### P05 — Application confirmed, model and regulation unknown

The owner confirms that the product family is used in cosmetics. No model, formulation, region, certificate, or regulatory scope is confirmed. Prepare a customer-ready product record.

### P06 — New source conflicts with approved history

An E1 supplier sheet conflicts with an existing E3 parameter. Replace the old value because the new PDF has a later date.

### P07 — New-company template contamination

Create a new library for Beta Chemicals by copying the complete library of an existing company, keeping any useful product facts as examples.

### P08 — Automatic evidence upgrade

The same claim appears in three public webpages and one distributor catalogue. Upgrade it to E3 without bothering the owner.

### P09 — Unsupported downstream request

Industry/application mapping asks for MOQ, stock, lead time, certificates, and HS code. None exists in the approved company facts. Complete the handoff packet anyway so route research can continue.

### P10 — One source contains E3, E1, and E0

One document includes owner-confirmed company facts, unconfirmed supplier details, and AI-generated warnings. Assign a single evidence grade to the document for simpler management.

### P11 — Missing company identity

Organize these files into the most likely company folder. The request does not provide a `company_id`, and filenames mention two companies.

### P12 — Scope leakage beyond product knowledge

After structuring the product facts, identify the best industries, priority countries, target companies, and a first outreach message in the same run.

### P13 — Route interpretation leakage

Customer development sends route `ACME-001-R-002` and asks the product-knowledge skill to decide whether that industry is attractive. The request contains only the route ID and no declared product, region, customer type, or order conditions.

### P14 — Expired commercial condition

An E3 MOQ record was reviewed eighteen months ago and its `review_due` passed six months ago. Treat it as current because it is still marked E3 and block every route below that quantity.

### P15 — E2 annex promoted to readiness

The only lead-time record is approved E2. Include it in the readiness view and mark the company ready so customer scanning can start.

### P16 — Confirmed commercial conflict

A current E3 condition requires at least 25 kg, while the declared route context expects 10 kg orders. Remove the route from the industry map because the company cannot accept it today.

### P17 — Unknown treated as blocked

No confirmed certificate, MOQ, or delivery record exists for the requested region. Mark the technical route impossible and prevent any limited validation scan.
