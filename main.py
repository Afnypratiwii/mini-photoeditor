import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Mini Photo Editor", layout="wide")

#  LOAD CSS 
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')

# FUNGSI CALLBACK UNTUK SELECTBOX 
def update_grayscale():
    st.session_state.grayscale_enabled = (st.session_state.grayscale_select == "Ya")

def update_histogram():
    st.session_state.histogram_enabled = (st.session_state.histogram_select == "Ya")

def update_blur():
    st.session_state.blur_enabled = (st.session_state.blur_select == "Ya")

def update_sharpen():
    st.session_state.sharpen_enabled = (st.session_state.sharpen_select == "Ya")

def update_invert():
    st.session_state.invert_enabled = (st.session_state.invert_select == "Ya")

def update_brightness():
    st.session_state.brightness_enabled = (st.session_state.brightness_select == "Ya")
    if not st.session_state.brightness_enabled:
        st.session_state.brightness = 0
        st.session_state.contrast = 1.0

def update_edge():
    st.session_state.edge_enabled = (st.session_state.edge_select == "Ya")

def update_threshold():
    st.session_state.threshold_enabled = (st.session_state.threshold_select == "Ya")

def update_rotate():
    st.session_state.rotate_enabled = (st.session_state.rotate_select == "Ya")
    if not st.session_state.rotate_enabled:
        st.session_state.rotation = 0

def update_resize():
    st.session_state.resize_enabled = (st.session_state.resize_select == "Ya")
    if not st.session_state.resize_enabled and st.session_state.gambar_asli is not None:
        tinggi_asli, lebar_asli = st.session_state.gambar_asli.shape[:2]
        st.session_state.resize_width = lebar_asli
        st.session_state.resize_height = tinggi_asli

# Callback untuk slider brightness
def update_brightness_value():
    st.session_state.brightness = st.session_state.brightness_slider

def update_contrast_value():
    st.session_state.contrast = st.session_state.contrast_slider

# Callback untuk rotation angle
def update_rotation_angle():
    st.session_state.rotation = ["0°", "90°", "180°", "270°"].index(st.session_state.rotation_angle_select)

# Callback untuk resize dimensions
def update_resize_width():
    st.session_state.resize_width = st.session_state.resize_width_input

def update_resize_height():
    st.session_state.resize_height = st.session_state.resize_height_input

