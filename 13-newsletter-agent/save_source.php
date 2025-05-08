<?php
/**
 * Save Source PHP Script
 * 
 * This script handles saving sources to the rss_feeds.json file.
 * It receives a JSON payload with the sources array and saves it to the file.
 */

// Set headers for JSON response
header('Content-Type: application/json');

// Get the JSON payload
$json = file_get_contents('php://input');
$data = json_decode($json, true);

// Check if sources array exists
if (!isset($data['sources']) || !is_array($data['sources'])) {
    echo json_encode([
        'success' => false,
        'message' => 'Invalid sources data'
    ]);
    exit;
}

// Validate each source URL
$sources = $data['sources'];
$validSources = [];

foreach ($sources as $source) {
    if (filter_var($source, FILTER_VALIDATE_URL)) {
        $validSources[] = $source;
    }
}

// Save the sources to the file
$result = file_put_contents('rss_feeds.json', json_encode($validSources, JSON_PRETTY_PRINT));

if ($result === false) {
    echo json_encode([
        'success' => false,
        'message' => 'Failed to save sources to file'
    ]);
    exit;
}

// Return success response
echo json_encode([
    'success' => true,
    'message' => 'Sources saved successfully',
    'count' => count($validSources)
]);
