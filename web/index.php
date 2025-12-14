<!DOCTYPE html>
<html>
<head>
    <title>Desa Dwitiro Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="card shadow p-4">
            <h2 class="text-center mb-4">📢 Sistem Informasi Desa</h2>
            
            <?php if(isset($_GET['msg'])) echo "<div class='alert alert-success'>Pesan Terkirim!</div>"; ?>

            <form action="process.php" method="POST">
                <div class="mb-3">
                    <label class="fw-bold">Isi Pengumuman:</label>
                    <textarea name="text" class="form-control" rows="4" required placeholder="Ketik pesan..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary w-100 py-2">🔊 Kirim Pesan</button>
            </form>
            
            <hr class="my-4">
            
            <div class="text-center">
                <h4>Kontrol Amplifier</h4>
                <div class="btn-group w-100">
                    <a href="relay.php?cmd=on" class="btn btn-success">NYALAKAN (ON)</a>
                    <a href="relay.php?cmd=off" class="btn btn-danger">MATIKAN (OFF)</a>
                </div>
                <p class="mt-2 text-muted">Status: <?php echo file_exists("relay_on.txt") ? "<b class='text-success'>MENYALA</b>" : "<b class='text-danger'>MATI</b>"; ?></p>
            </div>
        </div>
        
        <div class="card shadow mt-4 p-4">
            <h4>Riwayat Pesan</h4>
            <table class="table table-striped">
                <thead><tr><th>No</th><th>Pesan</th><th>Status</th><th>Waktu</th></tr></thead>
                <tbody>
                    <?php
                    include 'db.php';
                    $res = $conn->query("SELECT * FROM messages ORDER BY id DESC LIMIT 10");
                    while($row = $res->fetch_assoc()){
                        $status = ($row['status']=='done') ? '<span class="badge bg-success">Selesai</span>' : '<span class="badge bg-warning">Antrian</span>';
                        echo "<tr><td>{$row['id']}</td><td>{$row['content']}</td><td>$status</td><td>{$row['created_at']}</td></tr>";
                    }
                    ?>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>