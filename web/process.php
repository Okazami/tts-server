<?php
include 'db.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $text = $_POST['text'];
    
    // GANTI DENGAN IP PUBLIC AWS KAMU!
    $ip_aws = "3.27.18.184"; 

    // Panggil Python Service (Localhost Port 5000)
    $ch = curl_init("http://127.0.0.1:5000/generate");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, ['text' => $text]);
    $res = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($res, true);

    if (isset($data['status']) && $data['status'] == 'success') {
        $filename = $data['filename'];
        $audio_url = "http://$ip_aws/static/$filename";
        $waktu = date("Y-m-d H:i:s");

        $stmt = $conn->prepare("INSERT INTO messages (content, status, audio_url, created_at) VALUES (?, 'pending', ?, ?)");
        $stmt->bind_param("sss", $text, $audio_url, $waktu);
        
        if($stmt->execute()){
            header("Location: index.php?msg=sukses");
        } else {
            echo "Gagal DB: " . $conn->error;
        }
    } else {
        echo "Gagal Python: " . ($data['message'] ?? 'Unknown Error');
    }
}
?>