"""
Command line interface for designing FIR coefficients: `fir-design`.

    fir-design window lowpass --taps 101 --cutoff 40 --fs 2000
    fir-design window bandpass --taps 1001 --cutoff 1 40 --fs 2000 --window blackman -o bp.dat
    fir-design kaiser highpass --cutoff 500 --fs 2000 --attenuation 60 --width 50
    fir-design equiripple --taps 101 --bands 0 40 60 1000 --desired 1 0 --weight 1 10 --fs 2000
    fir-design least-squares --taps 101 --bands 0 40 60 1000 --desired 1 0 --fs 2000

Coefficients go to stdout (one per line) or to --output. --summary prints
the design figures to stderr and --plot shows the response (needs matplotlib).
"""
import argparse
import sys

import numpy as np

from . import analysis, designer

BTYPES = ['lowpass', 'highpass', 'bandpass', 'bandstop']


def _cutoff(values):
    return values[0] if len(values) == 1 else values


def _bands_from_gains(bands, desired):
    """Split band edges into passbands (gain > 0) and stopbands (gain 0)."""
    pairs = list(zip(bands[::2], bands[1::2]))
    return ([p for p, g in zip(pairs, desired) if g > 0],
            [p for p, g in zip(pairs, desired) if g == 0])


def build_parser():
    parser = argparse.ArgumentParser(prog='fir-design', description='Design FIR filter coefficients.')
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--fs', type=float, required=True, help='sample rate in Hz')
    common.add_argument('-o', '--output', help='file to write the coefficients to (default: stdout)')
    common.add_argument('--min-phase', choices=['homomorphic', 'hilbert'],
                        help='convert the result to minimum phase')
    common.add_argument('--summary', action='store_true', help='print design figures to stderr')
    common.add_argument('--plot', action='store_true', help='plot the frequency response')
    sub = parser.add_subparsers(dest='method', required=True)

    p = sub.add_parser('window', parents=[common], help='window method with a fixed number of taps')
    p.add_argument('btype', choices=BTYPES)
    p.add_argument('--taps', type=int, required=True)
    p.add_argument('--cutoff', type=float, nargs='+', required=True, help='cutoff(s) in Hz')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--window', help="window name, e.g. hamming (default), blackman")
    g.add_argument('--width', type=float, help='transition width in Hz (Kaiser window)')

    p = sub.add_parser('kaiser', parents=[common], help='window method, taps computed from the spec')
    p.add_argument('btype', choices=BTYPES)
    p.add_argument('--cutoff', type=float, nargs='+', required=True, help='cutoff(s) in Hz')
    p.add_argument('--attenuation', type=float, default=60, help='stopband attenuation in dB (default 60)')
    p.add_argument('--width', type=float, required=True, help='transition width in Hz')

    for name, helptext in [('equiripple', 'Parks-McClellan (remez)'), ('least-squares', 'least squares (firls)')]:
        p = sub.add_parser(name, parents=[common], help=helptext)
        p.add_argument('--taps', type=int, required=True)
        p.add_argument('--bands', type=float, nargs='+', required=True, help='band edges in Hz, two per band')
        p.add_argument('--desired', type=float, nargs='+', required=True, help='gain per band')
        p.add_argument('--weight', type=float, nargs='+', help='weight per band')
        if name == 'equiripple':
            p.add_argument('--kind', choices=['bandpass', 'differentiator', 'hilbert'], default='bandpass')
    return parser


def design_from_args(args):
    """Return (coefficients, passbands, stopbands) for parsed arguments."""
    passbands, stopbands = [], []
    if args.method == 'window':
        b = designer.design(args.taps, _cutoff(args.cutoff), args.fs, args.btype,
                            window=args.window, width=args.width)
    elif args.method == 'kaiser':
        b = designer.kaiser(_cutoff(args.cutoff), args.fs, args.btype,
                            attenuation_db=args.attenuation, width=args.width)
    else:
        if len(args.bands) != 2 * len(args.desired):
            raise ValueError('--bands needs two edges for every --desired gain')
        if args.method == 'equiripple':
            b = designer.equiripple(args.taps, args.bands, args.desired, args.fs,
                                    weight=args.weight, kind=args.kind)
        else:
            b = designer.least_squares(args.taps, args.bands, args.desired, args.fs, weight=args.weight)
        if getattr(args, 'kind', 'bandpass') == 'bandpass':
            passbands, stopbands = _bands_from_gains(args.bands, args.desired)
    if args.min_phase:
        b = designer.to_minimum_phase(b, args.min_phase)
    return b, passbands, stopbands


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        b, passbands, stopbands = design_from_args(args)
    except ValueError as e:
        sys.exit(f'fir-design: error: {e}')

    if args.output:
        designer.save_coefficients(b, args.output)
    else:
        np.savetxt(sys.stdout, b, fmt='%.18e')

    if args.summary:
        for key, value in analysis.summary(b, args.fs, passbands, stopbands).items():
            print(f'{key}: {value}', file=sys.stderr)

    if args.plot:
        import matplotlib.pylab as plt
        from . import plotting
        plotting.plot_frequency_response(b, args.fs)
        plt.title(f'{args.method}, {len(b)} taps')
        plt.show()


if __name__ == '__main__':
    main()
