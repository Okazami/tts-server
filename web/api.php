<?php
header('Content-Type: application/json');
include 'db.php';

$action = $_GET['action'] ?? '';

// 1. Cek Status (Untuk ESP32)
if ($action == 'check_status') {
    $sql = "SELECT id, audio_url FROM messages WHERE status='pending' ORDER BY id ASC LIMIT 1";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        echo json_encode([
            "status" => "ready",
            "url" => $row['audio_url'],
            "id" => (int)$row['id']
        ]);
    } else {
        echo json_encode(["status" => "empty"]);
    }
}

// 2. Lapor Selesai (Untuk ESP32)
if ($action == 'done') {
    $id = $_GET['id'] ?? 0;
    if ($id) {
        $stmt = $conn->prepare("UPDATE messages SET status='done' WHERE id=?");
        $stmt->bind_param("i", $id);
        $stmt->execute();
    }
    echo "OK";
}

// 3. Cek Relay
if ($action == 'relay_status') {
    $status = file_exists("relay_on.txt") ? "on" : "off";
    echo json_encode(["status" => $status]);
}
?>