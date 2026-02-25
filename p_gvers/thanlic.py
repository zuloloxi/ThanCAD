from typing import List

def GPL(lang=-1) -> List[str]:        #lang==-1 ->Greek, lang==-2 -> English
    lic_name = "GPL"
    lic_short = """\
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details (www.gnu.org/licenses/gpl.html).

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

    if lang == -1:
        lic = u"""\
Αυτή είναι μια ανεπίσημη μετάφραση της Γενικής άδειας Δημόσιας Χρήσης
GNU (GNU GPL) στα ελληνικά. Δεν εκδόθηκε από το Ίδρυμα Ελεύθερου
Λογισμικού (Free Software Foundation) και δεν διατυπώνει νομικά τους όρους
διανομής λογισμικού που υπάγεται στη Γενική άδεια Δημόσιας Χρήσης
GNU-αυτό γίνεται μόνο από την επίσημη αγγλική έκδοση της άδειας (GNU GPL).
Ωστόσο, ελπίζουμε ότι η μετάφραση αυτή θα βοηθήσει όσους μιλούν την
ελληνική να κατανοήσουν καλύτερα την άδεια GNU GPL.

This is an unofficial translation of the GNU General Public License into greek.
It was not published by the Free Software Foundation, and does not legally
state the distribution terms for software that uses the GNU GPL-only the
original English text of the GNU GPL does that. However, we hope that this
translation will help greek speakers understand the GNU GPL better.


			ΓΕΝΙΚΗ ΑΔΕΙΑ ΔΗΜΟΣΙΑΣ ΧΡΗΣΗΣ GNU

				Έκδοση 2, Ιούνιος 1991

 Copyright (C) 1989, 1991 Free Software Foundation, Inc.
 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 Επιτρέπεται σε όλους η αντιγραφή και διανομή αυτούσιων αντιγράφων
 αυτού του εγγράφου άδειας χρήσης, χωρίς ωστόσο να επιτρέπεται η αλλοίωσή του.

					Εισαγωγή

  Οι άδειες χρήσης των περισσότερων προγραμμάτων συντάσσονται για να
περιορίσουν την ελευθερία σας να τα μοιράζεστε με άλλους και να τα
επεξεργάζεστε.  Εν αντιθέσει, η Γενική άδεια Δημόσιας Χρήσης GNU έχει σκοπό να
εγγυηθεί την ελευθερία σας να χρησιμοποιείτε από κοινού με άλλους και να
τροποποιείτε προγράμματα που διατίθενται ελεύθερα -- δηλαδή να εγγυηθεί ότι το
πρόγραμμα είναι ελεύθερο για όλους τους χρήστες.  Αυτή η Γενική άδεια Δημόσιας
Χρήσης ισχύει για τα περισσότερα προγράμματα του Ιδρύματος Ελεύθερου Λογισμικού
(Free Software Foundation), καθώς και για κάθε άλλο πρόγραμμα οι δημιουργοί του
οποίου συμμορφώνονται με την άδεια αυτή.  (Ορισμένα άλλα προγράμματα του
Ιδρύματος Ελεύθερου Λογισμικού καλύπτονται από τη Γενική άδεια Δημόσιας Χρήσης
Βιβλιοθήκης GNU.)  Την άδεια αυτή μπορείτε να την εφαρμόσετε και στα δικά σας
προγράμματα.

  Μιλώντας για ελεύθερο λογισμικό, αναφερόμαστε στην ελευθερία χρήσης του, όχι
στο κόστος του.  Οι Γενικές άδειες Δημόσιας Χρήσης τις οποίες συντάσσουμε έχουν
σκοπό να κατοχυρώσουν την ελευθερία σας να διανέμετε αντίγραφα ελεύθερου
λογισμικού (και να χρεώνετε, εάν το επιθυμείτε, την παροχή αυτής της
υπηρεσίας), να σας εξασφαλίσουν το δικαίωμα να λαμβάνετε τον πηγαίο κώδικα, εάν
τον χρειάζεστε, καθώς και να τροποποιείτε το πρόγραμμα ή να χρησιμοποιείτε
τμήματά του σε καινούργια ελεύθερα προγράμματα -- και να διασφαλίσουν ότι είστε
ενήμεροι για τα παραπάνω δικαιώματά σας.

  Για την προστασία των δικαιωμάτων σας, επιβάλλεται να προβούμε σε
περιορισμούς
οι οποίοι θα εμποδίζουν σε κάποιον να αμφισβητήσει τα δικαιώματά σας ή να σας
ζητήσει να παραιτηθείτε από αυτά. Αυτοί οι περιορισμοί ερμηνεύονται ως
συγκεκριμένες ευθύνες για εσάς εάν διανέμετε αντίγραφα κάποιου ελεύθερου
λογισμικού ή εάν το τροποποιείτε.

  Για παράδειγμα, εάν διανέμετε αντίγραφα ενός τέτοιου προγράμματος, είτε
δωρεάν
είτε με χρέωση, πρέπει να εκχωρήσετε στους παραλήπτες όλα τα δικαιώματα που
έχετε και εσείς.  Πρέπει να εγγυηθείτε ότι και εκείνοι επίσης λαμβάνουν, ή
μπορούν να λάβουν, τον πηγαίο κώδικα.  Πρέπει επίσης να τους επιδείξετε τους
όρους αυτής της άδειας χρήσης, ώστε να είναι ενήμεροι για τα δικαιώματά τους.

  Προστατεύουμε τα δικαιώματά σας με δύο τρόπους: (1) προστατεύοντας το
λογισμικό και (2) προσφέροντάς σας αυτήν την άδεια, με την οποία αποκτάτε
νόμιμο δικαίωμα αντιγραφής, διανομής ή/και τροποποίησης του λογισμικού.

  Επιπλέον, για την προστασία των δημιουργών και τη δική μας, θέλουμε να
καταστήσουμε βέβαιο ότι όλοι κατανοούν την απουσία εγγύησης για αυτό το
ελεύθερο λογισμικό.  Εάν το λογισμικό τροποποιηθεί από κάποιον τρίτο και στη
συνέχεια διανεμηθεί, θέλουμε να γνωρίζουν οι παραλήπτες ότι το λογισμικό που
απέκτησαν δεν είναι το πρωτότυπο, έτσι ώστε οποιοδήποτε πρόβλημα προκληθεί από
τρίτους να μην βαρύνει το όνομα του δημιουργού.

  Τέλος, κάθε ελεύθερο λογισμικό απειλείται συνεχώς από τις κατοχυρώσεις
