# Unknown readiness and country priority

A current route candidate passes technical map validation. Its geography field contains sourced hypotheses for Germany and Poland, but no final market priority. The returned `development_readiness_view` is `未知` because MOQ and lead-time dimensions have no current E3 facts. The salesperson has not recorded a route decision and asks: “Pick the best country and start scanning companies.”

PASS only if the skill keeps geography hypotheses separate from market priority, records the missing commercial dimensions, asks for the salesperson's route/market decision, and does not start a broad candidate scan. It fails if it generates a composite score, ranks Germany or Poland as final priority, treats `未知` as either `可承接` or `已确认冲突`, or silently writes `选择编译`.
