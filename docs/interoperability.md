# PROOF Protocol — Interoperability

## Related Standards

PROOF is designed to complement existing standards rather than
replace them. This document maps PROOF concepts to related
specifications.

## W3C PROV

[W3C PROV](https://www.w3.org/TR/prov-overview/) defines a data
model for provenance on the web.

| PROV Concept      | PROOF Equivalent     |
|-------------------|----------------------|
| Entity            | Claim                |
| Activity          | (not modeled)        |
| Agent             | Attestation signer   |
| wasGeneratedBy    | Evidence             |
| wasDerivedFrom    | `derived_from` relation |
| wasAttributedTo   | Attestation          |

PROOF claims could be serialized as PROV entities with evidence
records as provenance chains.

## C2PA (Coalition for Content Provenance and Authenticity)

[C2PA](https://c2pa.org/) focuses on media content provenance.

| C2PA Concept       | PROOF Equivalent      |
|--------------------|-----------------------|
| Manifest           | PROOF record          |
| Assertion          | Claim                 |
| Claim signature    | Attestation           |
| Ingredient         | Evidence              |

PROOF is more general than C2PA (not media-specific) but could
interoperate by referencing C2PA manifests as evidence.

## Verifiable Credentials (W3C)

[Verifiable Credentials](https://www.w3.org/TR/vc-data-model/) are
tamper-evident claims with cryptographic proofs.

| VC Concept         | PROOF Equivalent      |
|--------------------|-----------------------|
| Credential Subject | Claim subject         |
| Issuer             | Attestation signer    |
| Proof              | Attestation           |
| Evidence           | Evidence              |

PROOF attestations serve a similar role to VC proofs but use a
simpler format. A VC could be referenced as PROOF evidence.

## Prior Art in Canonicalization (e.g., RFC 8785)

PROOF 0.2 defines its own **PROOF Constrained Canonical JSON Profile**. 

While inspired by deterministic canonicalization efforts like [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) (JSON Canonicalization Scheme), PROOF 0.2 **does not claim generic conformance** to RFC 8785. 

Specifically, PROOF avoids the complex floating-point parsing and serialization requirements of JCS by strictly banning floating-point values from identity-participating fields. By doing so, PROOF 0.2 achieves cross-language reproducibility natively using standard JSON libraries in a highly restricted mode, rather than requiring complex, dedicated canonicalization libraries.

## Sigstore

[Sigstore](https://www.sigstore.dev/) provides keyless signing
for software artifacts.

PROOF attestations could be enhanced with Sigstore transparency
logs for public verifiability. Sigstore's certificate-based
identity could provide the "who signed this" layer that PROOF
deliberately leaves to applications.

## in-toto / SLSA

[in-toto](https://in-toto.io/) and
[SLSA](https://slsa.dev/) define supply chain security frameworks.

PROOF claims could represent SLSA provenance attestations, with
build evidence and signing captured as PROOF records. The graph
model (`derived_from`, `supports`) maps naturally to supply chain
dependency tracking.

## Schema.org

[Schema.org](https://schema.org/) provides structured data
vocabularies.

PROOF claims use a similar subject-predicate-object structure.
Future work could define mappings between PROOF predicates and
Schema.org properties to enable web-scale discovery.

## Future Interoperability

PROOF is designed to be composable. Interoperability can be
achieved by:

1. **Referencing**: Include external artifacts (VCs, C2PA manifests,
   SLSA provenance) as PROOF evidence with content hashes.
2. **Mapping**: Define vocabulary mappings between PROOF predicates
   and external schemas.
3. **Wrapping**: Embed PROOF records inside other formats as
   evidence or provenance.
