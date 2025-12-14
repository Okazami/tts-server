<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Pengumuman</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .card-custom {
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
    </style>
</head>
<body class="bg-light">

    <!-- Navbar Header -->
    <nav class="navbar navbar-expand-lg navbar-white bg-white border-bottom">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#">PEMERINTAH DESA<br>DWITIRO</a>
            <div class="d-flex align-items-center">
                <a href="/history" class="btn btn-outline-primary me-2">Riwayat</a>
                <a href="/logout" class="btn btn-outline-danger">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        
        <!-- Bagian 1: Status Amplifier -->
        <div class="card card-custom">
            <div class="card-body text-center p-5">
                <h4 class="mb-4">Status Amplifier</h4>
                
                <!-- Tombol ON/OFF -->
                <!-- Menggunakan JavaScript/Link Flask untuk trigger -->
                <div class="btn-group" role="group">
                    <a href="/relay/on" class="btn btn-success btn-lg px-4">NYALAKAN (ON)</a>
                    <a href="/relay/off" class="btn btn-danger btn-lg px-4">MATIKAN (OFF)</a>
                </div>
                
                <p class="mt-3 text-muted">Klik tombol di atas untuk mengontrol amplifier masjid.</p>
            </div>
        </div>

        <!-- Bagian 2: Form Pengumuman -->
        <div class="card card-custom">
            <div class="card-body p-4">
                <h4 class="text-center mb-4">Form Pengumuman</h4>
                
                <form action="/tts" method="POST">
                    <div class="mb-3">
                        <label for="pesan" class="form-label fw-bold">Ketik Pesan:</label>
                        <textarea class="form-control" id="pesan" name="text" rows="5" placeholder="Tulis pengumuman di sini..." required></textarea>
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-dark btn-lg">Kirim Pesan</button>
                    </div>
                </form>
            </div>
        </div>

    </div>

</body>
</html>