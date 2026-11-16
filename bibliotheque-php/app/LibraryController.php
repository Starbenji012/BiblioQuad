<?php
require_once __DIR__ . '/LibraryModel.php';

final class LibraryController {
    public function __construct(private LibraryModel $model) {}
    public function handle(): array {
        $message = $_GET['message'] ?? '';
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            try {
                $action = $_POST['action'] ?? '';
                if ($action === 'book') $this->model->addBook($_POST);
                elseif ($action === 'edit_book') $this->model->updateBook($_POST);
                elseif ($action === 'delete_book') $this->model->deleteBook((int)$_POST['id']);
                elseif ($action === 'borrower') $this->model->addBorrower($_POST);
                elseif ($action === 'loan') $this->model->createLoan((int)$_POST['livre_id'], (int)$_POST['emprunteur_id']);
                elseif ($action === 'return') $this->model->returnLoan((int)$_POST['id']);
                $message = 'Opération effectuée.';
            } catch (Throwable $error) { $message = $error->getMessage(); }
        }
        return ['stats'=>$this->model->dashboard(), 'books'=>$this->model->books($_GET['q'] ?? ''), 'borrowers'=>$this->model->borrowers(), 'loans'=>$this->model->loans(), 'query'=>$_GET['q'] ?? '', 'message'=>$message];
    }
}
