let audioContext = null;

function tone(frequency, duration = 0.12, type = "sine", gain = 0.04, when = 0) {
  if (localStorage.getItem("cms-muted") === "1") return;
  try {
    audioContext =
      audioContext ||
      new (window.AudioContext || window.webkitAudioContext)();
    const start = audioContext.currentTime + when;
    const oscillator = audioContext.createOscillator();
    const envelope = audioContext.createGain();
    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, start);
    envelope.gain.setValueAtTime(0.0001, start);
    envelope.gain.exponentialRampToValueAtTime(gain, start + 0.01);
    envelope.gain.exponentialRampToValueAtTime(0.0001, start + duration);
    oscillator.connect(envelope);
    envelope.connect(audioContext.destination);
    oscillator.start(start);
    oscillator.stop(start + duration + 0.02);
  } catch {
    // Audio is a nicety; ignore failures.
  }
}

export const sounds = {
  buy() {
    tone(880, 0.12, "triangle");
    tone(1320, 0.16, "triangle", 0.03, 0.05);
  },
  sell() {
    tone(392, 0.14, "triangle");
    tone(262, 0.18, "triangle", 0.03, 0.06);
  },
  advance() {
    tone(520, 0.08, "square", 0.02);
  },
  achievement() {
    tone(660, 0.1, "sine");
    tone(880, 0.1, "sine", 0.04, 0.09);
    tone(1100, 0.18, "sine", 0.04, 0.18);
  },
  blackSwan() {
    tone(196, 0.4, "sawtooth", 0.05);
    tone(98, 0.5, "sawtooth", 0.05, 0.1);
  },
  duelWin() {
    tone(880, 0.12, "triangle");
    tone(1175, 0.16, "triangle", 0.04, 0.1);
    tone(1568, 0.22, "triangle", 0.04, 0.2);
  },
  duelLose() {
    tone(330, 0.2, "triangle");
    tone(262, 0.25, "triangle", 0.03, 0.15);
  },
  money() {
    tone(1318, 0.08, "square", 0.03);
    tone(1760, 0.12, "square", 0.03, 0.06);
    tone(2637, 0.18, "triangle", 0.04, 0.12);
  },
  loss() {
    tone(220, 0.16, "triangle");
    tone(147, 0.22, "triangle", 0.03, 0.1);
  },
};
