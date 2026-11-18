from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

# 8 Kota Nusantara
CITIES = {
    "purworejo": {"name": "Purworejo (Alun-Alun Utara)", "cost_mult": 0.80, "demand_base": 36, "vibe": "Modal Hemat & Pelajar Setia"},
    "jogja": {"name": "Yogyakarta (Jl. Kaliurang)", "cost_mult": 0.90, "demand_base": 52, "vibe": "Surga Mahasiswa & Wisata"},
    "solo": {"name": "Solo (Jl. Slamet Riyadi)", "cost_mult": 0.85, "demand_base": 48, "vibe": "Kuliner Malam Legendaris"},
    "semarang": {"name": "Semarang (Simpang Lima)", "cost_mult": 1.00, "demand_base": 55, "vibe": "Pusat Bisnis Pantura"},
    "malang": {"name": "Malang (Soekarno-Hatta)", "cost_mult": 0.92, "demand_base": 50, "vibe": "Kota Dingin Laris Kuah/Pedas"},
    "bandung": {"name": "Bandung (Jl. Braga)", "cost_mult": 1.10, "demand_base": 58, "vibe": "Anak Muda & Wisatawan"},
    "surabaya": {"name": "Surabaya (Tunjungan)", "cost_mult": 1.15, "demand_base": 62, "vibe": "Porsi Jumbo & Pedas Nampol"},
    "jakarta": {"name": "Jakarta (Blok M / Kemang)", "cost_mult": 1.35, "demand_base": 74, "vibe": "Sultan Metropolitan"}
}

# Menu Awal + Menu Rahasia Gacha
MENUS = {
    "lele": {"name": "Lele Marinasi Sambal Bawang", "base_cost": 9500, "ideal_price": 17000, "pop": 1.20, "rarity": "Starter", "unlocked": True},
    "nasgor": {"name": "Nasi Goreng Gila Babat", "base_cost": 12000, "ideal_price": 21000, "pop": 1.12, "rarity": "Starter", "unlocked": True},
    "mie": {"name": "Mie Nyemek Jogja Pedas Mampus", "base_cost": 10000, "ideal_price": 18500, "pop": 1.18, "rarity": "Common", "unlocked": False},
    "ayam": {"name": "Pecel Ayam Lamongan + Kremes", "base_cost": 14000, "ideal_price": 24000, "pop": 1.10, "rarity": "Common", "unlocked": False},
    "sate": {"name": "Sate Taichan & Lontong", "base_cost": 15000, "ideal_price": 26500, "pop": 1.08, "rarity": "Rare", "unlocked": False},
    "bebek": {"name": "Bebek Madura Bumbu Hitam", "base_cost": 20000, "ideal_price": 35000, "pop": 1.02, "rarity": "Rare", "unlocked": False},
    "iga": {"name": "Iga Bakar Madu Keraton", "base_cost": 26000, "ideal_price": 44000, "pop": 0.96, "rarity": "Legendary", "unlocked": False},
    "lobster": {"name": "Lobster & Kepiting Saus Padang", "base_cost": 34000, "ideal_price": 58000, "pop": 0.90, "rarity": "Legendary", "unlocked": False}
}

# Pelanggan VIP Nusantara dengan Dialog Interaktif
VIP_ENCOUNTERS = [
    {
        "id": "pak_rt",
        "name": "Pak RT Wibowo",
        "role": "Tokoh Masyarakat Setempat",
        "avatar": "👨‍💼",
        "dialog": "Malam Juragan! Malam ini warga lagi rapat ronda di pos kamling. Boleh minta konsumsi 15 porsi buat warga? Nanti izin lapakmu saya jamin aman dari razia!",
        "optA": {"label": "Siap Pak RT! Gratis buat warga (Biaya Rp 200rb)", "cash": -200000, "rep": 15, "shield": True, "reply": "Mantap! Warga senang, lapakmu aman sentosa!"},
        "optB": {"label": "Maaf Pak, stok lagi mepet banget", "cash": 0, "rep": -5, "shield": False, "reply": "Oh ya sudah, hati-hati saja kalau ada penertiban ya."}
    },
    {
        "id": "vlogger",
        "name": "Bang Nex & Mbak Magdalen KW",
        "role": "Food Vlogger 5 Juta Subscribers",
        "avatar": "🤳",
        "dialog": "Halo Juragan! Banyak netizen request review warung ini. Kalau kami bikin konten viral, mau kasih porsi spesial full topping gratis buat tim kami?",
        "optA": {"label": "Gas! Kasih porsi Sultan gratis (Biaya Rp 150rb)", "cash": -150000, "rep": 22, "shield": False, "reply": "GILA ENAK BANGET! Video langsung masuk Trending #1!"},
        "optB": {"label": "Bayar normal saja ya Kak", "cash": 50000, "rep": 2, "shield": False, "reply": "Oke deh, kami bayar normal dan review seadanya ya."}
    },
    {
        "id": "bikers",
        "name": "Mas Bro Dimas",
        "role": "Ketua Komunitas Motor Malam",
        "avatar": "🏍️",
        "dialog": "Bro, 35 motor rombongan kami baru kelar night ride. Kalau dikasih diskon rombongan, kami langsung borong semua minuman & makanan!",
        "optA": {"label": "Terima Borongan Rombongan (+Rp 850rb, +8⭐)", "cash": 850000, "rep": 8, "shield": False, "reply": "Solid! Minggu depan kami mampir bawa pasukan lebih banyak!"},
        "optB": {"label": "Tutup lebih awal, capek banget", "cash": 0, "rep": -2, "shield": False, "reply": "Siap bro, kami cari warung sebelah dulu."}
    }
]

# Event Harian & Spesial
EVENTS = [
    {"title": "FESTIVAL KULINER NUSANTARA!", "desc": "Pemkot gelar pesta kuliner malam! Pengunjung membludak 2x lipat!", "effect": "special", "mult": 1.9, "cash": 1200000, "rep": 20, "type": "special"},
    {"title": "MALAM TAHUN BARU / LIBUR PANJANG!", "desc": "Wisatawan memadati kota, semua pesanan ludes dalam sekejap!", "effect": "special", "mult": 2.1, "cash": 1500000, "rep": 15, "type": "special"},
    {"title": "Orderan Ojol Meledak Saat Hujan!", "desc": "Hujan turun deras, pembeli dine-in sepi tapi aplikasi online banjir order!", "effect": "rain_boom", "mult": 1.25, "cash": 300000, "rep": 5, "type": "good"},
    {"title": "Sidak Ketertiban Satpol PP", "desc": "Ada penertiban trotoar malam ini!", "effect": "satpol", "value": -450000, "type": "bad"},
    {"title": "Harga Cabai & Minyak Meroket", "desc": "Pasokan pasar menipis, biaya bahan membengkak.", "effect": "cash", "value": -300000, "type": "bad"},
    {"title": "Ulasan Bintang 5 Viral di X / Twitter", "desc": "Netizen memuji sambal bawang dan porsi bar-bar warungmu!", "effect": "rep_cash", "rep": 14, "cash": 500000, "type": "good"}
]

HTML_APP = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juragan Kuliner Malam: Play Store Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap');
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #060a12; color: #f1f5f9; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glass { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(51, 65, 85, 0.75); }
        @keyframes floatBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        .float-anim { animation: floatBounce 1.2s infinite ease-in-out; }
    </style>
