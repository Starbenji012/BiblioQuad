from flask import Flask, flash, redirect, render_template, request, url_for
from config import Config
import models


app = Flask(__name__)
app.config.from_object(Config)


@app.route("/")
def index():
    return render_template("index.html", stats=models.dashboard(), books=models.books(request.args.get("q", "")),
                           borrowers=models.borrowers(), loans=models.loans(), query=request.args.get("q", ""))


@app.post("/books")
def add_book():
    try:
        models.add_book({"titre": request.form["titre"].strip(), "auteur": request.form["auteur"].strip(),
                         "categorie": request.form.get("categorie", "").strip(), "quantite": int(request.form["quantite"])})
        flash("Livre ajouté.", "success")
    except (ValueError, KeyError) as error:
        flash(f"Données invalides : {error}", "error")
    return redirect(url_for("index"))


@app.post("/borrowers")
def add_borrower():
    try:
        models.add_borrower({"nom": request.form["nom"].strip(), "telephone": request.form["telephone"].strip()})
        flash("Emprunteur enregistré.", "success")
    except KeyError as error:
        flash(f"Donnée manquante : {error}", "error")
    return redirect(url_for("index"))


@app.post("/books/<int:book_id>/edit")
def edit_book(book_id):
    try:
        models.update_book(book_id, {"titre": request.form["titre"].strip(), "auteur": request.form["auteur"].strip(),
                                     "categorie": request.form.get("categorie", "").strip(), "quantite": int(request.form["quantite"])})
        flash("Livre modifié.", "success")
    except (ValueError, KeyError) as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.post("/books/<int:book_id>/delete")
def delete_book(book_id):
    try:
        models.delete_book(book_id)
        flash("Livre supprimé.", "success")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.post("/loans")
def add_loan():
    try:
        models.create_loan(int(request.form["livre_id"]), int(request.form["emprunteur_id"]))
        flash("Emprunt enregistré.", "success")
    except (ValueError, KeyError) as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


@app.post("/loans/<int:loan_id>/return")
def return_loan(loan_id):
    try:
        models.return_loan(loan_id)
        flash("Retour enregistré.", "success")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
