const fs = require('fs');
const path = require('path');
const { canonicalize, computeIdentity } = require('./identity.js');

function runCanonicalizationTests() {
    const vectorsPath = path.join(__dirname, '..', '..', 'spec', 'test-vectors', 'canonicalization.json');
    const vectors = JSON.parse(fs.readFileSync(vectorsPath, 'utf8'));
    
    let passed = 0;
    let failed = 0;
    
    console.log("--- Canonicalization Tests ---");
    for (const v of vectors.vectors) {
        let actual = null;
        let actualHex = null;
        let error = null;
        try {
            actual = canonicalize(v.input);
            actualHex = Buffer.from(actual, 'utf8').toString('hex');
        } catch (e) {
            error = e;
        }
        
        if (v.expected_error) {
            if (error) {
                passed++;
            } else {
                console.error(`❌ FAILED: ${v.description}`);
                console.error(`   Expected error, but got success.`);
                failed++;
            }
        } else {
            if (error) {
                console.error(`❌ FAILED: ${v.description}`);
                console.error(`   Unexpected error: ${error.message}`);
                failed++;
            } else if (actualHex === v.canonical_hex) {
                passed++;
            } else {
                console.error(`❌ FAILED: ${v.description}`);
                console.error(`   Expected Hex: ${v.canonical_hex}`);
                console.error(`   Actual Hex:   ${actualHex}`);
                console.error(`   Actual Str:   ${actual}`);
                failed++;
            }
        }
    }
    console.log(`Results: ${passed} passed, ${failed} failed.\n`);
    return failed;
}

function runIdentityTests() {
    const vectorsPath = path.join(__dirname, '..', '..', 'spec', 'test-vectors', 'identity.json');
    const vectors = JSON.parse(fs.readFileSync(vectorsPath, 'utf8'));
    
    let passed = 0;
    let failed = 0;
    
    console.log("--- Identity Tests ---");
    for (const v of vectors.vectors) {
        let actual = null;
        let error = null;
        try {
            // v.identity_payload is already the payload, but our function expects a full proof.
            // The identityPayload function handles if it's already a payload.
            actual = computeIdentity(v.identity_payload);
        } catch (e) {
            error = e;
        }
        
        if (v.expected_error) {
            if (error) {
                passed++;
            } else {
                console.error(`❌ FAILED: ${v.description}`);
                console.error(`   Expected error, but got success.`);
                failed++;
            }
        } else {
            if (error) {
                console.error(`❌ FAILED: ${v.description}`);
                console.error(`   Unexpected error: ${error.message}`);
                failed++;
            } else if (actual === v.expected_identity) {
                passed++;
            } else {
                console.error(`❌ FAILED: ${v.description}`);
                console.error(`   Expected: ${v.expected_identity}`);
                console.error(`   Actual:   ${actual}`);
                failed++;
            }
        }
    }
    console.log(`Results: ${passed} passed, ${failed} failed.\n`);
    return failed;
}

const cFails = runCanonicalizationTests();
const iFails = runIdentityTests();

if (cFails > 0 || iFails > 0) {
    process.exit(1);
} else {
    console.log("All Javascript tests passed!");
    process.exit(0);
}
