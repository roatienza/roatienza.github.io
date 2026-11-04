// Expanded field taxonomy for the common-words evaluation.
//
// The 2026-11-02 and 2026-11-03 runs cover FIVE tested fields (821 words,
// 2,463 cases). The taxonomy below is the wider set of application fields a
// TTS is bought for. Only the five tested fields have numbers behind them;
// the rest are listed as NOT YET COVERED so the page cannot imply coverage
// the data does not have.
//
// Every number here is derived from the two run files:
//   full_w1243.jsonl   (old model, 2026-11-02)
//   full2_w1243.jsonl  (new model, 2026-11-03)
// case = one render; word = all three seeds exact.

var FIELDS2 = {
  tested: [
    { field: "medical",   words: 171, cases: 513,
      oldCase: 73,  newCase: 458, oldWord: 18,  newWord: 147,
      note: "long clinical jargon: sphygmomanometer, anaesthesia, amoxicillin" },
    { field: "legal",     words: 186, cases: 558,
      oldCase: 233, newCase: 471, oldWord: 63,  newWord: 148,
      note: "justiciability, tortfeasor, venue, estoppel" },
    { field: "computing", words: 182, cases: 546,
      oldCase: 283, newCase: 483, oldWord: 82,  newWord: 157,
      note: "repository, iteration, idempotent, Kubernetes" },
    { field: "science",   words: 167, cases: 501,
      oldCase: 205, newCase: 459, oldWord: 59,  newWord: 147,
      note: "thermodynamics, spectroscopy, phylogeny" },
    { field: "finance",   words: 115, cases: 345,
      oldCase: 152, newCase: 308, oldWord: 41,  newWord: 102,
      note: "amortization, equity, collateral, tranche" }
  ],

  // The wider taxonomy. `maps` names the tested field whose words are the
  // closest proxy, or null when the evaluation holds no words for it.
  untested: [
    { field: "accessibility & assistive technology", maps: null,
      why: "screen readers, AAC, dyslexia read-along, audio description" },
    { field: "media, publishing & entertainment", maps: null,
      why: "audiobooks, podcasts, dubbing, voice-over, gaming NPCs" },
    { field: "conversational AI & voice agents", maps: null,
      why: "IVR, contact centres, full-duplex agents, voice cloning" },
    { field: "education & training", maps: null,
      why: "e-learning narration, language learning, exam accommodation" },
    { field: "healthcare & life sciences", maps: "medical",
      why: "patient education, medication reminders, telehealth triage" },
    { field: "automotive & transport", maps: null,
      why: "in-car assistants, platform announcements, fleet dispatch" },
    { field: "finance, banking & insurance", maps: "finance",
      why: "voice banking, fraud alerts, statements, claims IVR" },
    { field: "government & public sector", maps: null,
      why: "emergency alerts, public information lines, digital inclusion" },
    { field: "retail, commerce & hospitality", maps: null,
      why: "voice commerce, kiosk prompts, menus, concierge" },
    { field: "industrial, IoT & embedded", maps: null,
      why: "machine status, safety warnings, smart home, wearables, edge" },
    { field: "legal, compliance & enterprise", maps: "legal",
      why: "document review by ear, depositions, regulatory disclosure" },
    { field: "science & research", maps: "science",
      why: "lab protocol read-back, field checklists, paper audio" },
    { field: "productivity & personal tools", maps: null,
      why: "notification readout, dictation playback, daily briefings" },
    { field: "content creation & developer tooling", maps: "computing",
      why: "TTS APIs and SDKs, voice design, eval harnesses, synthetic data" }
  ]
};
