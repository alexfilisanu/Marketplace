Filisanu Mihai-Alexandru
334CB

Tema 1 - Marketplace

Implementare:

    - clasa Producer: ma folosesc de metoda register_producer() pentru a inregistra
un nou producator, iar, ulterior, produc cate produse se cer, si incerc publicarea
lor cu ajutorul metodei publish() pana cand toate produsele sunt adaugate

    - clasa Consumer: ma folosesc de metoda new_cart() pentru a crea un nou cos de
cumparaturi, iar in functie de tipul operatiei add/remove folosesc metodele
add_to_cart()/remove_from_cart() - in cazul add este posibil ca operatia sa nu fie
disponibila de la inceput, asa ca o sa incerc pana cand este realizata; la finalul
operatiilor folosesc metoda place_order() pentru a obtine o lista cu toate produsele,
pe care ulterior le afisez

    - clasa Marketplace: - in aceasta clasa sunt definite toate metodele mentionate mai
sus - implementarea lor contine si comentarii sugestive; 
                         - ca structuri de date folosesc producers_dictionary care este 
un dict cu key: producer_id si value: lista de produse ale acelui producer si 
carts_dictionary care este un dict cu key: cart_id si value: o lista cu elemente de 
forma (producer_id, product) pentru a retine al carui producator este produsul din 
cos in cazul eliminarii acestuia din cos; 
                         - ca elemente de sincronizare folosesc 4 Lock uri: 
register_producer_lock, publish_lock, add_to_cart_lock, new_cart_lock folosite in 
metodele care au acelasi nume;
                         - am folosit si logger pentru a afisa toate intrarile si 
iesirile in/din metodele clasei;

    - clasa TestMarketplace: contine unittests pentru toate metodele definite in
clasa Marketplace, iar pentru publish() si add_to_cart() cate 2 teste care sa testeze
atat functionalitatea normala(atunci cand este expected sa return true), cat si cea 
in care metoda returneaza false si se reapeleaza dupa un timp de asteptare

    Intregul enunt al temei este implementat, atat parte de logger, cat si ce de unittests.
La rularea locala toate testele sunt PASSED si nu exista erori de pylint.

Resurse utilizate:
    - Labaratoare ASC
    - Laboratoare APD

Git:
    - https://github.com/alexfilisanu/Marketplace/tree/main/skel/tema
