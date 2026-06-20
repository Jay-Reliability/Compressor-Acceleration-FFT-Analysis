import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter1d
import io

# Page Configuration
st.set_page_config(
    page_title="Compressor Acceleration Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Theme & Glassmorphism Aesthetics)
st.markdown("""
    <style>
        /* Base Background and Fonts */
        .reportview-container {
            background: #0a0a0f;
        }
        
        /* Metric Badges styling */
        .metric-badge {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 10px 15px;
            text-align: center;
        }
        .metric-label {
            font-size: 0.8rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.15rem;
            font-weight: 700;
            color: #00e5ff;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(20, 20, 30, 0.8);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("📊 Compressor Acceleration Analysis Dashboard")
st.markdown("High-Fidelity Vibration Signal Processing & FFT Diagnostics Web Application")
st.write("---")

# Signal Processing Functions

def compute_fft(signal, sampling_rate, num_samples):
    # Apply Hamming window
    window = np.hamming(len(signal))
    windowed_signal = signal * window
    
    # Magnitude correction
    signal_rms = np.sqrt(np.mean(windowed_signal**2))
    mean_abs = np.mean(np.abs(windowed_signal))
    signal_ratio = signal_rms / mean_abs if mean_abs > 0 else 1.0
    
    # FFT calculation
    Xk = np.fft.fft(windowed_signal, num_samples)
    magXk = (np.abs(Xk) / len(signal)) * signal_ratio
    
    # Scale non-DC and non-Nyquist frequencies by 2 (Single-sided correction)
    magXk[1:int(num_samples/2)] *= 2
    magXk1 = magXk[0:int(num_samples/2)]
    
    frequencies = np.fft.fftfreq(num_samples, d=1/sampling_rate)
    frequencies = frequencies[0:int(num_samples/2)]
    
    return frequencies, magXk1

# Sidebar Panel - File Loading & Configurations
st.sidebar.header("📁 Data Loader")

uploaded_file = st.sidebar.file_uploader(
    "Choose Vibration CSV File", 
    type=["csv"],
    help="Upload your time domain acceleration data. Expected columns: Time, CH11, CH12..."
)

if uploaded_file is not None:
    # Read CSV Header first to get columns efficiently
    @st.cache_data
    def load_data(file):
        df = pd.read_csv(file)
        return df
    
    try:
        df = load_data(uploaded_file)
        headers = list(df.columns)
        
        # Metadata Calculation
        # total_duration = df['Time'].iloc[-1]
        # sampling_rate = int(len(df) / total_duration)
        
        # Auto-detect Time column
        time_col_default = "Time" if "Time" in headers else headers[0]
        time_col = st.sidebar.selectbox("Select Time Column", headers, index=headers.index(time_col_default))
        
        total_samples = len(df)
        total_duration = df[time_col].iloc[-1] - df[time_col].iloc[0]
        sampling_rate = int(round(total_samples / total_duration)) if total_duration > 0 else 1.0
        
        # Display File Information Card
        st.sidebar.markdown("### ℹ️ File Information")
        st.sidebar.info(
            f"**File Name:** {uploaded_file.name}\n\n"
            f"**Total Samples:** {total_samples:,}\n\n"
            f"**Total Duration:** {total_duration:.3f} s\n\n"
            f"**Sampling Rate:** {sampling_rate:,} Hz"
        )
        
        st.sidebar.write("---")
        st.sidebar.header("⚙️ Settings")
        
        # Channel Selector
        potential_channels = [h for h in headers if h != time_col]
        default_selected = [ch for ch in ["CH11", "CH12"] if ch in potential_channels]
        if not default_selected:
            default_selected = potential_channels[:2]
            
        selected_channels = st.sidebar.multiselect(
            "Select Analysis Channels", 
            potential_channels, 
            default=default_selected
        )
        
        # Parameters Input
        start_time = st.sidebar.number_input(
            "Start Time (sec)", 
            value=15.0, 
            min_value=0.0, 
            max_value=float(max(0.0, total_duration - 0.1)),
            step=0.5
        )
        
        duration = st.sidebar.number_input(
            "Analysis Duration (sec)", 
            value=2.0, 
            min_value=0.1, 
            max_value=float(total_duration),
            step=0.5
        )
        
        max_freq_limit = st.sidebar.number_input(
            "Max FFT Frequency (Hz)", 
            value=200, 
            min_value=1, 
            max_value=int(sampling_rate / 2),
            step=50
        )
        
        sigma = st.sidebar.number_input(
            "Gaussian Filter Sigma (σ)", 
            value=0.5, 
            min_value=0.0, 
            max_value=10.0,
            step=0.1
        )
        
        scale_mode = st.sidebar.selectbox(
            "Default FFT Scale",
            options=["Linear", "dB (Ref: 10⁻⁵)"]
        )
        
        # Action button to trigger computation
        analyze_clicked = st.sidebar.button("⚡ Run Diagnostics", type="primary", use_container_width=True)
        
    except Exception as e:
        st.sidebar.error(f"Error reading CSV header: {e}")
        st.stop()
else:
    # Empty State Display
    st.info("💡 Please upload a vibration CSV file in the sidebar to begin analysis.")
    st.markdown("""
        ### Expected CSV File Format
        The file should contain a time column and one or more acceleration sensor channel columns. Example:
        
        | Time | CH11 | CH12 |
        | --- | --- | --- |
        | 0.0000 | 0.8396 | -1.8326 |
        | 0.0002 | 1.1350 | -2.3017 |
        | 0.0004 | 1.4781 | -2.6843 |
        
        Upload your file `TVN6_0124_1822_50deg_Time.csv` to see live analysis.
    """)
    st.stop()


# Core Calculation & Visualization Section

if analyze_clicked or 'analyzed' not in st.session_state:
    st.session_state.analyzed = True
    
    # Calculate boundary samples
    start_sample = int(round(start_time * sampling_rate))
    num_samples = int(round(duration * sampling_rate))
    
    if start_sample >= total_samples:
        st.error("Start sample is out of bounds for this dataset. Please decrease Start Time.")
        st.stop()
        
    actual_num_samples = min(num_samples, total_samples - start_sample)
    if actual_num_samples < 4:
        st.error("Not enough samples in the selected time range. Please increase duration.")
        st.stop()
        
    # Extract segment
    df_segment = df.iloc[start_sample : start_sample + actual_num_samples].copy()
    time_segment = df_segment[time_col].values
    
    # Cache and calculate calculations per channel
    channel_results = {}
    
    for ch in selected_channels:
        signal = df_segment[ch].values
        
        # Run FFT
        freqs, mag = compute_fft(signal, sampling_rate, len(signal))
        
        # Apply Gaussian filter
        if sigma > 0:
            smoothed_mag = gaussian_filter1d(mag, sigma=sigma)
        else:
            smoothed_mag = mag
            
        # Crop to maximum frequency limit
        limit_idx = np.searchsorted(freqs, max_freq_limit)
        freqs_cropped = freqs[:limit_idx]
        mag_cropped = smoothed_mag[:limit_idx]
        
        # Max / Min in Time Domain
        max_val = np.max(signal)
        max_idx_t = np.argmax(signal)
        min_val = np.min(signal)
        min_idx_t = np.argmin(signal)
        
        # Peak 1X detection in Frequency Domain (ignore DC at index 0)
        max_idx_f = np.argmax(mag_cropped[1:]) + 1 if len(mag_cropped) > 1 else 0
        freq1X = freqs_cropped[max_idx_f] if max_idx_f < len(freqs_cropped) else 0.0
        mag1X = mag_cropped[max_idx_f] if max_idx_f < len(mag_cropped) else 0.0
        
        # Overall Acceleration calculation (Peak RSS sum of the bins)
        overall_acc = np.sqrt(np.sum(mag_cropped[1:]**2))
        
        channel_results[ch] = {
            "signal": signal,
            "freqs": freqs_cropped,
            "mag": mag_cropped,
            "max_val": max_val,
            "max_time": time_segment[max_idx_t],
            "min_val": min_val,
            "min_time": time_segment[min_idx_t],
            "freq1X": freq1X,
            "mag1X": mag1X,
            "overall_acc": overall_acc
        }
    
    st.session_state.channel_results = channel_results
    st.session_state.time_segment = time_segment
    st.session_state.selected_channels = selected_channels


# Draw plots in columns
if 'channel_results' in st.session_state:
    results = st.session_state.channel_results
    t_seg = st.session_state.time_segment
    sel_ch = st.session_state.selected_channels
    
    # 2 Rows: Row 1 = Time Domain, Row 2 = Frequency Domain
    # Create columns matching the selected channels count
    cols = st.columns(len(sel_ch))
    
    # --- ROW 1: Time Domain Graphs ---
    for idx, ch in enumerate(sel_ch):
        with cols[idx]:
            ch_data = results[ch]
            
            # Setup Plotly Trace
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=t_seg, 
                y=ch_data["signal"], 
                mode='lines',
                line=dict(color='#00e5ff', width=1.5),
                name="Signal",
                hovertemplate="Time: %{x:.4f} s<br>Acc: %{y:.4f} g<extra></extra>"
            ))
            
            # Annotations for Max and Min
            fig.add_annotation(
                x=ch_data["max_time"], y=ch_data["max_val"],
                text=f"Max: {ch_data['max_val']:.3f}",
                showarrow=True, arrowhead=2, arrowcolor='#00e676', ax=0, ay=-30,
                font=dict(color='#00e676', size=9),
                bgcolor='rgba(0,0,0,0.8)', bordercolor='#00e676', borderwidth=1
            )
            
            fig.add_annotation(
                x=ch_data["min_time"], y=ch_data["min_val"],
                text=f"Min: {ch_data['min_val']:.3f}",
                showarrow=True, arrowhead=2, arrowcolor='#ff1744', ax=0, ay=30,
                font=dict(color='#ff1744', size=9),
                bgcolor='rgba(0,0,0,0.8)', bordercolor='#ff1744', borderwidth=1
            )
            
            fig.update_layout(
                title=dict(
                    text=f"📈 Time Domain - {ch}",
                    font=dict(size=15, color='#ffffff', family='Outfit')
                ),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40, r=20, t=40, b=40),
                height=350,
                xaxis=dict(
                    title=dict(text="Time (seconds)", font=dict(color='#94a3b8', size=11)),
                    gridcolor='rgba(255,255,255,0.05)',
                    zerolinecolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title=dict(text="Acceleration (g)", font=dict(color='#94a3b8', size=11)),
                    gridcolor='rgba(255,255,255,0.05)',
                    zerolinecolor='rgba(255,255,255,0.1)'
                )
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"time_{ch}")
            
    st.write("---")
            
    # --- ROW 2: Frequency Domain Graphs ---
    cols_f = st.columns(len(sel_ch))
    for idx, ch in enumerate(sel_ch):
        with cols_f[idx]:
            ch_data = results[ch]
            
            # Convert values based on scale mode
            freqs = ch_data["freqs"]
            mags = ch_data["mag"]
            
            if scale_mode == "dB (Ref: 10⁻⁵)":
                ref = 1e-5
                y_vals = 20 * np.log10(np.maximum(mags, 1e-12) / ref)
                y_label = "Amplitude (dB ref 10⁻⁵)"
                
                db1X = 20 * np.log10(max(ch_data["mag1X"], 1e-12) / ref)
                dbOA = 20 * np.log10(max(ch_data["overall_acc"], 1e-12) / ref)
                val1X_text = f"{db1X:.1f} dB"
                valOA_text = f"{dbOA:.1f} dB"
            else:
                y_vals = mags
                y_label = "Magnitude (g RMS)"
                val1X_text = f"{ch_data['mag1X']:.5f}"
                valOA_text = f"{ch_data['overall_acc']:.5f}"
                
            # Render Summary Cards inside the column
            st.markdown(f"""
                <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
                    <div class="metric-badge" style="flex: 1; min-width: 100px;">
                        <div class="metric-label">1X Freq</div>
                        <div class="metric-value">{ch_data['freq1X']:.2f} Hz</div>
                    </div>
                    <div class="metric-badge" style="flex: 1; min-width: 100px;">
                        <div class="metric-label">1X Mag</div>
                        <div class="metric-value">{val1X_text}</div>
                    </div>
                    <div class="metric-badge" style="flex: 1; min-width: 100px;">
                        <div class="metric-label">Overall Acc</div>
                        <div class="metric-value" style="color: #7c4dff;">{valOA_text}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Setup Plotly Trace
            fig_f = go.Figure()
            fig_f.add_trace(go.Scatter(
                x=freqs, 
                y=y_vals, 
                mode='lines',
                line=dict(color='#7c4dff', width=1.5),
                name="FFT Spectrum",
                hovertemplate="Freq: %{x:.2f} Hz<br>Amp: %{y:.5f}<extra></extra>"
            ))
            
            # Annotation for 1X peak
            if len(freqs) > 0:
                # Find maximum index in current y_vals (ignoring DC)
                max_idx_y = np.argmax(y_vals[1:]) + 1 if len(y_vals) > 1 else 0
                if max_idx_y < len(freqs):
                    fig_f.add_annotation(
                        x=freqs[max_idx_y], y=y_vals[max_idx_y],
                        text=f"1X Peak: {freqs[max_idx_y]:.2f} Hz",
                        showarrow=True, arrowhead=2, arrowcolor='#7c4dff', ax=30, ay=-30,
                        font=dict(color='#7c4dff', size=9),
                        bgcolor='rgba(0,0,0,0.8)', bordercolor='#7c4dff', borderwidth=1
                    )
            
            fig_f.update_layout(
                title=dict(
                    text=f"⚡ Frequency Domain (FFT) - {ch}",
                    font=dict(size=15, color='#ffffff', family='Outfit')
                ),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40, r=20, t=40, b=40),
                height=350,
                xaxis=dict(
                    title=dict(text="Frequency (Hz)", font=dict(color='#94a3b8', size=11)),
                    gridcolor='rgba(255,255,255,0.05)',
                    zerolinecolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    title=dict(text=y_label, font=dict(color='#94a3b8', size=11)),
                    gridcolor='rgba(255,255,255,0.05)',
                    zerolinecolor='rgba(255,255,255,0.1)'
                )
            )
            
            st.plotly_chart(fig_f, use_container_width=True, key=f"freq_{ch}")

    # --- CSV Export Section ---
    st.write("---")
    st.subheader("📥 Export FFT Calculation Data")
    
    # Generate CSV in memory
    csv_buffer = io.StringIO()
    csv_headers = ['Frequency (Hz)']
    for ch in sel_ch:
        csv_headers.append(f"{ch}_Mag_Linear")
        csv_headers.append(f"{ch}_Mag_dB")
        
    csv_buffer.write(','.join(csv_headers) + '\n')
    
    # We assume all channels share the same frequencies cropped list
    first_ch = sel_ch[0]
    freqs_export = results[first_ch]["freqs"]
    
    for i in range(len(freqs_export)):
        row = [f"{freqs_export[i]:.5f}"]
        for ch in sel_ch:
            lin_val = results[ch]["mag"][i]
            ref = 1e-5
            db_val = 20 * np.log10(max(lin_val, 1e-12) / ref)
            row.append(f"{lin_val:.8f}")
            row.append(f"{db_val:.4f}")
        csv_buffer.write(','.join(row) + '\n')
        
    # File download button
    export_filename = uploaded_file.name.replace('.csv', '') + '_FFT_Analysis.csv'
    st.download_button(
        label="Download FFT Data as CSV",
        data=csv_buffer.getvalue(),
        file_name=export_filename,
        mime="text/csv",
        help="Download the calculated FFT spectra (frequency, linear magnitude, and dB magnitude) for all active channels."
    )