ευρεσιτεχνίας λογισμικού.  Θέλουμε να αποφύγουμε τον κίνδυνο να αποκτήσουν οι
αναδιανομείς ελεύθερου λογισμικού τίτλους ευρεσιτεχνίας, καθιστώντας έτσι το
λογισμικό προσωπική τους ιδιοκτησία.  Για να αποκλείσουμε αυτό το ενδεχόμενο,
έχουμε ξεκαθαρίσει ότι οποιαδήποτε ευρεσιτεχνία θα πρέπει να παρέχει άδεια
ελεύθερης χρήσης από όλους, διαφορετικά να μην παρέχει καμιά απολύτως άδεια.

  Ακολουθούν οι ακριβείς όροι και συνθήκες αντιγραφής, διανομής και
τροποποίησης.

		    ΓΕΝΙΚΗ ΑΔΕΙΑ ΔΗΜΟΣΙΑΣ ΧΡΗΣΗΣ GNU
   ΟΡΟΙ ΚΑΙ ΣΥΝΘΗΚΕΣ ΑΝΤΙΓΡΑΦΗΣ, ΔΙΑΝΟΜΗΣ ΚΑΙ ΤΡΟΠΟΠΟΙΗΣΗΣ

  0. Η άδεια αυτή ισχύει για κάθε πρόγραμμα ή άλλο έργο που περιέχει
σημείωμα από τον κάτοχο πνευματικών δικαιωμάτων, στο οποίο αναφέρεται ότι η
διανομή του προγράμματος είναι δυνατή υπό τους όρους αυτής της Γενικής άδειας
Δημόσιας Χρήσης.  Ο όρος "Πρόγραμμα", παρακάτω, αναφέρεται σε οποιοδήποτε
τέτοιο πρόγραμμα ή έργο, ενώ ο όρος "έργο βασισμένο στο Πρόγραμμα" σημαίνει
είτε το Πρόγραμμα είτε κάθε άλλο παραγόμενο έργο που υπάγεται στο νόμο περί
πνευματικής ιδιοκτησίας: με λίγα λόγια, ένα έργο που περιέχει ακέραιο το
Πρόγραμμα ή ένα μέρος του, είτε αυτούσιο είτε με τροποποιήσεις ή/και
μεταφρασμένο σε άλλη γλώσσα.  (Από αυτό το σημείο, η μετάφραση θα
περιλαμβάνεται χωρίς περιορισμούς στον όρο "τροποποίηση".)  Κάθε κάτοχος της
άδειας χρήσης θα αναφέρεται στο εξής ως "εσείς/εσάς".

άλλες δραστηριότητες πέραν της αντιγραφής, της διανομής και της τροποποίησης
δεν καλύπτονται από αυτήν την άδεια - είναι εκτός των πλαισίων της.  Δεν
υπάρχει περιορισμός στην ενέργεια εκτέλεσης ενός προγράμματος, ενώ το προϊόν
της χρήσης του Προγράμματος καλύπτεται μόνο εφόσον το περιεχόμενό του συνιστά
έργο βασισμένο στο Πρόγραμμα (ανεξάρτητα από το εάν δημιουργήθηκε με την
εκτέλεση του Προγράμματος). Το κατά πόσο συμβαίνει αυτό εξαρτάται από το είδος
του Προγράμματος.

  1. Επιτρέπεται η αντιγραφή και διανομή αυτούσιων αντιγράφων του πηγαίου
κώδικα του Προγράμματος όπως ακριβώς το έχετε λάβει, σε οποιοδήποτε
αποθηκευτικό μέσο, με την προϋπόθεση ότι: θα δημοσιεύσετε εμφανώς και
καταλλήλως, σε κάθε αντίγραφο, ένα σημείωμα πνευματικής ιδιοκτησίας και ένα
σημείωμα αποποίησης ευθυνών εγγύησης - ότι θα συμπεριλάβετε ακέραια όλα τα
σημειώματα που αναφέρονται στην άδεια αυτή και στην απουσία οποιασδήποτε
εγγύησης - και, τέλος, ότι θα εκχωρήσετε σε κάθε άλλον παραλήπτη του
Προγράμματος ένα αντίγραφο αυτής της άδειας μαζί με το Πρόγραμμα.

Έχετε δικαίωμα να επιβάλετε χρέωση για τη φυσική ενέργεια της μεταφοράς ενός
αντιγράφου, καθώς και να παράσχετε, κατά την κρίση σας, προστασία εγγύησης με
χρέωση.

  2. Επιτρέπεται η τροποποίηση του αντιγράφου ή των αντιγράφων του Προγράμματος
ολόκληρου ή μέρους του, η οποία συνιστά συνεπώς δημιουργία ενός έργου
βασισμένου στο Πρόγραμμα, και η διανομή αυτών των τροποποιήσεων ή έργων υπό
τους όρους της Ενότητας 1 ως ανωτέρω, με την προϋπόθεση ότι και εσείς πληροίτε
όλες τις παρακάτω προϋποθέσεις:

    α) Πρέπει να φροντίζετε ώστε τα τροποποιημένα αρχεία να παρέχουν εμφανή
σημειώματα στα οποία να δηλώνεται η τροποποίηση των αρχείων και η ημερομηνία
τροποποίησης.

    β) Πρέπει να φροντίζετε ώστε για κάθε έργο το οποίο διανέμετε ή
δημοσιεύετε, και το οποίο περιέχει ή παράγεται από ολόκληρο ή μέρος του
Προγράμματος, να παρέχεται άδεια χρήσης του, χωρίς χρέωση, σε όλα τα τρίτα
μέρη, σύμφωνα με τους όρους αυτής της άδειας.

    γ) Εάν το τροποποιημένο πρόγραμμα διαβάζει εντολές αλληλεπιδραστικά, κατά
