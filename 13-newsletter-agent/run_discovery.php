<?php
/**
 * Run Discovery PHP Script
 * 
 * This script handles running the source discovery Python script.
 * It executes the discover_sources.py script and returns the result.
 */

// Set headers for JSON response
header('Content-Type: application/json');

// Path to the Python script
$pythonScript = 'discover_sources.py';

// Execute the Python script
$command = "python $pythonScript --action all 2>&1";
$output = [];
$returnCode = 0;

exec($command, $output, $returnCode);

// Check if the command was successful
if ($returnCode !== 0) {
    echo json_encode([
        'success' => false,
        'message' => 'Failed to run source discovery script',
        'output' => implode("\n", $output),
        'code' => $returnCode
    ]);
    exit;
}

// Check if sources.json was created
if (!file_exists('sources.json')) {
    echo json_encode([
        'success' => false,
        'message' => 'Source discovery completed but no sources file was created',
        'output' => implode("\n", $output)
    ]);
    exit;
}

// Read the sources.json file
$sourcesJson = file_get_contents('sources.json');
$sources = json_decode($sourcesJson, true);

// Check if rss_feeds.json exists
if (file_exists('rss_feeds.json')) {
    $rssJson = file_get_contents('rss_feeds.json');
    $rssFeeds = json_decode($rssJson, true);
} else {
    $rssFeeds = [];
}

// Return success response
echo json_encode([
    'success' => true,
    'message' => 'Source discovery completed successfully',
    'output' => implode("\n", $output),
    'sources' => $sources,
    'rss_feeds_count' => count($rssFeeds)
]);