</head>
<body class="min-h-screen">

    <!-- ==================== MODAL 1: PELANGGAN VIP DIALOG ==================== -->
    <div id="vip-modal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="glass max-w-md w-full rounded-3xl p-6 border-2 border-amber-400 space-y-4">
            <div class="flex items-center gap-3">
                <div id="vip-avatar" class="text-4xl bg-slate-800 p-3 rounded-2xl border border-amber-500/40">👨‍💼</div>
                <div>
                    <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-amber-400 text-slate-950">TAMU VIP DATANG!</span>
                    <h3 id="vip-name" class="text-lg font-extrabold text-white mt-0.5">Pak RT</h3>
                    <p id="vip-role" class="text-xs text-slate-400">Tokoh Masyarakat</p>
                </div>
            </div>
            <div class="p-4 rounded-2xl bg-slate-900 border border-slate-700 text-sm text-slate-200 italic leading-relaxed">
                "<span id="vip-dialog">...</span>"
            </div>
            <div class="space-y-2">
                <button id="vip-btn-a" class="w-full py-3 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs text-left transition"></button>
                <button id="vip-btn-b" class="w-full py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs text-left transition"></button>
            </div>
        </div>
    </div>

    <!-- ==================== MODAL 2: EVENT SPESIAL LAYAR PENUH ==================== -->
    <div id="special-modal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
        <div class="max-w-md w-full rounded-3xl p-8 bg-gradient-to-br from-amber-900 via-slate-900 to-rose-950 border-2 border-amber-400 text-center space-y-4 shadow-2xl">
            <span class="px-3 py-1 rounded-full bg-amber-400 text-slate-950 font-extrabold text-xs">🎉 EVENT SPESIAL NUSANTARA 🎉</span>
            <h2 id="sp-title" class="text-2xl font-extrabold text-white">FESTIVAL KULINER!</h2>
            <p id="sp-desc" class="text-sm text-amber-100"></p>
            <div id="sp-reward" class="p-3 rounded-xl bg-black/40 border border-amber-400/40 mono text-sm font-bold text-emerald-400"></div>
            <button onclick="document.getElementById('special-modal').classList.add('hidden')" class="w-full py-3.5 bg-amber-400 text-slate-950 font-extrabold rounded-xl text-sm">
                MANTAP! LANJUTKAN →
            </button>
        </div>
    </div>

    <!-- ==================== MODAL 3: DAILY LOGIN REWARD ==================== -->
    <div id="daily-modal" class="hidden fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
        <div class="glass max-w-sm w-full rounded-3xl p-6 border-amber-400 text-center space-y-4">
            <div class="text-4xl">🎁</div>
            <h2 class="text-xl font-extrabold text-amber-400">Absen Harian Juragan!</h2>
            <p class="text-xs text-slate-300">Klaim suntikan modal & reputasi harianmu sebelum membuka lapak.</p>
            <div class="p-3 rounded-xl bg-slate-900 border border-amber-500/30 mono text-xs space-y-1">
                <p class="text-emerald-400 font-bold">+ Rp 400.000 Modal Kas</p>
                <p class="text-amber-400 font-bold">+ 5 ⭐ Reputasi</p>
                <p id="daily-streak" class="text-sky-400">Login Ke-1</p>
            </div>
            <button onclick="claimDaily()" class="w-full py-3 bg-emerald-500 text-slate-950 font-extrabold rounded-xl text-sm">KLAIM SEKARANG</button>
        </div>
    </div>

    <!-- ==================== SCREEN 1: AUTH / LOGIN ==================== -->
    <div id="auth-screen" class="min-h-screen flex items-center justify-center p-4">
        <div class="glass max-w-md w-full p-8 rounded-3xl space-y-5 border-amber-500/30">
            <div class="text-center space-y-1">
                <span class="px-3 py-1 rounded-full text-[10px] font-extrabold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                    🏆 PLAY STORE EDITION • MINI-GAME & VIP STORY
                </span>
                <h1 class="text-3xl font-extrabold text-white">JURAGAN <span class="text-amber-400">KULINER</span></h1>
                <p class="text-xs text-slate-400">Kelola warung, layani rush-hour, gacha resep rahasia & kuasai Nusantara!</p>
            </div>

            <div class="grid grid-cols-2 bg-slate-900 p-1 rounded-xl">
                <button id="tab-login" onclick="switchAuth('login')" class="py-2 text-xs font-bold rounded-lg bg-amber-500 text-slate-950">Masuk Akun</button>
                <button id="tab-reg" onclick="switchAuth('reg')" class="py-2 text-xs font-bold rounded-lg text-slate-400">Daftar Baru</button>
            </div>

            <form onsubmit="handleAuth(event)" class="space-y-3">
                <input type="text" id="auth-user" required placeholder="Username Juragan (misal: Angger)"
                    class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm focus:border-amber-400 focus:outline-none">
                <input type="password" id="auth-pin" required placeholder="PIN Keamanan"
                    class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm focus:border-amber-400 focus:outline-none">

                <div id="reg-box" class="hidden space-y-3">
                    <input type="text" id="auth-brand" placeholder="Nama Warung (misal: Kedai Lelespit)"
                        class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm">
                    <select id="auth-city" class="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm">
                        {% for k, v in cities.items() %}
                        <option value="{{ k }}">{{ v.name }} — {{ v.vibe }}</option>
                        {% endfor %}
                    </select>
                </div>

                <button type="submit" id="auth-btn" class="w-full py-3.5 bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 font-extrabold rounded-xl text-sm">
                    MASUK KE LAPAK →
                </button>
            </form>

            <div id="saved-box" class="hidden border-t border-slate-800 pt-3">
                <p class="text-[11px] text-slate-400 mb-2">Akun Tersimpan:</p>
                <div id="saved-list" class="flex flex-wrap gap-2"></div>
            </div>
        </div>
    </div>

    <!-- ==================== SCREEN 2: GAMEPLAY ==================== -->
    <div id="game-screen" class="hidden pb-16">
        
        <!-- Top Navbar -->
        <header class="glass sticky top-0 z-40 border-b border-slate-800">
            <div class="max-w-7xl mx-auto px-4 py-2.5 flex flex-wrap justify-between items-center gap-2">
                <div class="flex items-center gap-2.5">
                    <div class="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-lg">🔥</div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h1 id="ui-brand" class="font-extrabold text-sm md:text-base text-white">Warung</h1>
                            <span id="ui-city" class="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">Kota</span>
                            <span id="ui-shield" class="hidden text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">🛡️ Aman Satpol PP</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Juragan: <b id="ui-user" class="text-amber-400">User</b> • Prestige Lv.<span id="ui-prestige">0</span></p>
                    </div>
                </div>

                <!-- Jam, Cuaca & Kalender -->
                <div class="flex items-center gap-3 bg-slate-950 px-3.5 py-1.5 rounded-xl border border-slate-800">
                    <div>
                        <p id="ui-cal" class="text-[11px] font-bold text-slate-200">Senin, Hari ke-1</p>
                        <p id="ui-weather" class="mono text-[11px] text-sky-400 font-bold">🌙 Malam Cerah • 18:00 WIB</p>
                    </div>
                </div>

                <!-- Audio & Logout -->
                <div class="flex items-center gap-2">
                    <button onclick="toggleAudio()" class="px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs font-bold">
                        <span id="audio-icon">🔇</span> <span id="audio-text">BGM Off</span>
                    </button>
                    <button onclick="location.reload()" class="px-3 py-1.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/30 text-xs font-bold">Keluar</button>
                </div>
            </div>
        </header>

        <main class="max-w-7xl mx-auto px-4 mt-4 space-y-4">

            <!-- LIVE INTERACTIVE CANVAS (MINI-GAME TAP PESANAN + ANIMASI JALANAN) -->
            <div class="glass rounded-2xl overflow-hidden border border-slate-700 relative">
                <div class="absolute top-3 left-3 z-10 flex flex-wrap items-center gap-2">
                    <span id="canvas-badge" class="px-3 py-1 rounded-lg bg-slate-950/85 border border-slate-700 text-xs font-bold text-amber-300">
                        🌃 Suasana Jalanan Nusantara
                    </span>
                    <span id="combo-badge" class="hidden px-3 py-1 rounded-lg bg-rose-600 text-white text-xs font-extrabold animate-bounce">
                        🔥 COMBO x0! Klik Pesanan!
                    </span>
                </div>
                <canvas id="streetCanvas" class="w-full h-60 md:h-64 block cursor-pointer"></canvas>
            </div>

            <!-- 4 Metrik Utama -->
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <div class="glass p-4 rounded-2xl border-l-4 border-l-emerald-400">
                    <p class="text-[11px] text-slate-400">Saldo Kas Bisnis</p>
                    <p id="stat-cash" class="mono text-lg md:text-xl font-extrabold text-emerald-400">Rp 0</p>
                </div>
                <div class="glass p-4 rounded-2xl border-l-4 border-l-amber-400">
                    <p class="text-[11px] text-slate-400">Reputasi & Rating</p>
                    <p id="stat-rep" class="mono text-lg md:text-xl font-extrabold text-amber-400">25 ⭐</p>
                </div>
                <div class="glass p-4 rounded-2xl border-l-4 border-l-sky-400">
                    <p class="text-[11px] text-slate-400">Bangunan & Dekorasi</p>
                    <p id="stat-tent" class="text-base md:text-lg font-extrabold text-sky-400">Tenda Terpal</p>
                </div>
                <div class="glass p-4 rounded-2xl border-l-4 border-l-purple-400">
                    <p class="text-[11px] text-slate-400">Gurita Cabang</p>
                    <p id="stat-branch" class="mono text-lg md:text-xl font-extrabold text-purple-400">0 Cabang</p>
                </div>
            </div>

            <!-- TAB NAVIGASI FITUR PLAY STORE -->
            <div class="flex flex-wrap gap-2 bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800">
                <button onclick="switchMainTab('ops')" id="mtab-ops" class="px-4 py-2 rounded-xl text-xs font-extrabold bg-amber-500 text-slate-950">🍳 Operasional & Ojol</button>
                <button onclick="switchMainTab('gacha')" id="mtab-gacha" class="px-4 py-2 rounded-xl text-xs font-extrabold text-slate-300 hover:bg-slate-800">🎁 Gacha Resep Rahasia</button>
                <button onclick="switchMainTab('decor')" id="mtab-decor" class="px-4 py-2 rounded-xl text-xs font-extrabold text-slate-300 hover:bg-slate-800">✨ Toko Dekorasi & Fasilitas</button>
                <button onclick="switchMainTab('rank')" id="mtab-rank" class="px-4 py-2 rounded-xl text-xs font-extrabold text-slate-300 hover:bg-slate-800">🏆 Leaderboard & Prestige</button>
            </div>

            <!-- GRID KONTEN UTAMA -->
            <div class="grid lg:grid-cols-12 gap-5">
                
                <!-- PANEL KIRI (5 Kolom - Berubah sesuai Tab) -->
                <div class="lg:col-span-5">
                    
                    <!-- TAB 1: OPERASIONAL -->
                    <div id="panel-ops" class="glass p-5 rounded-2xl space-y-4">
                        <h2 class="text-sm font-extrabold text-white border-b border-slate-800 pb-2">🍳 Persiapan Jualan Malam Ini</h2>
                        
                        <div>
                            <label class="block text-xs font-bold text-slate-300 mb-1">1. Menu Andalan (Buka lebih banyak di Gacha!)</label>
                            <select id="select-menu" onchange="updatePreview()" class="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-bold text-white"></select>
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-slate-900 p-3 rounded-xl border border-slate-800">
                                <div class="flex justify-between text-[11px]">
                                    <span class="text-slate-400">Stok Porsi</span>
                                    <span id="prev-stock" class="mono font-bold">60</span>
                                </div>
                                <input type="range" id="in-stock" min="20" max="500" step="10" value="60" class="w-full accent-amber-400 my-1" oninput="updatePreview()">
                                <p class="text-[10px] text-rose-400 mono">Modal: <span id="prev-cost">Rp 0</span></p>
                            </div>
                            <div class="bg-slate-900 p-3 rounded-xl border border-slate-800">
                                <div class="flex justify-between text-[11px]">
                                    <span class="text-slate-400">Harga Jual</span>
                                    <span id="prev-price" class="mono font-bold text-emerald-400">Rp 18.000</span>
                                </div>
                                <input type="range" id="in-price" min="10000" max="75000" step="1000" value="18000" class="w-full accent-emerald-400 my-1" oninput="updatePreview()">
                                <p id="prev-sent" class="text-[10px] text-amber-300 font-bold">Harga Pas</p>
                            </div>
                        </div>

                        <!-- Aplikasi Online -->
                        <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-2">
                            <p class="text-xs font-bold text-white">🛵 Aplikasi Pesan Antar Online (Laris Saat Hujan!)</p>
                            <div class="grid grid-cols-3 gap-2 text-[11px]">
                                <label class="p-2 rounded-lg bg-slate-950 border border-emerald-500/40 flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" id="app-go" checked class="accent-emerald-500"><b class="text-emerald-400">GoFood</b>
                                </label>
                                <label class="p-2 rounded-lg bg-slate-950 border border-green-500/40 flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" id="app-grab" class="accent-green-500"><b class="text-green-400">GrabFood</b>
                                </label>
                                <label class="p-2 rounded-lg bg-slate-950 border border-orange-500/40 flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" id="app-shopee" class="accent-orange-500"><b class="text-orange-400">ShopeeFood</b>
                                </label>
                            </div>
                        </div>

                        <button onclick="startRushHourShift()" id="btn-open"
                            class="w-full py-3.5 bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500 hover:brightness-110 text-slate-950 font-extrabold rounded-xl text-xs md:text-sm shadow-lg">
                            🚀 BUKA LAPAK (MAIN RUSH-HOUR 8 DETIK!)
                        </button>
                    </div>

                    <!-- TAB 2: GACHA RESEP RAHASIA -->
                    <div id="panel-gacha" class="hidden glass p-5 rounded-2xl space-y-4">
                        <div class="text-center space-y-2 bg-gradient-to-b from-purple-900/40 to-slate-900 p-5 rounded-2xl border border-purple-500/40">
                            <div class="text-4xl float-anim">📦✨</div>
                            <h3 class="text-base font-extrabold text-amber-400">Peti Riset Resep Rahasia</h3>
                            <p class="text-xs text-slate-300">Buka resep kuliner langka Nusantara dengan harga jual Sultan!</p>
                            <button onclick="rollGachaRecipe()" class="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white font-extrabold rounded-xl text-xs shadow-lg">
                                🎲 BUKA PETI RESEP (Rp 1.500.000)
                            </button>
                        </div>
                        <div class="space-y-2">
                            <p class="text-xs font-bold text-slate-300">Koleksi Buku Resepmu:</p>
                            <div id="recipe-book-list" class="grid grid-cols-1 gap-2 max-h-56 overflow-y-auto text-xs"></div>
                        </div>
                    </div>

                    <!-- TAB 3: TOKO DEKORASI LIVE -->
                    <div id="panel-decor" class="hidden glass p-5 rounded-2xl space-y-3">
                        <h3 class="text-sm font-extrabold text-sky-400">✨ Toko Dekorasi & Fasilitas Live</h3>
                        <p class="text-[11px] text-slate-400">Barang yang dibeli langsung muncul di gambar warungmu & menambah pembeli!</p>
                        <div id="decor-shop-list" class="space-y-2.5 text-xs"></div>
                    </div>

                    <!-- TAB 4: LEADERBOARD & PRESTIGE -->
                    <div id="panel-rank" class="hidden glass p-5 rounded-2xl space-y-4">
                        <h3 class="text-sm font-extrabold text-amber-400">🏆 Top Juragan Kuliner Indonesia</h3>
                        <div id="leaderboard-list" class="space-y-2 text-xs"></div>
                        <div class="p-4 rounded-2xl bg-indigo-950/60 border border-indigo-500/40 space-y-2">
                            <p class="text-xs font-extrabold text-indigo-300">✈️ Ekspansi Lintas Provinsi (Prestige)</p>
                            <p class="text-[11px] text-slate-300">Butuh kas minimal <b>Rp 25.000.000</b> untuk membuka pusat kuliner baru dengan bonus permanen +25% omzet!</p>
                            <button onclick="doPrestige()" class="w-full py-2.5 bg-indigo-500 hover:bg-indigo-400 text-slate-950 font-extrabold rounded-xl text-xs">
                                NAIK TINGKAT PRESTIGE (Rp 25 Juta)
                            </button>
                        </div>
                    </div>

                </div>

               <!-- PANEL TENGAH (4 Kolom): Grafik & Laporan Malam -->
                <div class="lg:col-span-4 space-y-4">
                    <div class="glass p-4 rounded-2xl">
                        <h3 class="text-xs font-extrabold text-white mb-2">📈 Grafik Omzet & Profit Bersih</h3>
                        <div class="h-44"><canvas id="financeChart"></canvas></div>
                    </div>

                    <div class="glass p-4 rounded-2xl border-l-4 border-l-amber-400 space-y-2.5">
                        <div class="flex justify-between items-center">
                            <h3 class="text-xs font-extrabold text-amber-400">🧾 Laporan Tutup Warung</h3>
                            <span id="res-day" class="mono text-[10px] text-slate-400">Hari ke-1</span>
                        </div>
                        <div id="event-banner" class="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300">
                            Saat klik <b>Buka Lapak</b>, klik gelembung pesanan di atas kepala pembeli & ojol untuk bonus Combo!
                        </div>
                        <div id="res-metrics" class="hidden grid grid-cols-3 gap-2 text-[11px]">
                            <div class="bg-slate-900 p-2 rounded-lg"><span class="text-slate-400 block text-[10px]">Dine-In</span><b id="res-dine" class="mono">0</b></div>
                            <div class="bg-slate-900 p-2 rounded-lg"><span class="text-slate-400 block text-[10px]">Ojol</span><b id="res-ojol" class="mono text-emerald-400">0</b></div>
                            <div class="bg-slate-900 p-2 rounded-lg"><span class="text-slate-400 block text-[10px]">Profit</span><b id="res-prof" class="mono text-amber-400">Rp 0</b></div>
                        </div>
                    </div>
                </div>

                <!-- PANEL KANAN (3 Kolom): Quest & Upgrade Timer -->
                <div class="lg:col-span-3 space-y-4">
                    <div class="glass p-4 rounded-2xl space-y-2.5">
                        <h3 class="text-xs font-extrabold text-amber-400">🎯 Quest & Side Quest</h3>
                        <div id="quest-list" class="space-y-2 text-xs"></div>
                    </div>

                    <div class="glass p-4 rounded-2xl space-y-2.5">
                        <h3 class="text-xs font-extrabold text-sky-400">🏗️ Renovasi & Tim (Timer)</h3>
                        <div id="const-box" class="hidden p-2.5 rounded-xl bg-amber-500/15 border border-amber-500/40 text-xs space-y-1">
                            <div class="flex justify-between font-bold text-amber-300"><span id="const-name">Renovasi</span><span id="const-time" class="mono">10d</span></div>
                            <div class="w-full bg-slate-800 h-1.5 rounded-full"><div id="const-bar" class="bg-amber-400 h-full" style="width:0%"></div></div>
                        </div>
                        <button onclick="startUpgrade('tent', 12)" class="w-full p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-left flex justify-between items-center text-xs">
                            <div><b>Upgrade Bangunan</b><span class="block text-[10px] text-slate-400">12 detik • +Reputasi</span></div>
                            <span id="cost-tent" class="mono font-bold text-sky-400">Rp 2.5jt</span>
                        </button>
                        <button onclick="startUpgrade('staff', 10)" class="w-full p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-left flex justify-between items-center text-xs">
                            <div><b>Rekrut Koki Baru</b><span class="block text-[10px] text-slate-400">10 detik • +Kapasitas</span></div>
                            <span id="cost-staff" class="mono font-bold text-emerald-400">Rp 3.5jt</span>
                        </button>
                        <button onclick="startUpgrade('branch', 20)" class="w-full p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-left flex justify-between items-center text-xs">
                            <div><b>Buka Cabang Baru</b><span class="block text-[10px] text-slate-400">20 detik • +Rp 500rb/mlm</span></div>
                            <span id="cost-branch" class="mono font-bold text-purple-400">Rp 8.0jt</span>
                        </button>
                    </div>
                </div>

            </div>
        </main>
    </div>
    <script>
        // ==================== DATA MASTER ====================
        const CITIES_DATA = {{ cities | tojson }};
        const MENUS_DATA = {{ menus | tojson }};
        const VIP_DATA = {{ vips | tojson }};
        const DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu (Malam Minggu)", "Minggu"];
        const TENT_TIERS = ["Tenda Terpal", "Tenda Rangka Besi", "Warung Semi-Permanen", "Ruko 2 Lantai", "Resto Legendaris"];

        const DECOR_ITEMS = [
            { id: "neon", name: "Spanduk Neon Box Menyala", cost: 1200000, bonusText: "+15% Pembeli Malam", rep: 8 },
            { id: "tv", name: "TV Layar Lebar (Nobar Bola)", cost: 2500000, bonusText: "+25% Betah Dine-In", rep: 14 },
            { id: "gerobak", name: "Gerobak Kayu Jati Ukiran", cost: 3200000, bonusText: "+20% Harga Ideal", rep: 18 }
        ];

        const QUESTS = [
            { id: "q1", title: "Bintang Kampung", desc: "Capai Reputasi 50 ⭐", type: "rep", val: 50, cash: 1000000, rep: 10 },
            { id: "q2", title: "Kolektor Resep", desc: "Miliki minimal 4 Resep Menu", type: "recipes", val: 4, cash: 1500000, rep: 12 },
            { id: "q3", title: "Juragan Muda", desc: "Kumpulkan Kas Rp 10.000.000", type: "cash", val: 10000000, cash: 2500000, rep: 15 },
            { id: "q4", title: "Gurita Kuliner", desc: "Buka 1 Cabang Franchise", type: "branch", val: 1, cash: 4000000, rep: 20 }
        ];

        let currentUser = null, gameState = null, authMode = 'login';
        let isRaining = false, rushHourActive = false, rushCombo = 0;

        // ==================== CANVAS & MINI-GAME RUSH HOUR ====================
        const canvas = document.getElementById('streetCanvas');
        const ctx = canvas.getContext('2d');
        let vehicles = [], pedestrians = [], raindrops = [], orderBubbles = [], wind = 0;

        function initCanvas() {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            raindrops = Array.from({length: 70}, () => ({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, l: Math.random() * 12 + 8 }));
            vehicles = [
                { x: -60, y: canvas.height - 36, s: 2.5, type: 'ojol_go', color: '#10b981' },
                { x: 240, y: canvas.height - 24, s: -2.0, type: 'car', color: '#38bdf8' },
                { x: 480, y: canvas.height - 36, s: 2.8, type: 'ojol_shopee', color: '#f97316' }
            ];
            pedestrians = [
                { x: 80, y: canvas.height - 54, s: 0.7, color: '#f59e0b' },
                { x: 320, y: canvas.height - 54, s: -0.6, color: '#a855f7' },
                { x: 520, y: canvas.height - 54, s: -0.8, color: '#ec4899' }
            ];
        }

        // Klik gelembung pesanan saat Rush Hour!
        canvas.addEventListener('click', (e) => {
            if (!rushHourActive) return;
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            for (let i = orderBubbles.length - 1; i >= 0; i--) {
                const b = orderBubbles[i];
                if (Math.hypot(mx - b.x, my - b.y) < 34) {
                    orderBubbles.splice(i, 1);
                    rushCombo++;
                    document.getElementById('combo-badge').innerText = `🔥 COMBO x${rushCombo}! (+Rp ${(rushCombo * 50)}rb)`;
                    playSFX('coin');
                    break;
                }
            }
        });

        function renderCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            wind += 0.03;
            const sway = Math.sin(wind) * 5;
            const sideY = canvas.height - 46;

            // Langit
            ctx.fillStyle = isRaining ? '#070b14' : '#0b1324';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Bulan (tertutup awan jika hujan)
            if (!isRaining) {
                ctx.fillStyle = '#fef08a';
                ctx.beginPath(); ctx.arc(canvas.width - 65, 38, 15, 0, Math.PI * 2); ctx.fill();
            }

            // Pohon Bergerak
            [70, canvas.width - 80].forEach((tx, idx) => {
                ctx.fillStyle = '#3f2e21'; ctx.fillRect(tx - 5, sideY - 50, 10, 50);
                ctx.fillStyle = '#064e3b';
                ctx.beginPath(); ctx.arc(tx + (idx === 0 ? sway : -sway), sideY - 62, 28, 0, Math.PI * 2); ctx.fill();
            });

            // Warung & Dekorasi Live
            const cx = canvas.width / 2;
            const lvl = gameState ? gameState.tentLevel : 1;
            const decors = gameState ? (gameState.decors || []) : [];
            const w = 135 + lvl * 16;
            const h = 68 + lvl * 3;
            const left = cx - w / 2, top = sideY - h;

            // Cahaya Neon Box jika sudah dibeli
            if (decors.includes('neon')) {
                const grad = ctx.createRadialGradient(cx, top + 25, 10, cx, top + 25, w);
                grad.addColorStop(0, 'rgba(245, 158, 11, 0.45)');
                grad.addColorStop(1, 'rgba(245, 158, 11, 0)');
                ctx.fillStyle = grad; ctx.fillRect(left - 50, top - 25, w + 100, h + 30);
            }
             // Tenda Utama
            ctx.fillStyle = lvl >= 3 ? '#1e293b' : '#1d4ed8';
            ctx.fillRect(left, top + 16, w, h - 16);
            ctx.fillStyle = decors.includes('neon') ? '#f59e0b' : '#2563eb';
            ctx.beginPath();
            ctx.moveTo(left - 8, top + 16); ctx.lineTo(left + 8, top);
            ctx.lineTo(left + w - 8, top); ctx.lineTo(left + w + 8, top + 16);
            ctx.fill();

            // Spanduk Nama Warung
            ctx.fillStyle = '#fef08a'; ctx.fillRect(left + 12, top + 20, w - 24, 15);
            ctx.fillStyle = '#991b1b'; ctx.font = 'bold 10px sans-serif'; ctx.textAlign = 'center';
            ctx.fillText((gameState ? gameState.brand : "WARUNG").toUpperCase().slice(0, 18), cx, top + 31);

            // TV Nobar Bola jika dibeli
            if (decors.includes('tv')) {
                ctx.fillStyle = '#0f172a'; ctx.fillRect(left + 14, top + 40, 24, 15);
                ctx.fillStyle = '#22c55e'; ctx.fillRect(left + 16, top + 42, 20, 11);
            }

            // Gerobak (Kayu Jati jika dibeli)
            ctx.fillStyle = decors.includes('gerobak') ? '#78350f' : '#92400e';
            ctx.fillRect(cx - 32, sideY - 26, 64, 26);

            // Trotoar & Aspal
            ctx.fillStyle = '#334155'; ctx.fillRect(0, sideY, canvas.width, 7);
            ctx.fillStyle = '#1e293b'; ctx.fillRect(0, sideY + 7, canvas.width, 40);

            // Pejalan Kaki (Pakai Payung jika Hujan!)
            const speedMult = rushHourActive ? 2.4 : 1;
            pedestrians.forEach(p => {
                p.x += p.s * speedMult;
                if (p.x > canvas.width + 20) p.x = -20;
                if (p.x < -20) p.x = canvas.width + 20;

                ctx.fillStyle = '#fde68a'; ctx.beginPath(); ctx.arc(p.x, sideY - 20, 4, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = p.color; ctx.fillRect(p.x - 4, sideY - 15, 8, 11);

                if (isRaining) {
                    ctx.fillStyle = '#f43f5e';
                    ctx.beginPath(); ctx.arc(p.x, sideY - 27, 11, Math.PI, 0); ctx.fill();
                }
            });

            // Kendaraan & Ojol
            vehicles.forEach(v => {
                v.x += v.s * speedMult;
                if (v.x > canvas.width + 80) v.x = -80;
                if (v.x < -80) v.x = canvas.width + 80;
                ctx.fillStyle = v.color;
                ctx.fillRect(v.x, v.y - 11, v.type === 'car' ? 42 : 22, 10);
                ctx.fillStyle = '#000';
                ctx.beginPath(); ctx.arc(v.x + 5, v.y, 4, 0, Math.PI * 2); ctx.arc(v.x + (v.type === 'car' ? 34 : 17), v.y, 4, 0, Math.PI * 2); ctx.fill();
            });

            // Efek Hujan Visual
            if (isRaining) {
                ctx.strokeStyle = 'rgba(148, 163, 184, 0.55)';
                ctx.lineWidth = 1.2;
                raindrops.forEach(r => {
                    r.y += 7; r.x -= 1.5;
                    if (r.y > canvas.height) { r.y = 0; r.x = Math.random() * canvas.width; }
                    ctx.beginPath(); ctx.moveTo(r.x, r.y); ctx.lineTo(r.x - 2, r.y + r.l); ctx.stroke();
                });
            }

            // Gelembung Pesanan Mini-Game Rush Hour
            orderBubbles.forEach(b => {
                b.y += Math.sin(wind * 3 + b.x) * 0.4;
                ctx.fillStyle = '#fef08a';
                ctx.beginPath(); ctx.roundRect(b.x - 36, b.y - 16, 72, 26, 8); ctx.fill();
                ctx.strokeStyle = '#f59e0b'; ctx.lineWidth = 2; ctx.stroke();
                ctx.fillStyle = '#0f172a'; ctx.font = 'bold 10px sans-serif'; ctx.textAlign = 'center';
                ctx.fillText(b.text, b.x, b.y);
            });

            requestAnimationFrame(renderCanvas);
        }
         // ==================== AUDIO SYNTH ====================
        let audioCtx = null, bgmInt = null, audioOn = false;
        function toggleAudio() {
            audioOn = !audioOn;
            document.getElementById('audio-icon').innerText = audioOn ? "🔊" : "🔇";
            document.getElementById('audio-text').innerText = audioOn ? "BGM On" : "BGM Off";
            if (audioOn) {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') audioCtx.resume();
                const chords = [[146.83, 174.61, 220], [110, 130.81, 164.81], [116.54, 146.83, 174.61], [110, 138.59, 164.81]];
                let s = 0;
                const play = () => {
                    if (!audioOn) return;
                    const now = audioCtx.currentTime;
                    chords[s % 4].forEach(f => {
                        const o = audioCtx.createOscillator(), g = audioCtx.createGain();
                        o.type = 'triangle'; o.frequency.setValueAtTime(f, now);
                        g.gain.setValueAtTime(0.001, now); g.gain.exponentialRampToValueAtTime(0.02, now + 0.6); g.gain.exponentialRampToValueAtTime(0.0008, now + 3.5);
                        o.connect(g); g.connect(audioCtx.destination); o.start(now); o.stop(now + 3.6);
                    });
                    s++;
                };
                play(); bgmInt = setInterval(play, 3800);
            } else if (bgmInt) clearInterval(bgmInt);
        }

        function playSFX(t) {
            if (!audioOn || !audioCtx) return;
            const now = audioCtx.currentTime, o = audioCtx.createOscillator(), g = audioCtx.createGain();
            o.type = t === 'alert' ? 'sawtooth' : 'sine';
            o.frequency.setValueAtTime(t === 'coin' ? 1046 : 180, now);
            if (t === 'coin') o.frequency.setValueAtTime(1318, now + 0.08);
            g.gain.setValueAtTime(0.06, now); g.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
            o.connect(g); g.connect(audioCtx.destination); o.start(now); o.stop(now + 0.3);
        }

        // ==================== AUTH & SAVE ====================
        function getDB() { return JSON.parse(localStorage.getItem('jkm_playstore_v3') || '{}'); }
        function saveDB(db) { localStorage.setItem('jkm_playstore_v3', JSON.stringify(db)); }
        function persist() { const db = getDB(); db[currentUser] = gameState; saveDB(db); }

        function switchAuth(m) {
            authMode = m;
            document.getElementById('reg-box').classList.toggle('hidden', m === 'login');
            document.getElementById('tab-login').className = m === 'login' ? "py-2 text-xs font-bold rounded-lg bg-amber-500 text-slate-950" : "py-2 text-xs font-bold rounded-lg text-slate-400";
            document.getElementById('tab-reg').className = m === 'reg' ? "py-2 text-xs font-bold rounded-lg bg-amber-500 text-slate-950" : "py-2 text-xs font-bold rounded-lg text-slate-400";
        }

        function renderSaved() {
            const users = Object.keys(getDB());
            if (users.length) {
                document.getElementById('saved-box').classList.remove('hidden');
                document.getElementById('saved-list').innerHTML = users.map(u => `<button type="button" onclick="document.getElementById('auth-user').value='${u}';switchAuth('login')" class="text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-amber-300 font-bold">👤 ${u}</button>`).join('');
            }
        }

        function handleAuth(e) {
            e.preventDefault();
            const u = document.getElementById('auth-user').value.trim();
            const pin = document.getElementById('auth-pin').value.trim();
            const db = getDB();

            if (authMode === 'reg') {
                if (db[u]) return alert("Username sudah terdaftar!");
                db[u] = {
                    username: u, pin: pin,
                    brand: document.getElementById('auth-brand').value.trim() || `Warung ${u}`,
                    city: document.getElementById('auth-city').value,
                    day: 1, cash: 2500000, reputation: 25,
                    tentLevel: 1, staffLevel: 1, branches: 0, prestige: 0,
                    unlockedMenus: ["lele", "nasgor"],
                    decors: [], claimedQuests: [], satpolShield: false,
                    lastLogin: "", streak: 0,
                    history: [{ day: "Awal", revenue: 0, profit: 0 }]
                };
                saveDB(db);
            } else if (!db[u] || db[u].pin !== pin) return alert("Username atau PIN salah!");

            currentUser = u;
            gameState = db[u];
            document.getElementById('auth-screen').classList.add('hidden');
            document.getElementById('game-screen').classList.remove('hidden');

            if (!audioOn) toggleAudio();
            initCanvas(); renderCanvas(); initChart();
            rollDailyWeather();
            updateUI();

            if (gameState.lastLogin !== new Date().toDateString()) {
                gameState.streak = (gameState.streak || 0) + 1;
                document.getElementById('daily-streak').innerText = `Login Streak Hari ke-${gameState.streak}`;
                document.getElementById('daily-modal').classList.remove('hidden');
            }
        }

        function claimDaily() {
            gameState.lastLogin = new Date().toDateString();
            gameState.cash += 400000;
            gameState.reputation += 5;
            playSFX('coin');
            document.getElementById('daily-modal').classList.add('hidden');
            persist(); updateUI();
        }
         // ==================== TABS & UI RENDER ====================
        function switchMainTab(t) {
            ['ops', 'gacha', 'decor', 'rank'].forEach(x => {
                document.getElementById(`panel-${x}`).classList.toggle('hidden', x !== t);
                document.getElementById(`mtab-${x}`).className = x === t ? "px-4 py-2 rounded-xl text-xs font-extrabold bg-amber-500 text-slate-950" : "px-4 py-2 rounded-xl text-xs font-extrabold text-slate-300 hover:bg-slate-800";
            });
        }

        function rollDailyWeather() {
            isRaining = Math.random() < 0.35;
            document.getElementById('ui-weather').innerText = isRaining ? "🌧️ Hujan Deras (Ojol Ramai!) • 18:30 WIB" : "🌙 Malam Cerah • 18:00 WIB";
        }

        function formatRp(n) { return "Rp " + Math.round(n).toLocaleString('id-ID'); }

        let chart = null;
        function initChart() {
            chart = new Chart(document.getElementById('financeChart').getContext('2d'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Omzet', data: [], borderColor: '#38bdf8', tension: 0.3 }, { label: 'Profit', data: [], borderColor: '#34d399', tension: 0.3 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#cbd5e1', font: { size: 10 } } } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 9 } } }, y: { ticks: { color: '#94a3b8', font: { size: 9 }, callback: v => (v/1000)+'k' } } } }
            });
        }

        function updateUI() {
            const city = CITIES_DATA[gameState.city];
            const dIdx = (gameState.day - 1) % 7;
            document.getElementById('ui-brand').innerText = gameState.brand;
            document.getElementById('ui-city').innerText = city.name;
            document.getElementById('ui-user').innerText = gameState.username;
            document.getElementById('ui-prestige').innerText = gameState.prestige || 0;
            document.getElementById('ui-cal').innerText = `${DAYS_ID[dIdx]}, Hari ke-${gameState.day}`;
            document.getElementById('ui-shield').classList.toggle('hidden', !gameState.satpolShield);

            document.getElementById('stat-cash').innerText = formatRp(gameState.cash);
            document.getElementById('stat-rep').innerText = `${gameState.reputation} ⭐`;
            document.getElementById('stat-tent').innerText = TENT_TIERS[Math.min(gameState.tentLevel - 1, TENT_TIERS.length - 1)];
            document.getElementById('stat-branch').innerText = `${gameState.branches} Cabang`;

            document.getElementById('cost-tent').innerText = `Rp ${(gameState.tentLevel * 2.5).toFixed(1)}jt`;
            document.getElementById('cost-staff').innerText = `Rp ${(gameState.staffLevel * 3.5).toFixed(1)}jt`;
            document.getElementById('cost-branch').innerText = `Rp ${((gameState.branches + 1) * 8).toFixed(0)}jt`;

            // Populate Menu Dropdown (Hanya menu yang sudah terbuka!)
            const sel = document.getElementById('select-menu');
            const prevVal = sel.value;
            sel.innerHTML = (gameState.unlockedMenus || ["lele", "nasgor"]).map(k => {
                const m = MENUS_DATA[k];
                return `<option value="${k}">${m.name} [${m.rarity}] (Modal Rp ${m.base_cost.toLocaleString('id-ID')})</option>`;
            }).join('');
            if (prevVal && gameState.unlockedMenus.includes(prevVal)) sel.value = prevVal;
            updatePreview();

            // Render Buku Resep Gacha
            document.getElementById('recipe-book-list').innerHTML = Object.entries(MENUS_DATA).map(([k, m]) => {
                const open = gameState.unlockedMenus.includes(k);
                return `<div class="p-2.5 rounded-xl border ${open ? 'bg-slate-900 border-amber-500/40' : 'bg-slate-950/60 border-slate-800 opacity-50'} flex justify-between items-center">
                    <div><b>${open ? m.name : '??? Resep Terkunci ???'}</b><span class="block text-[10px] text-amber-400">Tier: ${m.rarity}</span></div>
                    <span class="text-[10px] font-bold ${open ? 'text-emerald-400' : 'text-slate-500'}">${open ? '✓ Terbuka' : 'Terkunci'}</span>
                </div>`;
            }).join('');

            // Render Toko Dekorasi
            document.getElementById('decor-shop-list').innerHTML = DECOR_ITEMS.map(d => {
                const owned = (gameState.decors || []).includes(d.id);
                return `<div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
                    <div><b>${d.name}</b><span class="block text-[10px] text-emerald-400">${d.bonusText} (+${d.rep}⭐)</span></div>
                    ${owned ? '<span class="text-emerald-400 font-bold">✓ Terpasang</span>' : `<button onclick="buyDecor('${d.id}')" class="px-3 py-1.5 rounded-lg bg-sky-500 text-slate-950 font-extrabold">Rp ${(d.cost/1000000).toFixed(1)}jt</button>`}
                </div>`;
            }).join('');

            // Render Quests
            document.getElementById('quest-list').innerHTML = QUESTS.map(q => {
                const claimed = gameState.claimedQuests.includes(q.id);
                let cur = q.type === 'rep' ? gameState.reputation : (q.type === 'cash' ? gameState.cash : (q.type === 'branch' ? gameState.branches : gameState.unlockedMenus.length));
                const done = cur >= q.val;
                return `<div class="p-2.5 rounded-xl bg-slate-900 border ${done && !claimed ? 'border-amber-400' : 'border-slate-800'} flex justify-between items-center">
                    <div><b>${q.title}</b><span class="block text-[10px] text-slate-400">${q.desc}</span></div>
                    ${claimed ? '<span class="text-emerald-400 font-bold">✓</span>' : (done ? `<button onclick="claimQuest('${q.id}')" class="px-2 py-1 rounded bg-amber-400 text-slate-950 font-extrabold">Klaim</button>` : '<span class="text-slate-500">Proses</span>')}
                </div>`;
            }).join('');
            // Render Leaderboard
            const rivals = [
                { name: "Juragan Slamet (Solo)", net: 18500000 },
                { name: "Sultan Pecel Madiun", net: 42000000 },
                { name: "Raja Seafood Pantura", net: 95000000 },
                { name: `${gameState.brand} (Kamu)`, net: gameState.cash + (gameState.branches * 8000000), isMe: true }
            ].sort((a, b) => b.net - a.net);

            document.getElementById('leaderboard-list').innerHTML = rivals.map((r, i) => `
                <div class="p-2.5 rounded-xl ${r.isMe ? 'bg-amber-500/20 border border-amber-400' : 'bg-slate-900'} flex justify-between">
                    <span><b>#${i+1}</b> ${r.name}</span>
                    <span class="mono font-bold text-emerald-400">${formatRp(r.net)}</span>
                </div>`).join('');

            const rec = gameState.history.slice(-7);
            chart.data.labels = rec.map(r => r.day);
            chart.data.datasets[0].data = rec.map(r => r.revenue);
            chart.data.datasets[1].data = rec.map(r => r.profit);
            chart.update();
        }

        function updatePreview() {
            const mKey = document.getElementById('select-menu').value || 'lele';
            const m = MENUS_DATA[mKey];
            const mult = CITIES_DATA[gameState.city].cost_mult;
            const st = parseInt(document.getElementById('in-stock').value);
            const pr = parseInt(document.getElementById('in-price').value);
            document.getElementById('prev-stock').innerText = `${st} Porsi`;
            document.getElementById('prev-cost').innerText = formatRp(Math.round(m.base_cost * mult) * st);
            document.getElementById('prev-price').innerText = formatRp(pr);
            document.getElementById('prev-sent').innerText = pr <= m.ideal_price * 1.15 ? "Harga Ideal" : "Agak Mahal";
        }

        // ==================== FITUR INTERAKTIF: GACHA, DEKOR, PRESTIGE, VIP ====================
        function rollGachaRecipe() {
            if (gameState.cash < 1500000) return alert("Kas tidak cukup (Butuh Rp 1.500.000)!");
            const locked = Object.keys(MENUS_DATA).filter(k => !gameState.unlockedMenus.includes(k));
            if (!locked.length) return alert("Semua Resep Legendaris Nusantara sudah kamu kuasai!");
            gameState.cash -= 1500000;
            const got = locked[Math.floor(Math.random() * locked.length)];
            gameState.unlockedMenus.push(got);
            playSFX('coin');
            alert(`🎉 SELAMAT! Kamu menemukan Resep Rahasia: ${MENUS_DATA[got].name} [${MENUS_DATA[got].rarity}]!`);
            persist(); updateUI();
        }

        function buyDecor(id) {
            const item = DECOR_ITEMS.find(d => d.id === id);
            if (gameState.cash < item.cost) return alert("Saldo kas belum cukup!");
            gameState.cash -= item.cost;
            gameState.decors.push(id);
            gameState.reputation += item.rep;
            playSFX('coin');
            persist(); updateUI();
        }

        function claimQuest(id) {
            const q = QUESTS.find(x => x.id === id);
            gameState.claimedQuests.push(id);
            gameState.cash += q.cash;
            gameState.reputation += q.rep;
            playSFX('coin');
            persist(); updateUI();
        }

        function doPrestige() {
            if (gameState.cash < 25000000) return alert("Kumpulkan minimal Rp 25.000.000 untuk Prestige!");
            gameState.cash -= 25000000;
            gameState.prestige = (gameState.prestige || 0) + 1;
            gameState.reputation += 30;
            playSFX('coin');
            alert(`🏆 PRESTIGE LEVEL ${gameState.prestige}! Omzet seluruh cabang naik permanen +25%!`);
            persist(); updateUI();
        }
        let constructing = false;
        function startUpgrade(type, sec) {
            if (constructing) return alert("Sedang dalam proses konstruksi!");
            let cost = type === 'tent' ? gameState.tentLevel * 2500000 : (type === 'staff' ? gameState.staffLevel * 3500000 : (gameState.branches + 1) * 8000000);
            if (gameState.cash < cost) return alert("Kas tidak cukup!");
            gameState.cash -= cost; constructing = true; persist(); updateUI();

            const box = document.getElementById('const-box');
            box.classList.remove('hidden');
            let rem = sec;
            const iv = setInterval(() => {
                rem--;
                document.getElementById('const-time').innerText = `${rem}d`;
                document.getElementById('const-bar').style.width = `${((sec - rem)/sec)*100}%`;
                if (rem <= 0) {
                    clearInterval(iv); constructing = false; box.classList.add('hidden');
                    if (type === 'tent') { gameState.tentLevel++; gameState.reputation += 15; }
                    if (type === 'staff') gameState.staffLevel++;
                    if (type === 'branch') gameState.branches++;
                    playSFX('coin'); persist(); updateUI();
                }
            }, 1000);
        }
         // ==================== MINI-GAME RUSH HOUR & SIMULASI ====================
        function startRushHourShift() {
            const btn = document.getElementById('btn-open');
            btn.disabled = true;
            rushHourActive = true;
            rushCombo = 0;

            const badge = document.getElementById('combo-badge');
            badge.classList.remove('hidden');
            badge.innerText = "🔥 RUSH HOUR! Klik Pesanan di Layar!";

            const labels = ["Lele Pedas!", "GoFood!", "Es Teh!", "GrabFood!", "Nasgor!", "ShopeeFood!"];
            const spawnInt = setInterval(() => {
                if (!rushHourActive) return;
                orderBubbles.push({
                    x: Math.random() * (canvas.width - 120) + 60,
                    y: Math.random() * 80 + 60,
                    text: labels[Math.floor(Math.random() * labels.length)]
                });
                if (orderBubbles.length > 5) orderBubbles.shift();
            }, 950);

            setTimeout(() => {
                clearInterval(spawnInt);
                rushHourActive = false;
                orderBubbles = [];
                badge.classList.add('hidden');
                finalizeSimulation(rushCombo);
                btn.disabled = false;
            }, 8000);
        }

        async function finalizeSimulation(comboCount) {
            const apps = [];
            if (document.getElementById('app-go').checked) apps.push('go');
            if (document.getElementById('app-grab').checked) apps.push('grab');
            if (document.getElementById('app-shopee').checked) apps.push('shopee');

            const res = await fetch('/api/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    state: gameState,
                    menu: document.getElementById('select-menu').value,
                    stock: parseInt(document.getElementById('in-stock').value),
                    price: parseInt(document.getElementById('in-price').value),
                    apps: apps,
                    isRaining: isRaining,
                    combo: comboCount
                })
            });
            const data = await res.json();
            if (data.error) return alert(data.error);

            gameState = data.new_state;
            rollDailyWeather();
            persist(); updateUI();

            const ev = data.report.event;
            if (ev.type === 'special') {
                playSFX('coin');
                document.getElementById('sp-title').innerText = ev.title;
                document.getElementById('sp-desc').innerText = ev.desc;
                document.getElementById('sp-reward').innerText = `Bonus Event: +${formatRp(ev.cash)} & +${ev.rep}⭐`;
                document.getElementById('special-modal').classList.remove('hidden');
            } else {
                playSFX(data.report.profit >= 0 ? 'coin' : 'alert');
            }

            document.getElementById('res-day').innerText = `Malam Ke-${gameState.day - 1}`;
            document.getElementById('res-metrics').classList.remove('hidden');
            document.getElementById('res-dine').innerText = `${data.report.dinein} Porsi`;
            document.getElementById('res-ojol').innerText = `${data.report.online} Porsi`;
            document.getElementById('res-prof').innerText = (data.report.profit >= 0 ? "+" : "") + formatRp(data.report.profit);
            document.getElementById('event-banner').innerHTML = `<b>${ev.title}</b><p class="text-[11px] mt-0.5">${ev.desc} (Bonus Combo: +${formatRp(comboCount * 50000)})</p>`;

            // Peluang 35% Muncul Pelanggan VIP Interaktif setelah tutup lapak!
            if (Math.random() < 0.35) {
                triggerVIP();
            }
        }

        function triggerVIP() {
            const vip = VIP_DATA[Math.floor(Math.random() * VIP_DATA.length)];
            document.getElementById('vip-avatar').innerText = vip.avatar;
            document.getElementById('vip-name').innerText = vip.name;
            document.getElementById('vip-role').innerText = vip.role;
            document.getElementById('vip-dialog').innerText = vip.dialog;

            const btnA = document.getElementById('vip-btn-a');
            const btnB = document.getElementById('vip-btn-b');
            btnA.innerText = vip.optA.label;
            btnB.innerText = vip.optB.label;

            btnA.onclick = () => resolveVIP(vip.optA);
            btnB.onclick = () => resolveVIP(vip.optB);
            document.getElementById('vip-modal').classList.remove('hidden');
        }

        function resolveVIP(opt) {
            gameState.cash = Math.max(0, gameState.cash + opt.cash);
            gameState.reputation = Math.max(1, gameState.reputation + opt.rep);
            if (opt.shield) gameState.satpolShield = true;
            playSFX('coin');
            document.getElementById('vip-modal').classList.add('hidden');
            alert(opt.reply);
            persist(); updateUI();
        }

        renderSaved();
    </script>
