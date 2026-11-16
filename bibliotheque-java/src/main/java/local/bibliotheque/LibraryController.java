package local.bibliotheque;
import org.springframework.stereotype.Controller; import org.springframework.ui.Model; import org.springframework.web.bind.annotation.*;
@Controller public class LibraryController {
 private final LibraryService service; public LibraryController(LibraryService s){service=s;}
 @GetMapping("/") public String index(@RequestParam(defaultValue="") String q,@RequestParam(defaultValue="") String message,Model m){m.addAttribute("stats",service.stats());m.addAttribute("books",service.books(q));m.addAttribute("borrowers",service.borrowers());m.addAttribute("loans",service.loans());m.addAttribute("query",q);m.addAttribute("message",message);return "index";}
 private String back(String msg){return "redirect:/?message="+java.net.URLEncoder.encode(msg,java.nio.charset.StandardCharsets.UTF_8);}
 @PostMapping("/books") public String book(@RequestParam String titre,@RequestParam String auteur,@RequestParam(defaultValue="") String categorie,@RequestParam int quantite){try{service.addBook(titre,auteur,categorie,quantite);return back("Livre ajouté.");}catch(RuntimeException e){return back(e.getMessage());}}
 @PostMapping("/books/{id}/edit") public String edit(@PathVariable int id,@RequestParam String titre,@RequestParam String auteur,@RequestParam(defaultValue="") String categorie,@RequestParam int quantite){try{service.updateBook(id,titre,auteur,categorie,quantite);return back("Livre modifié.");}catch(RuntimeException e){return back(e.getMessage());}}
 @PostMapping("/books/{id}/delete") public String delete(@PathVariable int id){try{service.deleteBook(id);return back("Livre supprimé.");}catch(RuntimeException e){return back(e.getMessage());}}
 @PostMapping("/borrowers") public String borrower(@RequestParam String nom,@RequestParam String telephone){try{service.addBorrower(nom,telephone);return back("Emprunteur enregistré.");}catch(RuntimeException e){return back(e.getMessage());}}
 @PostMapping("/loans") public String loan(@RequestParam int livre_id,@RequestParam int emprunteur_id){try{service.loan(livre_id,emprunteur_id);return back("Emprunt enregistré.");}catch(RuntimeException e){return back(e.getMessage());}}
 @PostMapping("/loans/{id}/return") public String returned(@PathVariable int id){try{service.returnLoan(id);return back("Retour enregistré.");}catch(RuntimeException e){return back(e.getMessage());}}
}
