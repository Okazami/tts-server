<?php
session_start();

// 1. Cek Login
if (!isset($_SESSION['user'])) {
    header("Location: login.php");
    exit;
}

include 'db.php';

// 2. Cek apakah ada ID yang dikirim
if (isset($_GET['id'])) {
    $id = (int)$_GET['id']; // Pastikan ID berupa angka

    // 3. Hapus data dari database
    $stmt = $conn->prepare("DELETE FROM messages WHERE id = ?");
    $stmt->bind_param("i", $id);

    if ($stmt->execute()) {
        // Kalau berhasil, balik ke history bawa pesan sukses
        header("Location: history.php?msg=hapus");
    } else {
        echo "Gagal menghapus data.";
    }
} else {
    header("Location: history.php");
}
?>