</body>
</html>
"""
@app.route('/')
def index():
    return render_template_string(HTML_APP, cities=CITIES, menus=MENUS, vips=VIP_ENCOUNTERS)

@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json
    state = data['state']
    menu = MENUS[data['menu']]
    city = CITIES[state['city']]
    stock = int(data['stock'])
    price = int(data['price'])
    apps = data.get('apps', [])
    is_raining = data.get('isRaining', False)
    combo = int(data.get('combo', 0))

    unit_cost = int(menu['base_cost'] * city['cost_mult'])
    total_modal = stock * unit_cost
    if state['cash'] < total_modal:
        return jsonify({"error": f"Saldo kas tidak cukup untuk belanja bahan (Butuh Rp {total_modal:,})!"})

    event = random.choice(EVENTS)
    is_weekend = ((state['day'] - 1) % 7) == 5
    decors = state.get('decors', [])

    # Bonus Dekorasi & Cuaca
    decor_mult = 1.0 + (0.15 if 'neon' in decors else 0) + (0.25 if 'tv' in decors else 0)
    rain_dine_mult = 0.55 if is_raining else 1.0
    rain_ojol_mult = 1.85 if is_raining else 1.0
    prestige_mult = 1.0 + (state.get('prestige', 0) * 0.25)

    base_demand = city['demand_base'] + (state['reputation'] * 1.1) + (state['tentLevel'] * 14)
    ideal_price = menu['ideal_price'] * (1.2 if 'gerobak' in decors else 1.0)
    price_factor = max(0.35, min(1.8, ideal_price / max(price, 8000)))

    ev_mult = event.get('mult', 1.0)
    extra_cash = event.get('cash', 0)
    rep_delta = event.get('rep', 0)

    if event['effect'] == 'satpol':
        if state.get('satpolShield'):
            extra_cash = 0
            event = {"title": "🛡️ Dilindungi Pak RT!", "desc": "Razia Satpol PP berhasil diredam berkat dukungan warga setempat!", "type": "good"}
            state['satpolShield'] = False
        else:
            extra_cash = event['value']
    elif event['effect'] == 'cash':
        extra_cash = event['value']

    dinein_demand = int(base_demand * menu['pop'] * price_factor * decor_mult * rain_dine_mult * (1.45 if is_weekend else 1.0) * ev_mult)
    online_demand = int(len(apps) * (16 + state['reputation'] * 0.5) * price_factor * rain_ojol_mult)

    cap = 60 + (state['staffLevel'] * 45) + (state['tentLevel'] * 25)
    dinein_sold = min(stock, min(dinein_demand, cap))
    online_sold = min(stock - dinein_sold, online_demand)

    revenue = int(((dinein_sold * price) + (online_sold * price * 0.85)) * prestige_mult)
    combo_bonus = combo * 50000
    passive = state['branches'] * 500000
    profit = (revenue + extra_cash + combo_bonus + passive) - total_modal

    played_day = state['day']
    state['day'] += 1
    state['cash'] = max(0, state['cash'] + profit)
    state['reputation'] = max(1, state['reputation'] + rep_delta + (2 if (dinein_sold + online_sold) == stock else 0))
    state['history'].append({"day": f"H-{played_day}", "revenue": revenue, "profit": profit})

    return jsonify({
        "new_state": state,
        "report": {"dinein": dinein_sold, "online": online_sold, "profit": profit, "event": event}
    })

if __name__ == '__main__':
    app.run(debug=True)
       
