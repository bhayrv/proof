const crypto = require('crypto');

function compareKeys(a, b) {
    const arrA = Array.from(a).map(c => c.codePointAt(0));
    const arrB = Array.from(b).map(c => c.codePointAt(0));
    for (let i = 0; i < Math.min(arrA.length, arrB.length); i++) {
        if (arrA[i] !== arrB[i]) return arrA[i] - arrB[i];
    }
    return arrA.length - arrB.length;
}

function canonicalize(data) {
    if (data === null) return "null";
    if (typeof data === "boolean") return data ? "true" : "false";
    
    if (typeof data === "number") {
        if (!Number.isFinite(data) || !Number.isInteger(data)) {
            throw new Error("Floating point values are forbidden");
        }
        return data.toString();
    }
    
    if (typeof data === "string") {
        // We rely on standard JSON stringify for escaping. 
        // We might need to ensure hex escapes are lowercase if any.
        // Node's JSON.stringify uses lowercase for \u00xx.
        return JSON.stringify(data);
    }
    
    if (Array.isArray(data)) {
        const items = data.map(item => canonicalize(item));
        return "[" + items.join(",") + "]";
    }
    
    if (typeof data === "object") {
        const keys = Object.keys(data).sort(compareKeys);
        const parts = [];
        for (const k of keys) {
            parts.push(JSON.stringify(k) + ":" + canonicalize(data[k]));
        }
        return "{" + parts.join(",") + "}";
    }
    
    throw new Error("Unsupported type");
}

function identityPayload(proof) {
    if (proof.proof === "0.2" && "claim" in proof && "evidence" in proof && Object.keys(proof).length === 3) {
        return proof;
    }
    const payload = {
        proof: "0.2",
        claim: proof.claim,
        evidence: proof.evidence || []
    };
    return payload;
}

function computeIdentity(proof) {
    const payload = identityPayload(proof);
    const canonicalBytes = canonicalize(payload);
    const hash = crypto.createHash('sha256').update(canonicalBytes, 'utf8').digest('hex');
    return "sha256:" + hash;
}

module.exports = {
    canonicalize,
    identityPayload,
    computeIdentity
};
