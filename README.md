# Quantum Randomness Generator (Flask App)

This project is a single-file Flask web application that simulates quantum randomness using Python's cryptographically strong random number generation. It provides both an API endpoint and an interactive frontend with real-time visualizations.

## Features

- Cryptographically strong random bit generation (using Python `secrets`).
- `/generate` API endpoint for configurable-length random bit sequences.
- Interactive frontend with:
  - Histogram of 0s vs 1s.
  - Real-time Shannon entropy calculation.
  - Animated progress bar during randomness generation.
- Clean, modern design built with HTML, CSS, and JavaScript (Chart.js).
- Fully contained in one Python file, no frontend build steps required.

## Requirements

- Python 3.x
- Flask

Install Flask with:
```bash
pip install flask
```
#Usage

Run the application: python app.py
Open in your browser: http://127.0.0.1:5000/

#License
This project is released under the MIT License.
