
Realtime FIR filter implementation in Python
=======================================

This project is a small toolkit for designing FIR filters, running them in a realtime mode (sample by sample) and analysing the result. The FIR filter is implemented in a python class that can be used in any of your python projects.

Project layout
======

````
firdesigner/
    filter.py        FIRFilter (direct form) and LinearPhaseFIR (folded, types I-IV):
                     sample-by-sample (realtime) filtering
    designer.py      coefficient design: window method, Kaiser from a spec,
                     equiripple (remez), least squares (firls), minimum phase, save/load
    linear_phase.py  linear-phase types I-IV, their forced zeros and design rules
    analysis.py      numbers only: frequency response, group delay, impulse response,
                     ripple, attenuation, -3 dB points, spectrum of a signal
    plotting.py      matplotlib plots of all of the above
    cli.py           the fir-design command
examples/            scripts showing typical workflows
data/                example input signals
output/              coefficients written by the examples (not tracked)
````

Install
======

The project uses [Poetry](https://python-poetry.org/) and needs Python 3.12 or newer. From the repository root:
````
poetry install --extras plot
````
The `plot` extra installs matplotlib, which `firdesigner.plotting`, the examples and `fir-design --plot` need. Without it (`poetry install`) the filter, designer and analysis modules still work.

Run an example inside the Poetry environment:
````
poetry run python examples/filter_generated_sines.py
````

Design coefficients from the command line
======

`fir-design` writes the coefficients one per line to stdout, or to a file with `-o`. All frequencies are in Hz.
````
poetry run fir-design window lowpass --taps 101 --cutoff 40 --fs 2000
poetry run fir-design window bandpass --taps 1001 --cutoff 1 40 --fs 2000 --window blackman -o bandpass.dat
poetry run fir-design kaiser highpass --cutoff 500 --fs 2000 --attenuation 60 --width 50
poetry run fir-design equiripple --taps 101 --bands 0 40 60 1000 --desired 1 0 --weight 1 10 --fs 2000
poetry run fir-design least-squares --taps 101 --bands 0 40 60 1000 --desired 1 0 --fs 2000
````

| Method | Use it when |
|---|---|
| `window` | you know the number of taps; pick a window with `--window` or a Kaiser transition width with `--width` |
| `kaiser` | you know the spec (attenuation and transition width) and want the number of taps computed |
| `equiripple` | you want the fewest taps for a spec (Parks-McClellan); `--kind hilbert` / `differentiator` gives antisymmetric filters |
| `least-squares` | you want the least total error over the bands (odd number of taps only) |

Options for every method:
- `--summary` prints taps, linear-phase type, delay, -3 dB points, and ripple and attenuation per band (equiripple and least-squares) to stderr
- `--plot` shows the magnitude response
- `--min-phase homomorphic|hilbert` converts the result to minimum phase

Run `poetry run fir-design <method> --help` for all options. Impossible requests fail with an explanation, for example a highpass with an even number of taps (type II filters always have a zero at Nyquist).

Calculate the coefficients in Python
==========================

Cutoff frequencies are given in Hz together with the sample rate:
````
    from firdesigner import designer
    b = designer.bandpass(NTAPS, f1, f2, fs)                       # window method
    b = designer.kaiser(40, fs, 'lowpass', attenuation_db=60, width=20)
    b = designer.equiripple(101, [0, 40, 60, fs / 2], [1, 0], fs)
    b = designer.least_squares(101, [0, 40, 60, fs / 2], [1, 0], fs)
````
In the design process, implementation requirements must be taken in accordance to which behaviour is required on your application. Here is where your expertise and knowledge about DSP come into play. I can provide some recommended literature to understand the world of digital signal processing:
1. http://www.dspguide.com/
2. Discrete-Time Signal Processing by A. V. Oppenheim and R. W. Schafer.
3. Theory and Application of Digital Signal Processing by Rabiner and Gold. 

Instantiate the filter
==================

You can create an instance of the FIR filter by calling it:
````
    from firdesigner import FIRFilter, LinearPhaseFIR
    myFIR = FIRFilter(b)            # direct form, N multiplications per sample
    myFIR = LinearPhaseFIR(b)       # folded, about N/2 multiplications; b must be linear phase
    myFIR.type                      # 1 to 4
````
The old name `FIR_filter(b, NTAPS)` still works.

| Type | Coefficients | Length | Always zero at | Cannot be |
|---|---|---|---|---|
| I | symmetric | odd | (nothing) | (anything allowed) |
| II | symmetric | even | Nyquist | highpass, bandstop |
| III | antisymmetric | odd | DC and Nyquist | lowpass, highpass, bandstop |
| IV | antisymmetric | even | DC | lowpass, bandstop |

Filtering Flow
====

For filtering sample by sample:
````
    y = np.zeros(SAMPLES)
    for i in range(SAMPLES):
       y[i] = myFIR.dofilter(mysignal[i])
````
or, for a whole signal at once, `y = myFIR.filter(mysignal)`. Call `myFIR.reset()` before reusing the filter on another signal.

Analyse
====

````
    from firdesigner import analysis, plotting
    analysis.summary(b, fs, passbands=[(0, 40)], stopbands=[(60, fs / 2)])
    plotting.plot_frequency_response(b, fs)
    plotting.plot_before_after(mysignal, y, fs)
````

Examples
====

| Script | Shows |
|---|---|
| `filter_generated_sines.py` | band-pass a generated 1 + 50 + 350 Hz signal |
| `filter_sine_dat.py` | band-pass the signal in `data/sine.dat` |
| `filter_recorded_signal.py` | band-pass 100 s of the recorded `data/unfiltered.dat` |
| `compare_windows.py` | the same band-pass with four windows |
| `design_from_spec.py` | one low-pass spec designed with Kaiser, equiripple and least squares |
| `linear_phase_types.py` | types I-IV, their forced zeros, folded vs direct form |
| `linear_vs_minimum_phase.py` | delay of a linear-phase filter vs its minimum-phase versions |

`filter_generated_sines.py` filters a combination of 1, 50 and 350 Hz sine waves, and you obtain something like this:

![signa](https://user-images.githubusercontent.com/16301652/103227026-b4c38300-492d-11eb-99ea-334d0a0a11da.png)

The frequency spectrum of the filtered signal is the following

![fft](https://user-images.githubusercontent.com/16301652/103227030-b55c1980-492d-11eb-8a21-e12f11ff619f.png)
