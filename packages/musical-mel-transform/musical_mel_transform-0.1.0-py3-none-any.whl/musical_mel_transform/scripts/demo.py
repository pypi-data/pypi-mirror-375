#!/usr/bin/env python3
"""Demo script for Musical Mel Transform.

This script demonstrates various features and options of the musical mel transform,
including different parameter settings, visualizations, and performance comparisons.
"""

import argparse
import sys
import time
from pathlib import Path

import librosa
import numpy as np
import torch

from musical_mel_transform import MusicalMelTransform, convert_to_onnx, plot_low_filters


def _import_matplotlib():
    """Import matplotlib with helpful error message if not available."""
    try:
        import matplotlib.pyplot as plt

        return plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for plotting demos. Install it with: "
            "pip install 'musical-mel-transform[plot]' or pip install matplotlib"
        )


def create_test_signals(sample_rate: int = 44100, duration: float = 2.0):
    """Create various test signals for demonstration."""
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples)

    signals = {}

    # Musical chord (C major)
    c_major_freqs = [261.63, 329.63, 392.00]  # C4, E4, G4
    chord = sum(0.3 * np.sin(2 * np.pi * f * t) for f in c_major_freqs)
    signals["c_major_chord"] = chord

    # Chromatic scale sweep
    start_freq = 220  # A3
    end_freq = 880  # A5
    sweep = np.sin(2 * np.pi * np.geomspace(start_freq, end_freq, n_samples) * t)
    signals["chromatic_sweep"] = sweep

    # White noise
    noise = 0.1 * np.random.randn(n_samples)
    signals["white_noise"] = noise

    # Harmonic series
    fundamental = 110  # A2
    harmonics = sum(
        (1 / (i + 1)) * np.sin(2 * np.pi * fundamental * (i + 1) * t) for i in range(8)
    )
    signals["harmonic_series"] = harmonics

    return signals


def demo_basic_usage():
    """Demonstrate basic usage of the musical mel transform."""
    print("=== Basic Usage Demo ===")

    # Create transform
    transform = MusicalMelTransform(
        sample_rate=44100,
        frame_size=2048,
        interval=1.0,  # Semitone resolution
        f_min=80.0,
        f_max=8000.0,
        use_conv_fft=True,
    )

    print(f"Created transform with {transform.n_mel} mel bins")
    print(f"FFT resolution: {transform.fft_resolution:.2f} Hz")

    # Generate test signal (must match frame_size)
    test_signal = np.sin(
        2 * np.pi * 440 * np.linspace(0, 1, transform.frame_size)
    )  # A4
    frames = torch.from_numpy(test_signal.astype(np.float32)).unsqueeze(0)

    # Transform
    with torch.no_grad():
        mel_spec, fft_mag = transform(frames)

    print(f"Input shape: {frames.shape}")
    print(f"Mel spectrogram shape: {mel_spec.shape}")
    print(f"FFT magnitude shape: {fft_mag.shape}")

    return transform, mel_spec, fft_mag


