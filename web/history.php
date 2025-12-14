<?php
session_start();
if (!isset($_SESSION['user'])) {
    header("Location: login.php");
    exit;
}
include 'db.php';
?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Riwayat Pengumuman</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
</head>
<body class="bg-light">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-white bg-white shadow-sm sticky-top">
        <div class="container">
            <a class="navbar-brand fw-bold text-primary" href="index.php">DESA DWITIRO</a>
            <a href="index.php" class="btn btn-outline-secondary btn-sm rounded-pill px-3">
                <i class="bi bi-arrow-left"></i> Kembali ke Dashboard
            </a>
        </div>
    </nav>

    <div class="container mt-5">
        <div class="card shadow border-0 rounded-4">
            <div class="card-header bg-white py-3">
                <h5 class="mb-0 fw-bold"><i class="bi bi-clock-history me-2"></i> Riwayat Pengumuman</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th width="5%">No</th>
                                <th width="50%">Isi Pesan</th>
                                <th width="15%">Status</th>
                                <th width="20%">Waktu Kirim</th>
                                <th width="10%">Audio</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php
                            // Ambil data dari database (Limit 50 terakhir)
                            $sql = "SELECT * FROM messages ORDER BY id DESC LIMIT 50";
                            $result = $conn->query($sql);

                            if ($result->num_rows > 0) {
                                while($row = $result->fetch_assoc()) {
                                    // Atur Badge Status
                                    if ($row['status'] == 'done') {
                                        $badge = '<span class="badge bg-success bg-opacity-10 text-success rounded-pill px-3">Selesai</span>';
                                    } else {
                                        $badge = '<span class="badge bg-warning bg-opacity-10 text-warning rounded-pill px-3">Antrian</span>';
                                    }
                                    
                                    echo "<tr>";
                                    echo "<td class='fw-bold text-secondary'>{$row['id']}</td>";
                                    echo "<td>{$row['content']}</td>";
                                    echo "<td>{$badge}</td>";
                                    echo "<td class='small text-muted'>{$row['created_at']}</td>";
                                    
                                    // Tombol dengar (Optional, kalau mau dengerin lagi)
                                    echo "<td>
                                            <a href='{$row['audio_url']}' target='_blank' class='btn btn-sm btn-light border'>
                                                <i class='bi bi-play-fill'></i> Play
                                            </a>
                                          </td>";
                                    echo "</tr>";
                                }
                            } else {
                                echo "<tr><td colspan='5' class='text-center py-4 text-muted'>Belum ada riwayat pengumuman.</td></tr>";
                            }
                            ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>