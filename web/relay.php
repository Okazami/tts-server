<?php
$cmd = $_GET['cmd'] ?? '';
if($cmd == 'on') {
    file_put_contents("relay_on.txt", "1");
} else {
    if(file_exists("relay_on.txt")) unlink("relay_on.txt");
}
header("Location: index.php");
?>