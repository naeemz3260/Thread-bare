<?php
// Sample vulnerable PHP code for scanner demo purposes.

$db_host = "localhost";
$db_user = "admin";
$db_pass = "P@ssw0rd2024"; // hardcoded credential
$conn = mysqli_connect($db_host, $db_user, $db_pass, "shop");

// SQL Injection: raw user input concatenated into query
if (isset($_GET['id'])) {
    $id = $_GET['id'];
    $query = "SELECT * FROM products WHERE id = " . $id;
    $result = mysqli_query($conn, $query);
}

// Reflected XSS: user input echoed without escaping
if (isset($_GET['name'])) {
    echo "<p>Welcome, " . $_GET['name'] . "</p>";
}

// Path Traversal: user-controlled filename passed to include/file read
if (isset($_GET['page'])) {
    include($_GET['page'] . '.php');
}

// Command Injection: user input passed to shell exec
if (isset($_GET['file'])) {
    system("cat " . $_GET['file']);
}

// Insecure Deserialization: untrusted data passed to unserialize()
if (isset($_COOKIE['session_data'])) {
    $data = unserialize($_COOKIE['session_data']);
}
?>