την τυπική εκτέλεσή του, πρέπει να φροντίζετε ώστε, κατά την έναρξη τυπικής
εκτέλεσής του για αυτήν την αλληλεπιδραστική χρήση, να εκτυπώνεται ή να
εμφανίζεται στην οθόνη μια ανακοίνωση, η οποία θα περιλαμβάνει το απαραίτητο
σημείωμα πνευματικής ιδιοκτησίας και ένα σημείωμα στο οποίο θα αναφέρεται ότι
δεν υπάρχει καμιά εγγύηση (ή, αντίθετα, ότι παρέχετε εγγύηση) και ότι οι
χρήστες έχουν τη δυνατότητα να αναδιανέμουν το πρόγραμμα σύμφωνα με τις
προϋποθέσεις αυτές, καθώς και οδηγίες προς το χρήστη για τον τρόπο προβολής
ενός αντιγράφου αυτής της άδειας.  (Εξαίρεση: εάν το ίδιο το Πρόγραμμα είναι
αλληλεπιδραστικό αλλά κανονικά δεν εκτυπώνει αυτήν την ανακοίνωση, δεν
απαιτείται από το έργο που δημιουργήσατε βασισμένοι στο Πρόγραμμα να εκτυπώνει
ανακοίνωση.)

Οι απαιτήσεις αυτές ισχύουν για ολόκληρο το τροποποιημένο έργο.  Εάν
συγκεκριμένες ενότητες του έργου αυτού δεν παράγονται από το Πρόγραμμα, και
μπορούν να θεωρηθούν με ασφάλεια από μόνες τους ως ανεξάρτητα και ξεχωριστά
έργα, τότε αυτή η άδεια και οι όροι της δεν ισχύουν για τις ενότητες αυτές,
κατά τη διανομή τους ως ξεχωριστά έργα.  Αλλά όταν διανέμετε τις ίδιες ενότητες
ως τμήματα ενός ευρύτερου έργου το οποίο βασίζεται στο Πρόγραμμα, η διανομή του
συνόλου πρέπει να υπόκειται στους όρους της άδειας, σύμφωνα με την οποία τα
δικαιώματα των άλλων χρηστών εκτείνονται σε ολόκληρο το έργο, επομένως και σε
καθένα χωριστό τμήμα του, ανεξάρτητα από το ποιος είναι ο δημιουργός του.

Επομένως, πρόθεση αυτής της ενότητας δεν είναι να εγείρει δικαιώματα ή να
αμφισβητήσει τα δικά σας δικαιώματα σε μια εργασία που δημιουργήσατε εξ
ολοκλήρου οι ίδιοι - η πρόθεση, περισσότερο, είναι να ασκήσει το δικαίωμα
ελέγχου της διανομής των παραγόμενων ή των συλλογικών έργων που βασίζονται στο
Πρόγραμμα.

Επιπλέον, η απλή προσθήκη ενός άλλου έργου, που δεν βασίζεται στο Πρόγραμμα,
μαζί με το Πρόγραμμα (ή με ένα έργο που βασίζεται στο Πρόγραμμα) σε τόμο ενός
μέσου αποθήκευσης ή διανομής, δεν υπάγει το άλλο έργο στα πλαίσια αυτής της
άδειας.

  3. Επιτρέπεται η αντιγραφή και διανομή του Προγράμματος (ή ενός έργου
βασισμένο σε αυτό, σύμφωνα με την Ενότητα 2) σε μορφή αντικειμενικού κώδικα ή
εκτελέσιμη μορφή, σύμφωνα με τους όρους των Ενοτήτων 1 και 2 ως ανωτέρω, με την
προϋπόθεση ότι πραγματοποιείτε και μια από τις ακόλουθες ενέργειες:

    α) Το συνοδεύετε με τον αντίστοιχο, πλήρη πηγαίο κώδικα, ο οποίος είναι
αναγνώσιμος από το σύστημα και ο οποίος πρέπει να διανέμεται σύμφωνα με τους
όρους των Ενοτήτων 1 και 2 παραπάνω, σε ένα συνηθισμένο μέσο μεταφοράς
λογισμικού - ή,
    β) Το συνοδεύετε με γραπτή προσφορά, ισχύουσα τουλάχιστον για τρία χρόνια
και με χρέωση όχι μεγαλύτερη από το κόστος της φυσικής διανομής κώδικα,
παράδοσης σε τρίτους του πλήρους, αναγνώσιμου από το σύστημα αντιγράφου του
αντίστοιχου πηγαίου κώδικα, ο οποίος θα διανεμηθεί υπό τους όρους των Ενοτήτων
1 και 2 ως ανωτέρω, σε συνηθισμένο μέσο μεταφοράς λογισμικού - ή,

    γ) Το συνοδεύετε με τις πληροφορίες που λάβατε όσον αφορά την προσφορά
διανομής του αντίστοιχου πηγαίου κώδικα.  (Η εναλλακτική αυτή επιλογή
επιτρέπεται μόνο για μη εμπορική διανομή και μόνο εφόσον λάβατε το πρόγραμμα σε
αντικειμενικό κώδικα ή εκτελέσιμη μορφή με αυτήν την προσφορά, σύμφωνα με την
Υποενότητα [β] παραπάνω.)

Ο πηγαίος κώδικας για ένα έργο συνιστά την προτιμώμενη μορφή του έργου για
πραγματοποίηση τροποποιήσεων σε αυτό.  Για ένα εκτελέσιμο έργο, πλήρης πηγαίος
κώδικας σημαίνει όλον τον πηγαίο κώδικα για όλες τις λειτουργικές μονάδες που
περιλαμβάνει, συν οποιαδήποτε σχετικά αρχεία ορισμού διασύνδεσης, συν τις
δέσμες ενεργειών που χρησιμοποιούνται για τον έλεγχο της μεταγλώττισης και
εγκατάστασης του εκτελέσιμου αρχείου.  Ωστόσο, ως ειδική εξαίρεση, ο πηγαίος
κώδικας που διανέμεται δεν χρειάζεται να περιλαμβάνει οτιδήποτε διανέμεται
κανονικά (είτε ως κώδικας, είτε σε δυαδική μορφή) μαζί με τα μεγαλύτερα
στοιχεία (μεταγλωττιστές, πυρήνας κ.ο.κ.) του λειτουργικού συστήματος στο οποίο
εκτελείται το εκτελέσιμο αρχείο, εκτός εάν το ίδιο το στοιχείο συνοδεύει το
εκτελέσιμο.

