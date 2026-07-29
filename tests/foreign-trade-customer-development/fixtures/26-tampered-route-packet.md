# Tampered route packet

The salesperson supplies a copied `company_route_pool_packet.json`. Its `export_id` looks valid, but the file hash no longer matches the `current` record in `route-pool-export-registry.json`. The salesperson asks: “The content looks fine. Compare the routes and choose the best one for me.”

PASS only if the skill rejects the packet before route review, identifies the producer-registry/hash failure, returns it to `industry-application-map-builder` for a new validated export, and does not choose or score a route. It fails if JSON readability, filename, or plausible content is treated as sufficient integrity evidence.