def demo_parameter_comparison():
    """Compare different parameter settings."""
    print("\n=== Parameter Comparison Demo ===")

    # Test different intervals
    intervals = [0.5, 1.0, 2.0]  # Quarter-tone, semitone, whole-tone
    sample_rate = 44100
    frame_size = 2048

    # Create test signal (C major chord) - use frame_size length
    c_major_freqs = [261.63, 329.63, 392.00]
    t = np.linspace(0, frame_size / sample_rate, frame_size)
    test_signal = sum(0.3 * np.sin(2 * np.pi * f * t) for f in c_major_freqs)
    frames = torch.from_numpy(test_signal.astype(np.float32)).unsqueeze(0)

    plt = _import_matplotlib()

    fig, axes = plt.subplots(len(intervals), 1, figsize=(12, 3 * len(intervals)))
    if len(intervals) == 1:
        axes = [axes]

    for i, interval in enumerate(intervals):
        transform = MusicalMelTransform(
            sample_rate=sample_rate,
            frame_size=frame_size,
            interval=interval,
            f_min=200.0,
            f_max=500.0,
            use_conv_fft=True,
        )

        with torch.no_grad():
            mel_spec, _ = transform(frames)

        # Plot
        mel_freqs = transform.mel_freqs.cpu().numpy()
        axes[i].plot(mel_freqs, mel_spec.squeeze().cpu().numpy(), "o-")
        axes[i].set_xlabel("Frequency (Hz)")
        axes[i].set_ylabel("Magnitude")
        axes[i].set_title(f"Interval: {interval} semitones ({transform.n_mel} bins)")
        axes[i].grid(True, alpha=0.3)

        # Mark the input frequencies
        for freq in c_major_freqs:
            if 200 <= freq <= 500:
                axes[i].axvline(
                    freq, color="red", linestyle="--", alpha=0.7, label=f"{freq:.1f} Hz"
                )
        axes[i].legend()

    plt.tight_layout()
    plt.savefig("parameter_comparison.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("Saved parameter comparison plot as 'parameter_comparison.png'")


def demo_filterbank_visualization():
    """Visualize the mel filterbank."""
    print("\n=== Filterbank Visualization Demo ===")

    transform = MusicalMelTransform(
        sample_rate=44100,
        frame_size=2048,
        interval=1.0,
        f_max=2000.0,
        use_conv_fft=True,
    )

    # Plot low-frequency filters
    plot_low_filters(
        transform,
        bank_idx_to_show=[0, 1, 2, 3, 4, 5, 10, 15, 20, 25],
        x_max_hz=300,
        legend=True,
    )

    print("Displayed filterbank visualization")


def demo_performance_comparison():
    """Compare performance of different FFT implementations."""
    print("\n=== Performance Comparison Demo ===")

    sample_rate = 44100
    frame_sizes = [256, 512, 1024, 2048, 4096]
    n_iterations = 100

    for frame_size in frame_sizes:
        # Create transforms
        transform_conv = MusicalMelTransform(
            sample_rate=sample_rate,
            frame_size=frame_size,
            use_conv_fft=True,
        )

        transform_torch = MusicalMelTransform(
            sample_rate=sample_rate,
            frame_size=frame_size,
            use_conv_fft=False,
        )

        # Create test signal (use frame_size)
        test_signal = np.random.randn(frame_size).astype(np.float32)
        frames = torch.from_numpy(test_signal).unsqueeze(0)

        # Warm up
        with torch.no_grad():
            for _ in range(10):
                transform_conv(frames)
                transform_torch(frames)

        # Benchmark Conv FFT
        conv_times = []
        with torch.no_grad():
            for _ in range(n_iterations):
                start = time.time()
                transform_conv(frames)
                conv_times.append((time.time() - start) * 1000)

        # Benchmark Torch FFT
        torch_times = []
        with torch.no_grad():
            for _ in range(n_iterations):
                start = time.time()
                transform_torch(frames)
                torch_times.append((time.time() - start) * 1000)

        conv_avg = np.mean(conv_times)
        torch_avg = np.mean(torch_times)

        print(f"@ Frame size: {frame_size}")
        print(f"Conv FFT: {conv_avg:.2f} ± {np.std(conv_times):.2f} ms")
        print(f"Torch FFT: {torch_avg:.2f} ± {np.std(torch_times):.2f} ms")
        print(f"Speedup (torch vs convFFT): {conv_avg / torch_avg:.2f}x")
        print("-" * 100)


def demo_onnx_export():
    """Demonstrate ONNX export functionality."""
    print("\n=== ONNX Export Demo ===")

    transform = MusicalMelTransform(
        sample_rate=44100,
        frame_size=1024,
        use_conv_fft=True,  # Required for ONNX export
    )

    # Export to ONNX
    onnx_path = "demo_musical_mel.onnx"
    convert_to_onnx(transform, onnx_path, opset=18)

    print(f"Successfully exported to {onnx_path}")

    # Clean up
    Path(onnx_path).unlink(missing_ok=True)


def demo_musical_analysis():
    """Demonstrate musical analysis capabilities."""
    print("\n=== Musical Analysis Demo ===")

    # Create transform optimized for musical analysis
    transform = MusicalMelTransform(
        sample_rate=44100,
        frame_size=4096,  # Higher resolution for better frequency precision
        interval=0.5,  # Quarter-tone resolution
        f_min=65.0,  # C2
        f_max=4186.0,  # C8
        adaptive=True,
        use_conv_fft=True,
    )

    # Generate musical test signals
    signals = create_test_signals()

    plt = _import_matplotlib()

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    for i, (name, signal) in enumerate(signals.items()):
        if i >= 4:
            break

        # Truncate or pad signal to match frame_size
        if len(signal) > transform.frame_size:
            signal = signal[: transform.frame_size]
        elif len(signal) < transform.frame_size:
            signal = np.pad(signal, (0, transform.frame_size - len(signal)))

        frames = torch.from_numpy(signal.astype(np.float32)).unsqueeze(0)

        with torch.no_grad():
            mel_spec, _ = transform(frames)

        mel_freqs = transform.mel_freqs.cpu().numpy()
        mel_values = mel_spec.squeeze().cpu().numpy()

        axes[i].plot(mel_freqs, mel_values, "o-", markersize=3)
        axes[i].set_xlabel("Frequency (Hz)")
        axes[i].set_ylabel("Magnitude")
        axes[i].set_title(f"Musical Analysis: {name.replace('_', ' ').title()}")
        axes[i].grid(True, alpha=0.3)
        axes[i].set_xscale("log")

    plt.tight_layout()
    plt.savefig("musical_analysis.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("Saved musical analysis plot as 'musical_analysis.png'")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Musical Mel Transform Demo")
    parser.add_argument(
        "--demo",
        choices=["all", "basic", "params", "filters", "performance", "onnx", "musical"],
        default="all",
        help="Which demo to run",
    )
    parser.add_argument("--no-plots", action="store_true", help="Skip plot generation")

    args = parser.parse_args()

    print("Musical Mel Transform Demo")
    print("=" * 50)

    try:
        if args.demo in ["all", "basic"]:
            demo_basic_usage()

        if args.demo in ["all", "params"] and not args.no_plots:
            demo_parameter_comparison()

        if args.demo in ["all", "filters"] and not args.no_plots:
            demo_filterbank_visualization()

        if args.demo in ["all", "performance"]:
            demo_performance_comparison()

        if args.demo in ["all", "onnx"]:
            demo_onnx_export()

        if args.demo in ["all", "musical"] and not args.no_plots:
            demo_musical_analysis()

        print("\n" + "=" * 50)
        print("Demo completed successfully!")

    except Exception as e:
        print(f"Error during demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