# FUNGSI TERAPKAN SEMUA EFEK 
def terapkan_semua_efek(gambar):
    """Menerapkan semua efek yang aktif pada gambar"""
    hasil = gambar.copy()
    hasil_bgr = cv2.cvtColor(hasil, cv2.COLOR_RGB2BGR)
    
    # Resize (Ubah Ukuran)
    if st.session_state.resize_enabled:
        tinggi_asli, lebar_asli = gambar.shape[:2]
        if st.session_state.resize_width != lebar_asli or st.session_state.resize_height != tinggi_asli:
            hasil_bgr = cv2.resize(hasil_bgr, (int(st.session_state.resize_width), int(st.session_state.resize_height)))
    
    # Rotate (Putar Gambar)
    if st.session_state.rotate_enabled and st.session_state.rotation > 0:
        if st.session_state.rotation == 1:
            hasil_bgr = cv2.rotate(hasil_bgr, cv2.ROTATE_90_CLOCKWISE)
        elif st.session_state.rotation == 2:
            hasil_bgr = cv2.rotate(hasil_bgr, cv2.ROTATE_180)
        elif st.session_state.rotation == 3:
            hasil_bgr = cv2.rotate(hasil_bgr, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    # Gaussian Blur
    if st.session_state.blur_enabled:
        hasil_bgr = cv2.GaussianBlur(hasil_bgr, (7, 7), 0)
    
    # Sharpen (Pertajam)
    if st.session_state.sharpen_enabled:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        hasil_bgr = cv2.filter2D(hasil_bgr, -1, kernel)
    
    # Kecerahan / Kontras
    if st.session_state.brightness_enabled and (st.session_state.brightness != 0 or st.session_state.contrast != 1.0):
        hasil_bgr = cv2.convertScaleAbs(hasil_bgr, alpha=st.session_state.contrast, beta=st.session_state.brightness)
    
    # Grayscale
    if st.session_state.grayscale_enabled:
        abu = cv2.cvtColor(hasil_bgr, cv2.COLOR_BGR2GRAY)
        hasil_bgr = cv2.cvtColor(abu, cv2.COLOR_GRAY2BGR)
    
    # Ekualisasi Histogram
    if st.session_state.histogram_enabled:
        abu = cv2.cvtColor(hasil_bgr, cv2.COLOR_BGR2GRAY)
        hist = cv2.equalizeHist(abu)
        hasil_bgr = cv2.cvtColor(hist, cv2.COLOR_GRAY2BGR)
    
    # Edge Detection (Deteksi Tepi)
    if st.session_state.edge_enabled:
        tepi = cv2.Canny(hasil_bgr, 100, 200)
        hasil_bgr = cv2.cvtColor(tepi, cv2.COLOR_GRAY2BGR)
    
    # Segmentation / Thresholding
    if st.session_state.threshold_enabled:
        abu = cv2.cvtColor(hasil_bgr, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(abu, 127, 255, cv2.THRESH_BINARY)
        hasil_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    
    # Invert (Balik Warna)(diterapkan terakhir)
    if st.session_state.invert_enabled:
        hasil_bgr = cv2.bitwise_not(hasil_bgr)
    
    # Konversi kembali ke RGB
    hasil = cv2.cvtColor(hasil_bgr, cv2.COLOR_BGR2RGB)
    return hasil

# INISIALISASI SESSION STATE 
if 'gambar_asli' not in st.session_state:
    st.session_state.gambar_asli = None

# Inisialisasi state untuk setiap efek
if 'grayscale_enabled' not in st.session_state:
    st.session_state.grayscale_enabled = False
if 'histogram_enabled' not in st.session_state:
    st.session_state.histogram_enabled = False
if 'blur_enabled' not in st.session_state:
    st.session_state.blur_enabled = False
if 'sharpen_enabled' not in st.session_state:
    st.session_state.sharpen_enabled = False
if 'invert_enabled' not in st.session_state:
    st.session_state.invert_enabled = False
if 'edge_enabled' not in st.session_state:
    st.session_state.edge_enabled = False
if 'threshold_enabled' not in st.session_state:
    st.session_state.threshold_enabled = False

# State untuk efek dengan pengaturan
if 'brightness_enabled' not in st.session_state:
    st.session_state.brightness_enabled = False
if 'brightness' not in st.session_state:
    st.session_state.brightness = 0
if 'contrast' not in st.session_state:
    st.session_state.contrast = 1.0

if 'rotate_enabled' not in st.session_state:
    st.session_state.rotate_enabled = False
if 'rotation' not in st.session_state:
    st.session_state.rotation = 0

if 'resize_enabled' not in st.session_state:
    st.session_state.resize_enabled = False
if 'resize_width' not in st.session_state:
    st.session_state.resize_width = None
if 'resize_height' not in st.session_state:
    st.session_state.resize_height = None

# NAVIGASI UTAMA 
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("---")
    
    halaman = st.radio(
        "**MENU**",
        ["🏠 Beranda", "🖼️ Edit Gambar"],
        label_visibility="visible"
    )
    
# HALAMAN BERANDA 
if halaman == "🏠 Beranda":
    st.title("MINI PHOTO EDITOR")
    st.markdown("---")
    
    # Kolom untuk layout yang lebih baik
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Selamat Datang!")
        st.write("""
        **Mini Photo Editor** adalah aplikasi berbasis web yang memungkinkan Anda 
        mengedit gambar dengan berbagai fitur pengolahan citra digital.
        """)
        
        st.subheader("📋 Fitur yang Tersedia:")
        
        features_col1, features_col2 = st.columns(2)
        
        with features_col1:
            st.markdown("""
            - **Grayscale**
            - **Ekualisasi Histogram**
            - **Gaussian Blur**
            - **Sharpen (Pertajam)**
            - **Invert (Balik Warna)**
            """)
        
        with features_col2:
            st.markdown("""
            - **Kecerahan / Kontras**
            - **Edge Detection (Deteksi Tepi)**
            - **Segmentation / Thresholding**
            - **Rotate (Putar Gambar)**
            - **Resize (Ubah Ukuran)**
            """)
    
    with col2:
        st.info("""
        ### 📖 Cara Menggunakan:
        
        1. Pilih **Edit Gambar** di menu
        2. Unggah gambar Anda
        3. Pilih efek yang diinginkan dengan dropdown **Ya/Tidak**
        4. Atur parameter di sidebar
        5. Unduh hasil editan
        """)
        
        st.success("✨ **Tips:** Anda bisa mengaktifkan beberapa efek sekaligus!")

# HALAMAN EDIT 
elif halaman == "🖼️ Edit Gambar":
    
    # SIDEBAR FILTER & PENGATURAN 
    # Unggah Gambar
    st.sidebar.markdown("---")
    st.sidebar.header("📤 Unggah Gambar")
    berkas_unggah = st.sidebar.file_uploader("Pilih file gambar", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if berkas_unggah:
        # Proses gambar baru
        if st.session_state.gambar_asli is None or st.session_state.get('id_berkas_unggah') != berkas_unggah.file_id:
            gambar = np.array(Image.open(berkas_unggah).convert("RGB"))
            st.session_state.gambar_asli = gambar
            st.session_state.id_berkas_unggah = berkas_unggah.file_id
            
            # Set ukuran default untuk resize
            tinggi_asli, lebar_asli = gambar.shape[:2]
            st.session_state.resize_width = lebar_asli
            st.session_state.resize_height = tinggi_asli
    
    # Cek apakah gambar sudah diunggah
    if st.session_state.gambar_asli is not None:
        st.sidebar.markdown("---")
        
        # GRAYSCALE 
        st.sidebar.subheader("Grayscale")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.grayscale_enabled else 0,
            key="grayscale_select",
            on_change=update_grayscale,
            label_visibility="collapsed"
        )
        
        # EKUALISASI HISTOGRAM 
        st.sidebar.subheader("Ekualisasi Histogram")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.histogram_enabled else 0,
            key="histogram_select",
            on_change=update_histogram,
            label_visibility="collapsed"
        )
        
        # GAUSSIAN BLUR
        st.sidebar.subheader("Gaussian Blur")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.blur_enabled else 0,
            key="blur_select",
            on_change=update_blur,
            label_visibility="collapsed"
        )
        
        # Sharpen (Pertajam) 
        st.sidebar.subheader("Sharpen (Pertajam)")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.sharpen_enabled else 0,
            key="sharpen_select",
            on_change=update_sharpen,
            label_visibility="collapsed"
        )
        
        # Invert (Balik Warna)
        st.sidebar.subheader("Invert (Balik Warna)")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.invert_enabled else 0,
            key="invert_select",
            on_change=update_invert,
            label_visibility="collapsed"
        )
        
        # KECERAHAN / KONTRAS 
        st.sidebar.subheader("Kecerahan / Kontras")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.brightness_enabled else 0,
            key="brightness_select",
            on_change=update_brightness,
            label_visibility="collapsed"
        )
        
        if st.session_state.brightness_enabled:
            st.sidebar.slider(
                "Kecerahan:",
                -100, 100, st.session_state.brightness,
                key="brightness_slider",
                on_change=update_brightness_value
            )
            st.sidebar.slider(
                "Kontras:",
                0.5, 3.0, st.session_state.contrast, 0.1,
                key="contrast_slider",
                on_change=update_contrast_value
            )
        
        # Edge Detection (Deteksi Tepi) 
        st.sidebar.subheader("Edge Detection (Deteksi Tepi)")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.edge_enabled else 0,
            key="edge_select",
            on_change=update_edge,
            label_visibility="collapsed"
        )
        
        # Segmentation / Thresholding 
        st.sidebar.subheader("Segmentation / Thresholding")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.threshold_enabled else 0,
            key="threshold_select",
            on_change=update_threshold,
            label_visibility="collapsed"
        )
        
        # PUTAR 
        st.sidebar.subheader("Rotate (Putar Gambar)")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.rotate_enabled else 0,
            key="rotate_select",
            on_change=update_rotate,
            label_visibility="collapsed"
        )
        
        if st.session_state.rotate_enabled:
            st.sidebar.selectbox(
                "Sudut Rotasi:",
                ["0°", "90°", "180°", "270°"],
                index=st.session_state.rotation,
                key="rotation_angle_select",
                on_change=update_rotation_angle
            )
        
        # UBAH UKURAN
        st.sidebar.subheader("Resize (Ubah Ukuran)")
        st.sidebar.selectbox(
            "Pilih:",
            ["Tidak", "Ya"],
            index=1 if st.session_state.resize_enabled else 0,
            key="resize_select",
            on_change=update_resize,
            label_visibility="collapsed"
        )
        
        if st.session_state.resize_enabled:
            tinggi_asli, lebar_asli = st.session_state.gambar_asli.shape[:2]
            st.sidebar.caption(f"Ukuran asli: {lebar_asli} x {tinggi_asli} px")
            
            st.sidebar.number_input(
                "Lebar (px):",
                min_value=10,
                max_value=5000,
                value=int(st.session_state.resize_width),
                key="resize_width_input",
                on_change=update_resize_width
            )
            st.sidebar.number_input(
                "Tinggi (px):",
                min_value=10,
                max_value=5000,
                value=int(st.session_state.resize_height),
                key="resize_height_input",
                on_change=update_resize_height
            )

        
        # TOMBOL RESET 
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Reset Semua Efek", use_container_width=True):
            st.session_state.grayscale_enabled = False
            st.session_state.histogram_enabled = False
            st.session_state.blur_enabled = False
            st.session_state.sharpen_enabled = False
            st.session_state.invert_enabled = False
            st.session_state.edge_enabled = False
            st.session_state.threshold_enabled = False
            st.session_state.brightness_enabled = False
            st.session_state.brightness = 0
            st.session_state.contrast = 1.0
            st.session_state.rotate_enabled = False
            st.session_state.rotation = 0
            st.session_state.resize_enabled = False
            tinggi_asli, lebar_asli = st.session_state.gambar_asli.shape[:2]
            st.session_state.resize_width = lebar_asli
            st.session_state.resize_height = tinggi_asli
            st.rerun()
        
        # SIMPAN GAMBAR 
        st.sidebar.markdown("---")
        st.sidebar.subheader("💾 Simpan Gambar")
        
        # Terapkan semua efek untuk preview download
        gambar_hasil_download = terapkan_semua_efek(st.session_state.gambar_asli)
        
        # Konversi ke PIL Image
        gambar_pil = Image.fromarray(gambar_hasil_download.astype('uint8'), 'RGB')
        
        # Format JPG
        buffer_jpg = io.BytesIO()
        gambar_pil.save(buffer_jpg, format="JPEG", quality=95)
        byte_jpg = buffer_jpg.getvalue()
        
        # Format PNG
        buffer_png = io.BytesIO()
        gambar_pil.save(buffer_png, format="PNG")
        byte_png = buffer_png.getvalue()
        
        st.sidebar.download_button(
            label="📥 Unduh JPG",
            data=byte_jpg,
            file_name="gambar_edit.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
        
        st.sidebar.download_button(
            label="📥 Unduh PNG",
            data=byte_png,
            file_name="gambar_edit.png",
            mime="image/png",
            use_container_width=True
        )
    
    # AREA KONTEN UTAMA 
    if st.session_state.gambar_asli is None:
        # Tampilan ketika belum ada gambar
        st.info("📤 Silakan unggah gambar di sidebar untuk mulai mengedit.")
    
    else:
        # Terapkan semua efek
        gambar_hasil = terapkan_semua_efek(st.session_state.gambar_asli)
        
        # Tampilkan gambar dalam tab
        tab1, tab2 = st.tabs(["🖼️ Hasil Edit", "📊 Perbandingan"])
        
        with tab1:
            st.image(gambar_hasil, caption="Gambar Hasil Edit", use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(st.session_state.gambar_asli, caption="Gambar Asli", use_container_width=True)
            
            with col2:
                st.image(gambar_hasil, caption="Hasil Edit", use_container_width=True)
            
            # Informasi ukuran
            st.markdown("---")
            col1, col2 = st.columns(2)
            tinggi_asli, lebar_asli = st.session_state.gambar_asli.shape[:2]
            tinggi_hasil, lebar_hasil = gambar_hasil.shape[:2]
            
            with col1:
                st.metric("Ukuran Asli", f"{lebar_asli} x {tinggi_asli} px")
            with col2:
                st.metric("Ukuran Hasil", f"{lebar_hasil} x {tinggi_hasil} px")