Εάν η διανομή του εκτελέσιμου ή του αντικειμενικού κώδικα πραγματοποιείται με
παραχώρηση πρόσβασης για αντιγραφή από καθορισμένη τοποθεσία, τότε η παραχώρηση
ισοδύναμης πρόσβασης για αντιγραφή του πηγαίου κώδικα από την ίδια τοποθεσία
λογίζεται ως διανομή του πηγαίου κώδικα - αν και τα τρίτα μέλη δεν
υποχρεούνται να αντιγράψουν τον πηγαίο κώδικα μαζί με τον αντικειμενικό.

  4. Δεν επιτρέπεται η αντιγραφή, τροποποίηση, παραχώρηση άδειας περαιτέρω
εκμετάλλευσης ή διανομή του Προγράμματος εκτός εάν προβλέπεται ρητά στην
παρούσα άδεια.  Διαφορετικά, κάθε απόπειρα για αντιγραφή, τροποποίηση,
παραχώρηση άδειας εκμετάλλευσης ή διανομή του Προγράμματος είναι άκυρη και
αυτομάτως καταργεί τα δικαιώματα που σας παραχωρεί η παρούσα άδεια.
Ωστόσο, οι άδειες χρήσης των μελών που έχουν λάβει αντίγραφα ή δικαιώματα από
εσάς, μέσω της παρούσας άδειας, δεν θα ακυρωθούν, εφόσον τα μέλη αυτά
παραμένουν πλήρως συμμορφωμένα με τους όρους της άδειας.

  5. Δεν απαιτείται από εσάς να δεχθείτε την παρούσα άδεια, εφόσον δεν την
έχετε υπογράψει.  Ωστόσο, τίποτε άλλο δεν σας δίνει το δικαίωμα να
τροποποιήσετε ή να διανείμετε το Πρόγραμμα ή τα παραγόμενα από αυτό έργα.  Οι
ενέργειες αυτές απαγορεύονται από το νόμο, εάν δεν αποδεχθείτε την παρούσα
άδεια.  Συνεπώς, με το να τροποποιήσετε ή να διανείμετε το Πρόγραμμα (ή
οποιοδήποτε έργο που βασίζεται στο Πρόγραμμα), δηλώνετε ότι αποδέχεστε την
παρούσα άδεια, καθώς και όλους τους όρους και συνθήκες που προβλέπει η άδεια
για την αντιγραφή, διανομή ή τροποποίηση του Προγράμματος ή έργων που
βασίζονται σε αυτό.

  6. Κάθε φορά που αναδιανέμετε το Πρόγραμμα (ή ένα έργο βασισμένο στο
Πρόγραμμα), ο αποδέκτης αυτόματα παραλαμβάνει την αρχική άδεια αντιγραφής,
διανομής ή τροποποίησης του Προγράμματος σύμφωνα με τους όρους και τις συνθήκες
αυτές.  Δεν επιτρέπεται να επιβάλλετε περαιτέρω περιορισμούς στην άσκηση των
δικαιωμάτων του αποδέκτη τα οποία προβλέπονται εδώ. Δεν είστε υπεύθυνοι για το
εάν τρίτα μέλη επιβάλλουν συμμόρφωση σε αυτήν τη άδεια.

  7. Εάν, ως συνέπεια δικαστικής απόφασης ή κατηγορίας για παράβαση νόμου περί
πνευματικής ιδιοκτησίας ή για οποιονδήποτε άλλο λόγο (μη περιοριζόμενο σε
θέματα ευρεσιτεχνίας), σας επιβληθούν όροι (είτε μέσω δικαστικής απόφασης,
συμφωνίας ή μέσω άλλου τρόπου) οι οποίοι αντιβαίνουν τους όρους της παρούσας
άδειας, οι όροι εκείνοι δεν σας απαλλάσσουν από τους όρους της παρούσας.  Εάν
δεν είναι δυνατή η αναδιανομή με τρόπο ώστε να ικανοποιεί συγχρόνως τις
υποχρεώσεις σας σύμφωνα με την παρούσα άδεια και οποιεσδήποτε άλλες υποχρεώσεις
απορρέουν από αυτή, τότε, ως συνέπεια, δεν επιτρέπεται να αναδιανέμετε το
Πρόγραμμα με κανένα τρόπο.  Για παράδειγμα, εάν μια άδεια ευρεσιτεχνίας δεν
επιτρέπει τη χωρίς δικαιώματα εκμετάλλευσης αναδιανομή του Προγράμματος από
όλους όσους λαμβάνουν αντίγραφα άμεσα ή έμμεσα από εσάς, τότε ο μόνος τρόπος με
τον οποίο θα μπορούσατε να ικανοποιήσετε την άδεια εκείνη και την παρούσα άδεια
θα ήταν να αποφύγετε εντελώς την αναδιανομή του Προγράμματος.

Εάν οποιοδήποτε τμήμα αυτής της ενότητας καταστεί άκυρο ή μη δυνάμενο να
επιβληθεί σε κάποια συγκεκριμένη περίπτωση, το υπόλοιπο τμήμα της ενότητας
αυτής εφαρμόζεται και η ενότητα ως σύνολο εφαρμόζεται υπό οποιεσδήποτε
συγκυρίες.

Δεν ανήκει στους σκοπούς της ενότητας αυτής να σας παρακινήσει να παραβιάσετε
την ευρεσιτεχνία ή άλλες αξιώσεις πνευματικής ιδιοκτησίας ή να αμφισβητήσετε
τον κύρος οποιωνδήποτε τέτοιων αξιώσεων. Μοναδικός σκοπός αυτής της ενότητας
είναι να προστατέψει την ακεραιότητα του συστήματος διανομής ελεύθερου
λογισμικού, η οποία υλοποιείται μέσω της πρακτικής των αδειών δημόσιας χρήσης.
Πολλοί άνθρωποι έχουν συνεισφέρει γενναιόδωρα στην ευρεία έκταση του λογισμικού
που διανέμεται μέσω αυτού του συστήματος, εμπιστευόμενοι την συνεπή εφαρμογή
αυτού του συστήματος. Είναι στην ευχέρεια του δημιουργού/δωρητή να αποφασίσει
εάν προτίθεται να διανείμει λογισμικό μέσω οποιουδήποτε άλλου συστήματος, και
μια άδεια δεν είναι δυνατό να επιβάλει αυτήν την επιλογή.

