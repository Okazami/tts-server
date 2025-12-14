<?php
// Konfigurasi Database AWS RDS
$host = "db-desa.cpcki2auqun0.ap-southeast-2.rds.amazonaws.com"; // Ganti dengan Endpoint RDS
$user = "admin";
$pass = "dbdesa123";      // Ganti Password
$db   = "flask.app";

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("Koneksi Database Gagal: " . $conn->connect_error);
}
?>