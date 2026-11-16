<?php
require_once __DIR__ . '/app/LibraryController.php';

$database = Database::connect();
$controller = new LibraryController(new LibraryModel($database));
$data = $controller->handle();
require __DIR__ . '/views/index.php';