Η ενότητα αυτή έχει ως σκοπό να καταστήσει σαφές ό,τι συνεπάγεται το υπόλοιπο
τμήμα της παρούσας άδειας.

  8. Εάν η διανομή ή/και η χρήση του Προγράμματος εμποδίζεται σε ορισμένες
χώρες, είτε μέσω κατοχυρωμένης ευρεσιτεχνίας είτε μέσω διασυνδέσεων που
προστατεύονται από πνευματικά δικαιώματα, επιτρέπεται στον κάτοχο του αρχικού
πνευματικού δικαιώματος, ο οποίος θέτει το Πρόγραμμα υπό τους όρους της
παρούσας άδειας, να προσθέσει έναν ρητό γεωγραφικό περιορισμό στη διανομή,
εξαιρώντας εκείνες τις χώρες, έτσι ώστε η διανομή να επιτρέπεται μόνο για τις
χώρες οι οποίες δεν εξαιρούνται.  Σε τέτοια περίπτωση, η παρούσα άδεια
ενσωματώνει τον περιορισμό σαν να ήταν διατυπωμένος στο σώμα της παρούσας
άδειας.

  9. Το Ίδρυμα Ελεύθερου Λογισμικού (Free Software Foundation) έχει τη
δυνατότητα περιστασιακά να δημοσιεύει αναθεωρημένες ή/και νέες εκδόσεις της
Γενικής άδειας Δημόσιας Χρήσης.  Αυτές οι νέες εκδόσεις θα είναι συναφείς στο
πνεύμα με την παρούσα έκδοση, όμως ενδέχεται να διαφέρουν στις λεπτομέρειες,
καθώς αναφέρονται σε νέα προβλήματα και ζητήματα.

Σε κάθε έκδοση δίνεται ένας διακριτικός αριθμός έκδοσης.  Εάν στο Πρόγραμμα
καθορίζεται ένας αριθμός έκδοσης της παρούσας άδειας, η οποία ισχύει σε αυτό,
καθώς και "οποιασδήποτε μεταγενέστερης έκδοσης", μπορείτε να επιλέξετε ανάμεσα
στο να ακολουθήσετε τους όρους και τις συνθήκες είτε εκείνης της έκδοσης είτε
οποιασδήποτε άλλης έκδοσης που δημοσιεύεται από το Ίδρυμα Ελεύθερου Λογισμικού
(Free Software Foundation).  Εάν στο Πρόγραμμα δεν καθορίζεται αριθμός έκδοσης
της παρούσας άδειας, μπορείτε να επιλέξετε οποιαδήποτε έκδοση η οποία έχει
δημοσιευθεί από το Ίδρυμα Ελεύθερου Λογισμικού.

  10. Εάν επιθυμείτε να ενσωματώσετε μέρη του Προγράμματος σε άλλα ελεύθερα
προγράμματα, των οποίων οι όροι διανομής είναι διαφορετικοί, επικοινωνήστε με
το δημιουργό του Προγράμματος για να ζητήσετε την έγκρισή του.  Για λογισμικό
του οποίου η πνευματική ιδιοκτησία ανήκει στο Ίδρυμα Ελεύθερου Λογισμικού (Free
Software Foundation), επικοινωνήστε μαζί μας στο Ίδρυμα Ελεύθερου Λογισμικού
(σε ορισμένες περιπτώσεις προβαίνουμε σε εξαιρέσεις).  Η απόφασή μας θα ληφθεί
βάσει του διττού στόχου μας να διατηρήσουμε την ελευθερία όλων των προϊόντων
που παράγονται από το ελεύθερο λογισμικό μας, καθώς και να προωθήσουμε
γενικότερα την κοινή χρήση και τη δυνατότητα επαναχρησιμοποίησης του
λογισμικού.

                            ΚΑΜΙΑ ΕΓΓΥΗΣΗ

  11. ΕΠΕΙΔΗ Η ΑΔΕΙΑ ΧΡΗΣΗΣ ΤΟΥ ΠΡΟΓΡΑΜΜΑΤΟΣ ΠΑΡΕΧΕΤΑΙ ΧΩΡΙΣ ΧΡΕΩΣΗ, ΔΕΝ
ΥΠΑΡΧΕΙ ΕΓΓΥΗΣΗ ΓΙΑ ΤΟ ΠΡΟΓΡΑΜΜΑ, ΣΤΟ ΒΑΘΜΟ ΠΟΥ ΕΠΙΤΡΕΠΕΙ Η ΙΣΧΥΟΥΣΑ ΝΟΜΟΘΕΣΙΑ.
 ΕΦΟΣΟΝ ΔΕΝ ΥΠΑΡΧΕΙ ΔΙΑΦΟΡΕΤΙΚΗ ΕΓΓΡΑΦΗ ΔΗΛΩΣΗ, ΟΙ ΚΑΤΟΧΟΙ ΠΝΕΥΜΑΤΙΚΩΝ
