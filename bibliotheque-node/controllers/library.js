const model = require('../models/library');
async function page(req,res) { res.render('index', { stats:await model.dashboard(), books:await model.books(req.query.q || ''), borrowers:await model.borrowers(), loans:await model.loans(), query:req.query.q || '', message:req.query.message || null }); }
function redirect(res, message) { res.redirect('/?message=' + encodeURIComponent(message)); }
async function addBook(req,res) { try { await model.addBook(req.body); redirect(res,'Livre ajouté.'); } catch(e) { redirect(res,e.message); } }
async function updateBook(req,res) { try { await model.updateBook(Number(req.params.id),req.body); redirect(res,'Livre modifié.'); } catch(e) { redirect(res,e.message); } }
async function deleteBook(req,res) { try { await model.deleteBook(Number(req.params.id)); redirect(res,'Livre supprimé.'); } catch(e) { redirect(res,e.message); } }
async function addBorrower(req,res) { try { await model.addBorrower(req.body); redirect(res,'Emprunteur enregistré.'); } catch(e) { redirect(res,e.message); } }
async function loan(req,res) { try { await model.loan(Number(req.body.livre_id),Number(req.body.emprunteur_id)); redirect(res,'Emprunt enregistré.'); } catch(e) { redirect(res,e.message); } }
async function returnLoan(req,res) { try { await model.returnLoan(Number(req.params.id)); redirect(res,'Retour enregistré.'); } catch(e) { redirect(res,e.message); } }
module.exports = { page,addBook,updateBook,deleteBook,addBorrower,loan,returnLoan };
