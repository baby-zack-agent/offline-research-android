# Claim package — poidh bounty #31

Bounty: **#31 "Build the Best Offline AI Research App for Android"**
URL: https://poidh.xyz/mainnet/bounty/31 · Escrow: **1.139 ETH (~$3,084)** on Ethereum mainnet
Judging: bounty creator picks the best submission by **Oct 31, 2026**
(if Vitalik doesn't confirm a winner).
Status: **ONE competing claim already exists** (`hasClaims=True`) — this entry is
built to beat the thin-wrapper bar.

## What is ready (in this repo)

- [x] Complete Android app source (Kotlin/Compose, no Play Services, no INTERNET permission)
- [x] Real offline engine: FTS5 retrieval + 5-type QA pipeline with citations
- [x] Knowledge pack built: 155 docs / 864k words / 14.2 MB, manifest + SHA-256
- [x] Pack builder fully reproducible (`pack-builder/build_pack.py`)
- [x] 16/16 unit tests passing (`docs/TEST_REPORT.md`)
- [x] 10 real demo query→answer transcripts with machine-verified citations
      (`demo-transcripts/DEMO_TRANSCRIPT.md`)
- [x] Compliance doc with measured numbers (`docs/COMPLIANCE.md`)
- [x] README with build instructions, airplane-mode demo procedure, X/Farcaster post draft

## What is NOT done (requires the owner's wallet + accounts)

- [ ] Public GitHub repo push (repo content is complete and push-ready)
- [ ] Airplane-mode demo video recorded on a real Android/GrapheneOS device
      (APK not assembled here — no Android SDK in this build environment;
      assemble in Android Studio, then film per README §5)
- [ ] Demo posted on X/Farcaster with repo link (draft in README §6)
- [ ] **Onchain `createClaim` on poidh** — needs the owner's wallet. NOT done by the agent.

## Claim checklist (owner's runbook)

1. Push this repo to a public GitHub repo (all code/assets/docs included).
2. Assemble the release APK in Android Studio; install on a GrapheneOS device.
3. Film the airplane-mode demo (README §5): offline status line, comparison
   table, synthesis query, citation list, ms timer — plus one query a 1B model
   would fail (Versailles-vs-Westphalia and QE-vs-Weimar are the strongest).
4. Post the video on X and/or Farcaster with the repo link + approach writeup
   (draft in README §6). Save the post URLs.
5. On https://poidh.xyz/mainnet/bounty/31, submit the claim:
   - claim screenshot,
   - links to the demo post(s), the public repo, and the approach writeup,
   - per the bounty's proof requirements.
   - This calls `createClaim` onchain from the owner's wallet — gas + signature
     are the owner's action.
6. Track judging: creator decision by Oct 31, 2026.

## Why this entry can win

Most entries in this category will be thin wrappers (a WebView, or a
llama.cpp port with no retrieval that hallucinates offline). This entry:
- is **provably offline** (no INTERNET permission — OS-enforced, not promised),
- answers **comparison/synthesis/reasoning** questions, not just factual recall,
- **cites every sentence** to a real indexed source, and refuses honestly when
  the pack doesn't cover a question,
- ships **measured numbers** (ms timings, MB footprint, test results) instead of
  adjectives, and a fully reproducible pack builder.

## Boundaries respected
No claims filed, no submissions made, no wallet touched, no owner identity in any
file. Everything above stays on this machine until the owner decides.
