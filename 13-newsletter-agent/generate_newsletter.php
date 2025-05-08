<?php
// Set headers to prevent caching
header('Cache-Control: no-cache, must-revalidate');
header('Expires: Sat, 26 Jul 1997 05:00:00 GMT');
header('Content-Type: text/plain');

// Path to the Python script
$pythonScript = 'rated_newsletter_test.py';
$pythonPath = '/usr/bin/python'; // Adjust this path if needed

// Execute the Python script
$command = "cd " . escapeshellarg(dirname(__FILE__)) . " && $pythonPath $pythonScript 2>&1";
$output = [];
$returnCode = 0;

exec($command, $output, $returnCode);

// Check if the command was successful
if ($returnCode === 0) {
    echo "success\n";
    echo "Output:\n";
    echo implode("\n", $output);
} else {
    echo "error\n";
    echo "Return code: $returnCode\n";
    echo "Output:\n";
    echo implode("\n", $output);
}
?>