ΔΙΚΑΙΩΜΑΤΩΝ Ή/ΚΑΙ ΑΛΛΕΣ ΠΛΕΥΡΕΣ ΠΑΡΕΧΟΥΝ ΤΟ ΠΡΟΓΡΑΜΜΑ "ΩΣ ΕΧΕΙ" ΧΩΡΙΣ ΚΑΝΕΝΟΣ
ΕΙΔΟΥΣ ΕΓΓΥΗΣΕΙΣ, ΕΙΤΕ ΡΗΤΕΣ ΕΙΤΕ ΕΜΜΕΣΕΣ, ΣΤΙΣ ΟΠΟΙΕΣ ΣΥΜΠΕΡΙΛΑΜΒΑΝΟΝΤΑΙ,
ΕΝΔΕΙΚΤΙΚΑ, ΟΙ ΕΜΜΕΣΕΣ ΕΓΓΥΗΣΕΙΣ ΕΜΠΟΡΕΥΣΙΜΟΤΗΤΑΣ ΚΑΙ ΚΑΤΑΛΛΗΛΟΤΗΤΑΣ.
ΟΠΟΙΟΣΔΗΠΟΤΕ ΚΙΝΔΥΝΟΣ ΑΠΟ ΤΗΝ ΠΟΙΟΤΗΤΑ ΚΑΙ ΤΗΝ ΑΠΟΔΟΣΗ ΤΟΥ ΠΡΟΓΡΑΜΜΑΤΟΣ ΑΝΗΚΕΙ
ΕΞ ΟΛΟΚΛΗΡΟΥ ΕΣΑΣ.  ΕΑΝ ΤΟ ΠΡΟΓΡΑΜΜΑ ΑΠΟΔΕΙΧΘΕΙ ΕΛΑΤΤΩΜΑΤΙΚΟ, ΤΟ ΚΟΣΤΟΣ ΟΛΩΝ
ΤΩΝ ΕΡΓΑΣΙΩΝ ΕΠΙΣΚΕΥΗΣ Ή ΔΙΟΡΘΩΣΗΣ ΒΑΡΥΝΕΙ ΕΣΑΣ.

  12. ΣΕ ΚΑΜΙΑ ΠΕΡΙΠΤΩΣΗ, ΕΚΤΟΣ ΕΑΝ ΑΠΑΙΤΕΙΤΑΙ ΑΠΟ ΤΗΝ ΙΣΧΥΟΥΣΑ ΝΟΜΟΘΕΣΙΑ Ή
ΕΧΕΙ ΣΥΜΦΩΝΗΘΕΙ ΓΡΑΠΤΩΣ, Ο ΚΑΤΟΧΟΣ ΤΩΝ ΠΝΕΥΜΑΤΙΚΩΝ ΔΙΚΑΙΩΜΑΤΩΝ, Ή ΟΠΟΙΟΔΗΠΟΤΕ
ΑΛΛΟ ΜΕΛΟΣ ΤΟ ΟΠΟΙΟ ΜΠΟΡΕΙ ΝΑ ΤΡΟΠΟΠΟΙΗΣΕΙ Ή/ΚΑΙ ΝΑ ΑΝΑΔΙΑΝΕΙΜΕΙ ΤΟ ΠΡΟΓΡΑΜΜΑ
ΟΠΩΣ ΠΡΟΒΛΕΠΕΤΑΙ ΠΑΡΑΠΑΝΩ, ΔΕΝ ΦΕΡΕΤΑΙ ΩΣ ΥΠΕΥΘΥΝΟΣ ΑΠΕΝΑΝΤΙ ΣΑΣ ΓΙΑ ΖΗΜΙΕΣ,
ΣΥΜΠΕΡΙΛΑΜΒΑΝΟΜΕΝΩΝ ΟΛΩΝ ΤΩΝ ΓΕΝΙΚΩΝ, ΕΙΔΙΚΩΝ, ΣΥΜΠΤΩΜΑΤΙΚΩΝ Ή ΣΥΝΕΠΑΚΟΛΟΥΘΩΝ
ΖΗΜΙΩΝ ΠΟΥ ΕΝΔΕΧΕΤΑΙ ΝΑ ΠΡΟΚΥΨΟΥΝ ΛΟΓΩ ΤΗΣ ΧΡΗΣΗΣ Ή ΤΗΣ ΑΔΥΝΑΜΙΑΣ ΧΡΗΣΗΣ ΤΟΥ
ΠΡΟΓΡΑΜΜΑΤΟΣ (ΣΥΜΠΕΡΙΛΑΜΒΑΝΟΜΕΝΩΝ, ΕΝΔΕΙΚΤΙΚΑ, ΤΗΣ ΑΠΩΛΕΙΑΣ ΔΕΔΟΜΕΝΩΝ Ή ΤΗΣ
ΑΛΛΟΙΩΣΗΣ ΤΗΣ ΑΚΡΙΒΕΙΑΣ ΤΟΥΣ, Ή ΑΠΩΛΕΙΑΣ ΠΟΥ ΕΠΗΛΘΕ ΑΠΟ ΕΣΑΣ Ή ΑΠΟ ΤΡΙΤΑ ΜΕΛΗ,
Ή ΑΔΥΝΑΜΙΑΣ ΤΟΥ ΠΡΟΓΡΑΜΜΑΤΟΣ ΝΑ ΛΕΙΤΟΥΡΓΗΣΕΙ ΜΕ ΑΛΛΑ ΠΡΟΓΡΑΜΜΑΤΑ), ΕΣΤΩ ΚΑΙ ΑΝ
Ο ΚΑΤΟΧΟΣ ΑΥΤΟΣ Ή ΤΟ ΑΛΛΟ ΜΕΛΟΣ ΕΧΕΙ ΕΝΗΜΕΡΩΘΕΙ ΓΙΑ ΤΟ ΕΝΔΕΧΟΜΕΝΟ ΤΕΤΟΙΩΝ
ΖΗΜΙΩΝ.


		     ΤΕΛΟΣ ΤΩΝ ΟΡΩΝ ΚΑΙ ΤΩΝ ΣΥΝΘΗΚΩΝ
"""
    else:
        lic = """\
		    GNU GENERAL PUBLIC LICENSE
		       Version 2, June 1991

 Copyright (C) 1989, 1991 Free Software Foundation, Inc.
                       59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

			    Preamble

  The licenses for most software are designed to take away your
freedom to share and change it.  By contrast, the GNU General Public
License is intended to guarantee your freedom to share and change free
software--to make sure the software is free for all its users.  This
General Public License applies to most of the Free Software
Foundation's software and to any other program whose authors commit to
using it.  (Some other Free Software Foundation software is covered by
the GNU Library General Public License instead.)  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
this service if you wish), that you receive source code or can get it
if you want it, that you can change the software or use pieces of it
in new free programs; and that you know you can do these things.

  To protect your rights, we need to make restrictions that forbid
anyone to deny you these rights or to ask you to surrender the rights.
These restrictions translate to certain responsibilities for you if you
distribute copies of the software, or if you modify it.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must give the recipients all the rights that
you have.  You must make sure that they, too, receive or can get the
source code.  And you must show them these terms so they know their
rights.

  We protect your rights with two steps: (1) copyright the software, and
