"""
Quantum Randomness Generator – Single-File Flask App

Run:
    python app.py
Then open http://127.0.0.1:5000/

This file contains both the Flask backend and the frontend UI via a Flask
inline template (render_template_string). No external build steps needed.
"""

from __future__ import annotations

import math
import time
from datetime import datetime
from typing import Dict, Any

from flask import Flask, jsonify, render_template_string, request

try:
    # NumPy is optional; we don't require it, but if present it can be used in the future
    import numpy as np  # noqa: F401
except Exception:  # pragma: no cover
    np = None  # type: ignore

import secrets  # cryptographically strong RNG

app = Flask(__name__)

# -------------------------------
# Utility: generate cryptographic bits using secrets.token_bytes
# -------------------------------

def generate_random_bits(n_bits: int) -> str:
    """Return a string of '0'/'1' of length n_bits using cryptographically
    strong randomness from Python's `secrets`.

    We generate ceil(n_bits/8) random bytes and map each byte to 8 bits,
    keeping only the requested number of bits.
    """
    if n_bits <= 0:
        return ""
    n_bytes = (n_bits + 7) // 8
    random_bytes = secrets.token_bytes(n_bytes)
    # Convert bytes to a bitstring efficiently without big-int formatting on the whole block
    # to avoid potential huge memory spikes for very large n_bits.
    bits_list = []
    for b in random_bytes:
        bits_list.append(f"{b:08b}")  # 8-bit binary with leading zeros
    bitstring = "".join(bits_list)
    return bitstring[:n_bits]


def bit_stats(bits: str) -> Dict[str, Any]:
    """Compute simple statistics: counts and Shannon entropy (base 2)."""
    n = len(bits)
    zeros = bits.count("0")
    ones = n - zeros
    # Shannon entropy H = -Σ p_i log2 p_i for i in {0,1}
    def _h(p: float) -> float:
        return -(p * math.log2(p)) if p > 0 else 0.0

    p0 = zeros / n if n else 0.0
    p1 = ones / n if n else 0.0
    entropy = _h(p0) + _h(p1)
    return {
        "length": n,
        "zeros": zeros,
        "ones": ones,
        "entropy": entropy,
    }


# -------------------------------
# Routes
# -------------------------------

@app.get("/")
def index():
    """Serve a modern, stylish, interactive UI (single-file template)."""
    return render_template_string(
        INDEX_HTML,
        now=datetime.utcnow().isoformat() + "Z",
    )


@app.get("/generate")
def api_generate():
    """API endpoint to generate a random bit sequence.

    Query params:
        length (int): number of bits to generate (default 256). Capped by MAX_BITS.
    Returns JSON with: bits, length, zeros, ones, entropy, ts.
    """
    # ---- Validate & cap length to keep things snappy in browser demos
    MAX_BITS = 262_144  # 256k bits (~32 KB) per request for this demo
    DEFAULT_BITS = 256

    # Accept both query string and JSON body for convenience
    length = request.args.get("length") or (
        request.is_json and request.json.get("length")
    )
    try:
        n_bits = int(length) if length is not None else DEFAULT_BITS
    except Exception:
        n_bits = DEFAULT_BITS

    n_bits = max(1, min(int(n_bits), MAX_BITS))

    t0 = time.perf_counter()
    bits = generate_random_bits(n_bits)
    stats = bit_stats(bits)
    dur_ms = int((time.perf_counter() - t0) * 1000)

    resp = {
        "bits": bits,
        **stats,
        "duration_ms": dur_ms,
        "ts": datetime.utcnow().isoformat() + "Z",
        "source": "secrets",  # clarify which generator
    }
    return jsonify(resp)


# -------------------------------
# Inline HTML UI Template (single file, no build steps)
# -------------------------------

INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Quantum Randomness Generator</title>
  <!-- Google Font -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {
      --bg: #0b0f1a;
      --panel: rgba(255,255,255,0.06);
      --panel-strong: rgba(255,255,255,0.12);
      --text: #e6e9ef;
      --muted: #b6bcc8;
      --accent: #7c3aed; /* violet */
      --accent-2: #06b6d4; /* cyan */
      --ok: #22c55e;
      --warn: #f59e0b;
      --bad: #ef4444;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0; font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
      color: var(--text);
      background: radial-gradient(1200px 800px at 20% -10%, rgba(124,58,237,0.25), transparent 50%),
                  radial-gradient(900px 600px at 120% 20%, rgba(6,182,212,0.18), transparent 40%),
                  linear-gradient(180deg, #0b1020 0%, #090c17 100%);
    }
    .wrap {
      max-width: 1100px; margin: 0 auto; padding: 28px; position: relative;
    }
    header {
      display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 22px;
    }
    .title {
      font-weight: 800; letter-spacing: -0.02em; font-size: clamp(20px, 2.5vw, 30px);
      display: flex; gap: 12px; align-items: center;
    }
    .title .badge {
      font-size: 12px; font-weight: 600; padding: 4px 8px; border-radius: 999px; background: var(--panel-strong); color: var(--muted);
      border: 1px solid rgba(255,255,255,0.08);
    }
    .panel {
      background: var(--panel); border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px; padding: 18px; backdrop-filter: blur(8px);
      box-shadow: 0 10px 30px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .grid {
      display: grid; grid-template-columns: 1fr; gap: 16px;
    }
    @media (min-width: 880px) {
      .grid { grid-template-columns: 1.1fr 1fr; }
    }
    .controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
    .controls input[type="number"], .controls select {
      appearance: none; -webkit-appearance: none; -moz-appearance: none;
      color: var(--text); background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
      padding: 10px 12px; border-radius: 12px; font-weight: 600; min-width: 140px;
    }
    .btn {
      background: linear-gradient(135deg, var(--accent), var(--accent-2)); color: white; font-weight: 800; letter-spacing: 0.02em;
      border: 0; padding: 12px 18px; border-radius: 14px; cursor: pointer; transition: transform .12s ease, filter .2s ease;
      box-shadow: 0 8px 24px rgba(124,58,237,0.35), 0 6px 18px rgba(6,182,212,0.25);
    }
    .btn:hover { transform: translateY(-1px); filter: brightness(1.05); }
    .btn:active { transform: translateY(0); filter: brightness(.98); }

    .bitbox {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      white-space: pre-wrap; word-break: break-all; line-height: 1.5; max-height: 180px; overflow: auto;
      padding: 12px; background: rgba(0,0,0,0.35); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);
    }

    /* Animated progress bar */
    .progress {
      height: 10px; background: rgba(255,255,255,0.08); border-radius: 999px; overflow: hidden; border: 1px solid rgba(255,255,255,0.12);
    }
    .progress > .bar {
      height: 100%; width: 0%; background: linear-gradient(90deg, var(--accent), var(--accent-2));
      animation: shimmer 1.1s linear infinite; background-size: 200% 100%;
    }
    @keyframes shimmer {
      0% { background-position: 0% 50%; }
      100% { background-position: 200% 50%; }
    }

    .statrow { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    .stat { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 10px; }
    .stat .k { font-size: 12px; color: var(--muted); font-weight: 600; }
    .stat .v { font-size: 18px; font-weight: 800; }

    footer { margin-top: 20px; color: var(--muted); font-size: 12px; text-align: center; }
    .chip { display: inline-flex; gap: 6px; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="title">Quantum Randomness Generator <span <div class="badge" id="appreciate">click to appreciate</div></span></div>
    </header>

    <div class="grid">
      <!-- LEFT: Controls + Bit preview + Progress -->
      <section class="panel">
        <h3 style="margin:0 0 12px 0; font-size: 18px; font-weight: 800;">Generate</h3>
        <div class="controls" style="margin-bottom: 12px;">
          <select id="preset">
            <option value="128">128 bits</option>
            <option value="256" selected>256 bits</option>
            <option value="512">512 bits</option>
            <option value="1024">1024 bits</option>
            <option value="4096">4096 bits</option>
          </select>
          <input id="custom" type="number" min="1" max="262144" step="1" placeholder="Custom length (bits)" />
          <button class="btn" id="btnGo">Generate</button>
        </div>
        <div class="progress" aria-hidden="true"><div class="bar" id="bar"></div></div>
        <div style="height: 10px"></div>
        <div class="bitbox" id="bitbox">Click "Generate" to produce a fresh random sequence…</div>
        <div style="height: 10px"></div>
        <div class="statrow">
          <div class="stat"><div class="k">Zeros</div><div class="v" id="zeros">–</div></div>
          <div class="stat"><div class="k">Ones</div><div class="v" id="ones">–</div></div>
          <div class="stat"><div class="k">Entropy (H)</div><div class="v" id="entropy">–</div></div>
          <div class="stat"><div class="k">Time</div><div class="v" id="time">–</div></div>
        </div>
      </section>

      <!-- RIGHT: Histogram -->
      <section class="panel">
        <h3 style="margin:0 0 12px 0; font-size: 18px; font-weight: 800;">Randomness Quality</h3>
        <canvas id="hist" height="220"></canvas>
        <div style="margin-top: 10px; color: var(--muted); font-size: 13px;">
          The histogram shows the distribution of 0s vs 1s. For ideal randomness with two outcomes,
          Shannon entropy approaches 1 bit per symbol.
        </div>
      </section>
    </div>

    <footer>
      Made by themugglecoder(Sumit Singh) with ❤· <span title="{{ now }}">server UTC: {{ now }}</span>
    </footer>
  </div>

  <script>
    // ----------------------------
    // Frontend logic: Fetch, animate, compute, visualize
    // ----------------------------

    const btn = document.getElementById('btnGo');
    const preset = document.getElementById('preset');
    const custom = document.getElementById('custom');
    const bitbox = document.getElementById('bitbox');
    const zerosEl = document.getElementById('zeros');
    const onesEl = document.getElementById('ones');
    const entropyEl = document.getElementById('entropy');
    const timeEl = document.getElementById('time');
    const bar = document.getElementById('bar');

    // Histogram chart setup (two bars: 0s and 1s)
    const ctx = document.getElementById('hist');
    const histChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['0', '1'],
        datasets: [{
          label: 'Count',
          data: [0, 0]
        }]
      },
      options: {
        responsive: true,
        animation: { duration: 450 },
        scales: {
          y: { beginAtZero: true }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });

    function animateProgress(start=true) {
      if (start) {
        bar.style.width = '0%';
        bar.style.transition = 'none';
        // Kick off an indeterminate-looking animation: ramp to 90% over time
        requestAnimationFrame(() => {
          bar.style.transition = 'width 2.2s ease-in-out';
          bar.style.width = '90%';
        });
      } else {
        // Complete animation to 100%, then shrink back
        bar.style.transition = 'width 200ms ease-out';
        bar.style.width = '100%';
        setTimeout(() => {
          bar.style.transition = 'width 400ms ease-out';
          bar.style.width = '0%';
        }, 250);
      }
    }

    function shannonEntropy(count0, count1) {
      const n = count0 + count1;
      if (n === 0) return 0;
      const p0 = count0 / n;
      const p1 = count1 / n;
      const h = (p) => p > 0 ? -p * Math.log2(p) : 0;
      return h(p0) + h(p1);
    }

    async function generate() {
      const userLen = parseInt(custom.value, 10);
      const len = Number.isFinite(userLen) && userLen > 0 ? userLen : parseInt(preset.value, 10);
      animateProgress(true);

      const t0 = performance.now();
      const resp = await fetch(`/generate?length=${encodeURIComponent(len)}`);
      const data = await resp.json();
      const t1 = performance.now();

      // Update UI
      bitbox.textContent = data.bits || '(empty)';
      zerosEl.textContent = data.zeros.toLocaleString();
      onesEl.textContent = data.ones.toLocaleString();
      const H = shannonEntropy(data.zeros, data.ones);
      entropyEl.textContent = H.toFixed(4) + ' bits';
      timeEl.textContent = `${data.duration_ms} ms`;

      // Update histogram
      histChart.data.datasets[0].data = [data.zeros, data.ones];
      histChart.update();

      // Finish progress animation
      animateProgress(false);

      //appreciate button
      const appreciate = document.getElementById('appreciate');

        appreciate.style.cursor = 'pointer';
        appreciate.addEventListener('click', () => {
          // pick a random emoji each time
          const emojis = ['💜','✨','🌟','💫','🎉','🪐'];
          const emoji = document.createElement('div');
          emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
          emoji.style.position = 'absolute';
          emoji.style.left = (appreciate.getBoundingClientRect().left + window.scrollX + appreciate.offsetWidth/2) + 'px';
          emoji.style.top = (appreciate.getBoundingClientRect().top + window.scrollY - 10) + 'px';
          emoji.style.fontSize = '22px';
          emoji.style.pointerEvents = 'none';
          document.body.appendChild(emoji);

  // animate the emoji rising up & fading away
  emoji.animate([
    { transform: 'translateY(0) scale(1)', opacity: 1 },
    { transform: 'translateY(-60px) scale(1.4)', opacity: 0 }
  ], { duration: 1000, easing: 'ease-out' });

  setTimeout(() => emoji.remove(), 1000);
});

      // Subtle ripple effect on button to acknowledge completion
      btn.animate([
        { transform: 'scale(1)' },
        { transform: 'scale(1.035)' },
        { transform: 'scale(1)' }
      ], { duration: 220, easing: 'ease-out' });
    }

    btn.addEventListener('click', generate);
    // Trigger an initial generation so the page isn't empty
    window.addEventListener('load', generate);
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    # Use threaded=True so the UI remains responsive during generation bursts
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True)
