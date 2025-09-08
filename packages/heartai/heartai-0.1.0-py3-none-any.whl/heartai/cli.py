"""
Command-line interface for HeartAI
"""

import click
import sys
from pathlib import Path
import logging
from typing import Optional

from .core.analyzer import ECGAnalyzer
from .utils.helpers import generate_sample_ecg, create_sample_dataset
from .visualization.plotter import ECGPlotter
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """
    HeartAI - ECG/EKG signal processing and arrhythmia detection library
    
    A powerful tool for analyzing ECG signals and detecting potential arrhythmias
    using machine learning techniques.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.argument('ecg_file', type=click.Path(exists=True))
@click.option('--sampling-rate', '-sr', default=360.0, help='Sampling rate in Hz (default: 360)')
@click.option('--output', '-o', help='Output file for results (JSON format)')
@click.option('--plot', '-p', help='Save plot to file (PNG/PDF format)')
@click.option('--confidence-threshold', '-t', default=0.5, help='Confidence threshold for prediction (default: 0.5)')
@click.option('--show-plot', is_flag=True, help='Display plot interactively')
def predict(ecg_file, sampling_rate, output, plot, confidence_threshold, show_plot):
    """
    Predict arrhythmia risk from ECG data file.
    
    ECG_FILE: Path to ECG data file (CSV, TXT, or NPY format)
    """
    try:
        click.echo(f"🫀 HeartAI - Analyzing ECG data from: {ecg_file}")
        
        # Initialize analyzer
        analyzer = ECGAnalyzer(data_path=ecg_file, sampling_rate=sampling_rate)
        
        # Run analysis
        with click.progressbar(length=3, label='Processing ECG data') as bar:
            bar.update(1)  # Data loaded
            
            # Preprocess
            analyzer.preprocess()
            bar.update(1)  # Preprocessing done
            
            # Predict
            results = analyzer.predict(confidence_threshold=confidence_threshold)
            bar.update(1)  # Prediction done
        
        # Display results
        click.echo("\n📊 Analysis Results:")
        click.echo(f"Status: {results['status']}")
        click.echo(f"Confidence: {results['confidence']:.1%}")
        click.echo(f"Risk Level: {results['risk_level']}")
        
        # Save results to file if requested
        if output:
            import json
            complete_results = analyzer.get_summary()
            with open(output, 'w') as f:
                json.dump(complete_results, f, indent=2, default=str)
            click.echo(f"Results saved to: {output}")
        
        # Create and save plot if requested
        if plot or show_plot:
            plotter = ECGPlotter()
            fig = plotter.plot_prediction_result(
                analyzer.processed_data, 
                results, 
                sampling_rate=sampling_rate
            )
            
            if plot:
                fig.savefig(plot, dpi=150, bbox_inches='tight')
                click.echo(f"Plot saved to: {plot}")
            
            if show_plot:
                plotter.show_plots()
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--duration', '-d', default=10.0, help='Duration in seconds (default: 10)')
@click.option('--sampling-rate', '-sr', default=360.0, help='Sampling rate in Hz (default: 360)')
@click.option('--heart-rate', '-hr', default=75.0, help='Heart rate in BPM (default: 75)')
@click.option('--noise-level', '-n', default=0.1, help='Noise level 0-1 (default: 0.1)')
@click.option('--arrhythmia', is_flag=True, help='Generate arrhythmia pattern')
@click.option('--output', '-o', required=True, help='Output file for generated ECG (CSV format)')
@click.option('--plot', '-p', help='Save plot to file (PNG/PDF format)')
def generate(duration, sampling_rate, heart_rate, noise_level, arrhythmia, output, plot):
    """
    Generate synthetic ECG data for testing and demonstration.
    """
    try:
        click.echo(f"🔬 Generating synthetic ECG data...")
        click.echo(f"Duration: {duration}s, Heart Rate: {heart_rate} BPM, Arrhythmia: {arrhythmia}")
        
        # Generate ECG signal
        ecg_signal = generate_sample_ecg(
            duration=duration,
            sampling_rate=sampling_rate,
            heart_rate=heart_rate,
            noise_level=noise_level,
            arrhythmia=arrhythmia
        )
        
        # Save to CSV
        import pandas as pd
        time_axis = np.arange(len(ecg_signal)) / sampling_rate
        df = pd.DataFrame({
            'time': time_axis,
            'ecg': ecg_signal
        })
        df.to_csv(output, index=False)
        click.echo(f"ECG data saved to: {output}")
        
        # Create plot if requested
        if plot:
            plotter = ECGPlotter()
            title = f"Synthetic ECG - {'Arrhythmia' if arrhythmia else 'Normal'} ({heart_rate} BPM)"
            fig = plotter.plot_ecg(ecg_signal, sampling_rate, title=title)
            fig.savefig(plot, dpi=150, bbox_inches='tight')
            click.echo(f"Plot saved to: {plot}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('ecg_file', type=click.Path(exists=True))
@click.option('--sampling-rate', '-sr', default=360.0, help='Sampling rate in Hz (default: 360)')
@click.option('--output', '-o', help='Output directory for plots')
@click.option('--show', is_flag=True, help='Display plots interactively')
def analyze(ecg_file, sampling_rate, output, show):
    """
    Comprehensive ECG analysis with detailed visualizations.
    
    ECG_FILE: Path to ECG data file (CSV, TXT, or NPY format)
    """
    try:
        click.echo(f"🔍 Comprehensive ECG Analysis: {ecg_file}")
        
        # Initialize analyzer
        analyzer = ECGAnalyzer(data_path=ecg_file, sampling_rate=sampling_rate)
        
        # Run complete analysis
        with click.progressbar(length=4, label='Running analysis') as bar:
            # Preprocess
            analyzer.preprocess()
            bar.update(1)
            
            # Predict
            results = analyzer.predict()
            bar.update(1)
            
            # Create visualizations
            plotter = ECGPlotter()
            bar.update(1)
            
            # Generate plots
            output_dir = Path(output) if output else Path.cwd()
            output_dir.mkdir(exist_ok=True)
            
            # 1. Basic ECG plot
            fig1 = plotter.plot_ecg(analyzer.processed_data, sampling_rate, 
                                   title="Processed ECG Signal")
            if output:
                fig1.savefig(output_dir / "ecg_signal.png", dpi=150, bbox_inches='tight')
            
            # 2. Raw vs processed comparison
            fig2 = plotter.plot_comparison(analyzer.raw_data, analyzer.processed_data, 
                                          sampling_rate)
            if output:
                fig2.savefig(output_dir / "comparison.png", dpi=150, bbox_inches='tight')
            
            # 3. Prediction result
            fig3 = plotter.plot_prediction_result(analyzer.processed_data, results, 
                                                 sampling_rate)
            if output:
                fig3.savefig(output_dir / "prediction.png", dpi=150, bbox_inches='tight')
            
            # 4. Summary report
            complete_results = analyzer.get_summary()
            complete_results.update(results)
            fig4 = plotter.create_summary_report(complete_results)
            if output:
                fig4.savefig(output_dir / "summary_report.png", dpi=150, bbox_inches='tight')
            
            bar.update(1)
        
        # Display results
        click.echo("\n📊 Analysis Complete!")
        click.echo(f"Status: {results['status']}")
        click.echo(f"Confidence: {results['confidence']:.1%}")
        click.echo(f"Risk Level: {results['risk_level']}")
        
        if output:
            click.echo(f"\n📁 Plots saved to: {output_dir}")
            click.echo("Generated files:")
            click.echo("  - ecg_signal.png: Processed ECG signal")
            click.echo("  - comparison.png: Raw vs processed comparison")
            click.echo("  - prediction.png: Prediction results")
            click.echo("  - summary_report.png: Comprehensive report")
        
        if show:
            plotter.show_plots()
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--normal-samples', '-n', default=100, help='Number of normal samples (default: 100)')
@click.option('--arrhythmia-samples', '-a', default=100, help='Number of arrhythmia samples (default: 100)')
@click.option('--duration', '-d', default=10.0, help='Duration per sample in seconds (default: 10)')
@click.option('--sampling-rate', '-sr', default=360.0, help='Sampling rate in Hz (default: 360)')
@click.option('--output-dir', '-o', required=True, help='Output directory for dataset')
def create_dataset(normal_samples, arrhythmia_samples, duration, sampling_rate, output_dir):
    """
    Create a synthetic dataset for training and testing.
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"🏗️ Creating synthetic dataset...")
        click.echo(f"Normal samples: {normal_samples}, Arrhythmia samples: {arrhythmia_samples}")
        click.echo(f"Output directory: {output_path}")
        
        # Create dataset
        with click.progressbar(length=normal_samples + arrhythmia_samples, 
                             label='Generating samples') as bar:
            
            signals, labels = create_sample_dataset(
                n_normal=normal_samples,
                n_arrhythmia=arrhythmia_samples,
                duration=duration,
                sampling_rate=sampling_rate
            )
            bar.update(normal_samples + arrhythmia_samples)
        
        # Save dataset
        import pandas as pd
        
        # Save signals as individual CSV files
        for i, (signal, label) in enumerate(zip(signals, labels)):
            time_axis = np.arange(len(signal)) / sampling_rate
            df = pd.DataFrame({
                'time': time_axis,
                'ecg': signal
            })
            
            label_str = 'arrhythmia' if label == 1 else 'normal'
            filename = f"{label_str}_{i:04d}.csv"
            df.to_csv(output_path / filename, index=False)
        
        # Save metadata
        metadata = {
            'total_samples': len(signals),
            'normal_samples': normal_samples,
            'arrhythmia_samples': arrhythmia_samples,
            'duration_seconds': duration,
            'sampling_rate_hz': sampling_rate,
            'samples_per_signal': len(signals[0])
        }
        
        import json
        with open(output_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        click.echo(f"✅ Dataset created successfully!")
        click.echo(f"Total files: {len(signals)} ECG samples + 1 metadata file")
        click.echo(f"Normal samples: {normal_samples}")
        click.echo(f"Arrhythmia samples: {arrhythmia_samples}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def info():
    """
    Display information about HeartAI library.
    """
    click.echo("🫀 HeartAI - ECG/EKG Signal Processing & Arrhythmia Detection")
    click.echo("=" * 60)
    click.echo("Version: 0.1.0")
    click.echo("Author: AhmetXHero")
    click.echo("License: MIT")
    click.echo("")
    click.echo("Features:")
    click.echo("  📊 ECG signal processing (filtering, normalization)")
    click.echo("  🤖 AI-powered arrhythmia detection")
    click.echo("  📈 Advanced visualization tools")
    click.echo("  🔌 Extensible and modular design")
    click.echo("")
    click.echo("Supported file formats: CSV, TXT, NPY")
    click.echo("Default sampling rate: 360 Hz")
    click.echo("")
    click.echo("For more information, visit: https://github.com/ahmetxhero/AhmetX-HeartAi")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