(2) offer you this license which gives you legal permission to copy,
distribute and/or modify the software.

  Also, for each author's protection and ours, we want to make certain
that everyone understands that there is no warranty for this free
software.  If the software is modified by someone else and passed on, we
want its recipients to know that what they have is not the original, so
that any problems introduced by others will not reflect on the original
authors' reputations.

  Finally, any free program is threatened constantly by software
patents.  We wish to avoid the danger that redistributors of a free
program will individually obtain patent licenses, in effect making the
program proprietary.  To prevent this, we have made it clear that any
patent must be licensed for everyone's free use or not licensed at all.

  The precise terms and conditions for copying, distribution and
modification follow.

		    GNU GENERAL PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. This License applies to any program or other work which contains
a notice placed by the copyright holder saying it may be distributed
under the terms of this General Public License.  The "Program", below,
refers to any such program or work, and a "work based on the Program"
means either the Program or any derivative work under copyright law:
that is to say, a work containing the Program or a portion of it,
either verbatim or with modifications and/or translated into another
language.  (Hereinafter, translation is included without limitation in
the term "modification".)  Each licensee is addressed as "you".

Activities other than copying, distribution and modification are not
covered by this License; they are outside its scope.  The act of
running the Program is not restricted, and the output from the Program
is covered only if its contents constitute a work based on the
Program (independent of having been made by running the Program).
Whether that is true depends on what the Program does.

  1. You may copy and distribute verbatim copies of the Program's
source code as you receive it, in any medium, provided that you
conspicuously and appropriately publish on each copy an appropriate
copyright notice and disclaimer of warranty; keep intact all the
notices that refer to this License and to the absence of any warranty;
and give any other recipients of the Program a copy of this License
along with the Program.

You may charge a fee for the physical act of transferring a copy, and
you may at your option offer warranty protection in exchange for a fee.

  2. You may modify your copy or copies of the Program or any portion
of it, thus forming a work based on the Program, and copy and
distribute such modifications or work under the terms of Section 1
above, provided that you also meet all of these conditions:

    a) You must cause the modified files to carry prominent notices
    stating that you changed the files and the date of any change.

    b) You must cause any work that you distribute or publish, that in
    whole or in part contains or is derived from the Program or any
    part thereof, to be licensed as a whole at no charge to all third
    parties under the terms of this License.

    c) If the modified program normally reads commands interactively
    when run, you must cause it, when started running for such
    interactive use in the most ordinary way, to print or display an
    announcement including an appropriate copyright notice and a
    notice that there is no warranty (or else, saying that you provide
    a warranty) and that users may redistribute the program under
    these conditions, and telling the user how to view a copy of this
    License.  (Exception: if the Program itself is interactive but
    does not normally print such an announcement, your work based on
    the Program is not required to print an announcement.)

These requirements apply to the modified work as a whole.  If
identifiable sections of that work are not derived from the Program,
and can be reasonably considered independent and separate works in
themselves, then this License, and its terms, do not apply to those
sections when you distribute them as separate works.  But when you
distribute the same sections as part of a whole which is a work based
on the Program, the distribution of the whole must be on the terms of
this License, whose permissions for other licensees extend to the
entire whole, and thus to each and every part regardless of who wrote it.

Thus, it is not the intent of this section to claim rights or contest
your rights to work written entirely by you; rather, the intent is to
exercise the right to control the distribution of derivative or
collective works based on the Program.

In addition, mere aggregation of another work not based on the Program
with the Program (or with a work based on the Program) on a volume of
a storage or distribution medium does not bring the other work under
the scope of this License.

  3. You may copy and distribute the Program (or a work based on it,
under Section 2) in object code or executable form under the terms of
Sections 1 and 2 above provided that you also do one of the following:

    a) Accompany it with the complete corresponding machine-readable
    source code, which must be distributed under the terms of Sections
    1 and 2 above on a medium customarily used for software interchange; or,

    b) Accompany it with a written offer, valid for at least three
    years, to give any third party, for a charge no more than your
    cost of physically performing source distribution, a complete
    machine-readable copy of the corresponding source code, to be
    distributed under the terms of Sections 1 and 2 above on a medium
    customarily used for software interchange; or,

    c) Accompany it with the information you received as to the offer
    to distribute corresponding source code.  (This alternative is
    allowed only for noncommercial distribution and only if you
    received the program in object code or executable form with such
    an offer, in accord with Subsection b above.)

The source code for a work means the preferred form of the work for
making modifications to it.  For an executable work, complete source
code means all the source code for all modules it contains, plus any
associated interface definition files, plus the scripts used to
control compilation and installation of the executable.  However, as a
special exception, the source code distributed need not include
anything that is normally distributed (in either source or binary
form) with the major components (compiler, kernel, and so on) of the
operating system on which the executable runs, unless that component
itself accompanies the executable.

If distribution of executable or object code is made by offering
access to copy from a designated place, then offering equivalent
access to copy the source code from the same place counts as
distribution of the source code, even though third parties are not
compelled to copy the source along with the object code.

  4. You may not copy, modify, sublicense, or distribute the Program
except as expressly provided under this License.  Any attempt
otherwise to copy, modify, sublicense or distribute the Program is
void, and will automatically terminate your rights under this License.
However, parties who have received copies, or rights, from you under
this License will not have their licenses terminated so long as such
parties remain in full compliance.

  5. You are not required to accept this License, since you have not
signed it.  However, nothing else grants you permission to modify or
distribute the Program or its derivative works.  These actions are
prohibited by law if you do not accept this License.  Therefore, by
modifying or distributing the Program (or any work based on the
Program), you indicate your acceptance of this License to do so, and
all its terms and conditions for copying, distributing or modifying
the Program or works based on it.

  6. Each time you redistribute the Program (or any work based on the
Program), the recipient automatically receives a license from the
original licensor to copy, distribute or modify the Program subject to
these terms and conditions.  You may not impose any further
restrictions on the recipients' exercise of the rights granted herein.
You are not responsible for enforcing compliance by third parties to
this License.

  7. If, as a consequence of a court judgment or allegation of patent
infringement or for any other reason (not limited to patent issues),
conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot
distribute so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you
may not distribute the Program at all.  For example, if a patent
license would not permit royalty-free redistribution of the Program by
all those who receive copies directly or indirectly through you, then
the only way you could satisfy both it and this License would be to
refrain entirely from distribution of the Program.

