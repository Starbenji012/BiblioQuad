const express = require('express');
const c = require('./controllers/library');
const router = express.Router();
router.get('/', c.page); router.post('/books', c.addBook); router.post('/books/:id/edit', c.updateBook); router.post('/books/:id/delete', c.deleteBook); router.post('/borrowers', c.addBorrower); router.post('/loans', c.loan); router.post('/loans/:id/return', c.returnLoan);
module.exports = router;
