#!/usr/bin/env node

// ---- GLOBAL ENVIRONMENT SHIMS ----
const shimEnv = {
  outerHeight: 1000,
  innerHeight: 100,
  location: {
    protocol: "https:",
    hostname: "vipreader.qidian.com",
  },
};

global.window = global;
globalThis.window = global;
globalThis.self = global;

for (const [key, value] of Object.entries(shimEnv)) {
  globalThis[key] = value;
}

// ---- DECRYPT FUNCTION ----
const Fock = require('./4819793b.qeooxh.js');

async function decrypt(enContent, cuChapterId, fkp, fuid) {
  Fock.initialize();
  Fock.setupUserKey(fuid);
  eval(atob(fkp));
  isFockInit = true;

  return new Promise((resolve, reject) => {
    Fock.unlock(enContent, cuChapterId, (code, decrypted) => {
      if (code === 0) {
        resolve(decrypted);
      } else {
        reject(new Error(`Fock.unlock failed, code=${code}`));
      }
    });
  });
}

// ---- MAIN ----
const fs = require('fs');

(async () => {
  const [inputPath, outputPath] = process.argv.slice(2);
  if (!inputPath || !outputPath) {
    console.error(
      "Usage: node decrypt_qd.js <input.json> <output.txt>"
    );
    process.exit(1);
  }

  try {
    const inputData = fs.readFileSync(inputPath, "utf-8");
    const [
      raw_enContent,
      raw_cuChapterId,
      raw_fkp,
      raw_fuid
    ] = JSON.parse(inputData);

    const decryptPromise = decrypt(
      String(raw_enContent),
      String(raw_cuChapterId),
      String(raw_fkp),
      String(raw_fuid)
    );

    const timeoutMs = 5000;
    const timerPromise = new Promise((_, reject) => {
      setTimeout(() => {
        reject(new Error(`decrypt timeout after ${timeoutMs}ms`));
      }, timeoutMs);
    });

    const result = await Promise.race([
      decryptPromise,
      timerPromise
    ]);

    fs.writeFileSync(outputPath, result, "utf-8");
    process.exit(0);
  } catch (err) {
    console.error("Failed to decrypt:", err);
    process.exit(1);
  }
})();