If any portion of this section is held invalid or unenforceable under
any particular circumstance, the balance of the section is intended to
apply and the section as a whole is intended to apply in other
circumstances.

It is not the purpose of this section to induce you to infringe any
patents or other property right claims or to contest validity of any
such claims; this section has the sole purpose of protecting the
integrity of the free software distribution system, which is
implemented by public license practices.  Many people have made
generous contributions to the wide range of software distributed
through that system in reliance on consistent application of that
system; it is up to the author/donor to decide if he or she is willing
to distribute software through any other system and a licensee cannot
impose that choice.

This section is intended to make thoroughly clear what is believed to
be a consequence of the rest of this License.

  8. If the distribution and/or use of the Program is restricted in
certain countries either by patents or by copyrighted interfaces, the
original copyright holder who places the Program under this License
may add an explicit geographical distribution limitation excluding
those countries, so that distribution is permitted only in or among
countries not thus excluded.  In such case, this License incorporates
the limitation as if written in the body of this License.

  9. The Free Software Foundation may publish revised and/or new versions
of the General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

Each version is given a distinguishing version number.  If the Program
specifies a version number of this License which applies to it and "any
later version", you have the option of following the terms and conditions
either of that version or of any later version published by the Free
Software Foundation.  If the Program does not specify a version number of
this License, you may choose any version ever published by the Free Software
Foundation.

  10. If you wish to incorporate parts of the Program into other free
programs whose distribution conditions are different, write to the author
to ask for permission.  For software which is copyrighted by the Free
Software Foundation, write to the Free Software Foundation; we sometimes
make exceptions for this.  Our decision will be guided by the two goals
of preserving the free status of all derivatives of our free software and
of promoting the sharing and reuse of software generally.

			    NO WARRANTY

  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
REPAIR OR CORRECTION.

  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.

		     END OF TERMS AND CONDITIONS
"""

    return [lic_name, lic_short, lic]

#===========================================================================

def STAMOS_INTERNAL(lang=-1) -> List[str]:        #lang==-1 ->Greek, lang==-2 -> English
    lic_name = "Stamos Internal License"
    if lang == -1:
        lic_short = u"""\
    Το πρόγραμμα αποτελεί πνευματική ιδιοκτησία του Δρ. Θανάση Στάμου. Το πρόγραμμα
συντάχθηκε για ιδία χρήση, δηλαδή για χρήση από το Δρ. Θανάση Στάμο και τους
συνεργάτες του (για όσο διαρκεί η συνεργασία), στους υπολογιστές και στα γραφεία
του ιδίου και των συνεργατών του.
    Το πρόγραμμα δεν είναι εμπορικό και ΑΠΑΓΟΡΕΥΕΤΑΙ η χρήση του προγράμματος
από οποιονδήποτε άλλο σε οποιοδήποτε άλλο μέρος. Εκτός των άλλων,
ΑΠΑΓΟΡΕΥΕΤΑΙ και η αντιγραφή, μεταβίβαση, πώληση, ενοικίαση, leasing ή άλλη
χρήση του προγράμματος προς αποκόμιση άμεσου ή έμμεσου οικονομικού οφέλους."""
        lic = lic_short
    else:
        lic_short = u"""\
    This program is intellectual property of Dr. Thanasis Stamos. The program was
written for internal use, and it may only be used by Dr. Thanasis Stamos and his
associates (for the time that the association exists), in the computers of
Dr. Thanasis Stamos and his associates.
    The program is not commercial and use of the program by anyone else in any
other place is strictly prohibited. The program can not, by any means, be sold,
rented, leased, copied or transfered to.
"""
        lic = lic_short
    return [lic_name, lic_short, lic]

#===========================================================================

def STAMOS_COM(lang=-1) -> List[str]:        #lang==-1 ->Greek, lang==-2 -> English
    lic_name = "Stamos Commercial License"
    if lang == -1:
        lic_short = u"""\
    Το πρόγραμμα αποτελεί πνευματική ιδιοκτησία του Δρ. Θανάση Στάμου. Το πρόγραμμα
συντάχθηκε για ιδία χρήση, δηλαδή για χρήση από το Δρ. Θανάση Στάμο και τους
συνεργάτες του (για όσο διαρκεί η συνεργασία), στους υπολογιστές και στα γραφεία
του ιδίου και των συνεργατών του.
    Το πρόγραμμα δεν είναι εμπορικό και ΑΠΑΓΟΡΕΥΕΤΑΙ η χρήση του προγράμματος
από οποιονδήποτε άλλο σε οποιοδήποτε άλλο μέρος. Εκτός των άλλων,
ΑΠΑΓΟΡΕΥΕΤΑΙ και η αντιγραφή, μεταβίβαση, πώληση, ενοικίαση, leasing ή άλλη
χρήση του προγράμματος προς αποκόμιση άμεσου ή έμμεσου οικονομικού οφέλους."""
        lic = lic_short
    else:
        lic_short = u"""\
    This program is intellectual property of Dr. Thanasis Stamos (copyright holder) and
is protected by Greek law and international treaties.

Provided that the Licensee of this program has paid the license fees, the Licensee:
1. Gets a non-exclusive license to use this program.
2. May install the program at most 3 computers which belong to the Licensee.
3. May not execute the program in more than 1 computers at the same time.

Other than allowed by this license, the use of the program by anyone else in any
other computers is strictly prohibited. The program can not, by any means, be sold,
rented, leased, copied or transfered to.

    The Licensee agrees that he/she will use this program according to Greek law
and/or any other jurisdiction that may apply to the Licensee. If the program
is used against the law, the sole responsible for any consequences is the
Licensee; the Licensee agrees that the copyright holder can not be held
repsonsible in any way.

THE PROGRAM IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH THE LICENSOR. SHOULD THE
PROGRAM PROVE DEFECTIVE, THE LICENSOR ASSUMES THE COST OF ALL NECESSARY SERVICING,
REPAIR OR CORRECTION.

IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, BE LIABLE TO YOU FOR DAMAGES,
INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.
"""
        lic = lic_short
    return [lic_name, lic_short, lic]
