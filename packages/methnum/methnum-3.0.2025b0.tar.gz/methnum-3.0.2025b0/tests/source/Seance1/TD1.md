---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

+++ {"nbgrader": {"grade": false, "grade_id": "cell-64cc25cccda49f37", "locked": true, "schema_version": 3, "solution": false, "task": false}}

# TP 1 : Généralités sur Linux et Python

+++ {"nbgrader": {"grade": false, "grade_id": "cell-b060c535f91928c4", "locked": true, "schema_version": 3, "solution": false, "task": false}}

**Durant tout ce cours, vous écrirez vos propres programmes dans ce Jupyter Notebook.**

## Hello, World!

Dans la cellule suivante, effacez `"#LA REPONSE ICI"` et écrivez  un programme qui affiche à l'écran *Hello, World!*  Vous n'êtes certainement pas le premier à le faire.](https://en.wikipedia.org/wiki/%22Hello,_World!%22_program)

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-17c81655a466eff1
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
print('Hello, World!')
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-4d824e0e7f9d9cde", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## Exercice 1 : Déclarations et types

Déclarez trois variables `n`, `x`, `c` respectivement de type `int`, `float` et `str` initialisées aux valeurs que vous voulez. À l'aide de `print`, affichez une phrase donnant le type de ces trois variables.

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-635343fa6b8a26fa
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
#TP1 exo3
#on demande un entier un nombre décimal et une chaîne de caractères
n = 42
x = 42.0
c = "MethNum"

print(n, 'est de type', type(n))
print(x, 'est de type', type(x))
print(c, 'est de type', type(c))
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-1298aaa681e184b4", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## Exercice 2 : Un peu de mathématiques...

Écrire un programme qui :
1. déclare un angle en degrés, le convertit en radians et l'affiche à l'écran.
2. déclare un angle en radians, le convertit en degrés et l'affiche à l'écran.
Tester le programme avec $\pi/4$, alias $45$°. On pourra impoter `pi` depuis la librairie [`math`](https://docs.python.org/3/library/math.html).

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-7bcf63f282d8b3be
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
#TP1 exercice 4 conversion d'angles radian--> degré et degré --> radians
from numpy import pi
angd=45
angr1=angd*pi/180
print('un angle de ', angd,'degrés vaut',angr1,'radians')

angr=pi/4
angd1=angr*180/pi
print('un angle de ', angr,'radians vaut',angd1,'degrés')
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-dfc31618024b2380", "locked": true, "schema_version": 3, "solution": false, "task": false}}

3. Écrire un programme qui somme deux nombres `a` et `b` et affiche la somme `a+b` de façon élégante (par exemple $2+3=5$).

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-861895e1bd017628
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
x1=3
x2=2.5
print(x1,'+',x2,' = ',x1+x2)
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-69326c1c6a3fd0bb", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## Exercice 3 : Âge
Écrire un programme qui calcule votre âge à la date d'aujourd'hui en jours (on arrondira un mois à 30 jours et une année à 365 jours).

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-b0c3d5ec83d666f5
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
#on demande l'année de nassance et on calcule l'age
jour, mois, annee  = 11, 12, 1987
jour2, mois2, annee2 = 2, 2, 2022
annee3 = annee2 - annee
mois3 = mois2 - mois
jour3 = jour2 - jour
print('Vous avez',annee3, 'ans', mois3, 'mois et',jour3,'jours, soit', annee3*365+mois3*30+jour3,'jours.')
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-ea37295cc5ce6d5d", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## Exercice 4 : Distance euclidienne
Écrire un programme qui déclare les coordonnées de deux points $A=(x_A,y_A)$ et $B=(x_B, y_B)$ dans le plan et qui calcule puis affiche la distance entre ces deux points selon la formule :
$$
d = \sqrt{(x_B-x_A)^2+(y_B-y_A)^2}.
$$
La racine carrée sera importée depuis la librairie [`math`](https://docs.python.org/3/library/math.html). Afficher un résultat arrondi à 3 décimales avec [`round`](https://docs.python.org/fr/3.7/library/functions.html?highlight=round).

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-98b763364c6264df
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
from numpy import sqrt
xA, yA = 3, 5
xB, yB = 4, 2

dist=(xB-xA)**2+(yB-yA)**2
dist=sqrt(dist)
print('La distance est :',round(dist,3))
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-e1183321404b643f", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## Exercice 5  : Fonctions inverses

Vérifier en python pour quelques x les relations mathématiques suivantes :
1. $\ln(\exp(x)) = x$
1. $\sqrt{x^2} = x$
1. $\arccos(\cos(x)) = x$
Rechercher ces différentes fonctions à l'aide de la documentation en ligne ou via la fonction `help`.

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-352f01955b2c25ff
  locked: false
  points: 0
  schema_version: 3
  solution: true
  task: false
---
### BEGIN SOLUTION
from numpy import log, exp, sqrt, arccos, cos

x = 0
print(log(exp(x)))
print(sqrt(x**2))
print(arccos(cos(x)))
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-9c2fc54b9cae769c", "locked": true, "points": 0, "schema_version": 3, "solution": false, "task": true}}

## Exercice 6 : Division euclidienne

1. Stocker un nombre entier quelconque dans une variable, et à l'aide de l'opérateur `%` écrire un petit calcul pour vérifier si celui-ci est impair ou pair.

```{code-cell}
---
nbgrader:
  grade: false
  grade_id: cell-feacf93a4e4d7bf9
  locked: false
  schema_version: 3
  solution: true
  task: false
---
### BEGIN SOLUTION
a = 42
reste = a % 2
print(reste)
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-49601ffb37b8d96a", "locked": true, "points": 0, "schema_version": 3, "solution": false, "task": true}}

2. Diviser un nombre entier quelconque par un autre nombre entier quelconque à l'aide de l'opérateur division `/` et par l'opérateur division euclidienne `//`. Vérifier le résultat et le type du résultat. En particulier tester un cas où l'un est divisible oar l'autre.

```{code-cell}
---
nbgrader:
  grade: false
  grade_id: cell-b9f3ca642dc30efe
  locked: false
  schema_version: 3
  solution: true
  task: false
---
### BEGIN SOLUTION
a = 20
b = 12
print("a/b =", a/b, type(a/b))
print("a//b =", a//b, type(a//b))
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-e183316fc3513187", "locked": true, "points": 0, "schema_version": 3, "solution": false, "task": true}}

3. Ecrire un petit code qui réalise la division euclidienne d'un nombre entier par un autre et affiche quotient et reste.

```{code-cell}
---
nbgrader:
  grade: false
  grade_id: cell-87760f92b8ef6dde
  locked: false
  schema_version: 3
  solution: true
  task: false
---
### BEGIN SOLUTION
a = 42
b = 5
print(a,'//',b,': quotient =', a//b, ' reste =', a%b)
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-a9ce133a0e6b1c9b", "locked": true, "schema_version": 3, "solution": false, "task": false}}

 ## Exercice 7 : Nombres complexes

1. Écrire un programme qui ajoute, soustrait, multiplie et divise des nombres complexes. Vérifier les résultats.

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-2b114f80eaa168c3
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
#calcul de la somme a+b
a=4+5j
b=1-2j
c=a+b
print('somme de ',a,' et ',b,' : ',c)
#calcul de la différence a-b
d=a-b
print('différence ',a,' et ',b,' : ',d)
#calcul du produit a*b
e=a*b
print('produit ',a,' et ',b,' : ',e)
#calcul de la division a/b
f=a/b
#f=complex(round(f.real,3),round(f.imag,3))
print('division ',a,' et ',b,' : ',f)
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-15604f51fd778d0a", "locked": true, "schema_version": 3, "solution": false, "task": false}}

2. Écrire un programme qui déclare deux nombres, forme un nombre complexe avec ceux-ci (partie réelle et partie imaginaire) (voir [ce tutoriel](https://www.programiz.com/python-programming/methods/built-in/complex) par exemple), puis affiche le nombre complexe, sa partie réelle et sa partie imaginaire.

En Python, le nombre imaginaire $i$ est représenté par `j`.

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-e9187b99a92c0f6f
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
x,y=4,5
a=complex(x, y)
print('nombre complexe: ',a,': partie réelle: ',a.real,' partie imaginaire: ',a.imag)
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-7017891d6e7989d9", "locked": true, "schema_version": 3, "solution": false, "task": false}}

3. Écrire un programme qui d'un nombre complexe calcule son module grâce à la fonction [`abs`](https://docs.python.org/3/library/functions.html#abs) et son argument grâce à la fonction arctangente [`arctan`](https://numpy.org/doc/stable/reference/generated/numpy.arctan.html). La partie réelle d'un nombre complexe `z` est accessible via l'attribut `real`: `z.real`, et sa partie imaginaire via l'attribut `imag`. Vérifier le résultat avec $(1+i)/\sqrt{2}$.

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-4e3509939ab7f67e
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
#calcul du module r et de l'argument phi
from numpy import sqrt, arctan
z=(1+1j)/sqrt(2)
r=abs(z)
phi=arctan(z.imag/z.real)
print(z,' module: ', r, ' argument', phi*180/pi)
#l'argument est arctan(b/a)
print(arctan(1))
### END SOLUTION
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-d5fe0885191d9aee", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## Exercice 8 : À vol d'oiseau

Écrire un programme qui calcule la distance entre deux points à la surface de la Terre à partir de leurs latitudes $\phi_A,\ \phi_B$ et longitudes $\lambda_A,\ \lambda_B$. En coordonnées sphériques, la distance **angulaire**, $\theta_{AB}$, entre ces deux points est telle que:
\begin{equation*}
\cos\theta_{AB} = \sin\phi_A\sin\phi_B + \cos\phi_A\cos\phi_B\cos(\lambda_B-\lambda_A)
\end{equation*}

Paris, Londres et New-York sont respectivement situées aux coordonnées ($48.86^\circ$ N, $2.35^\circ$ E), ($51.51^\circ$ N, $0.13^\circ$ W) et ($40.71^\circ$ N, $74.01^\circ$ W). Calculer la distance entre Paris et Londres puis entre Paris et New York (attention aux signes, attention aussi à la donnée manquante).

La distance à vol d'oiseau entre Paris et Londres est d'environ 344 km et celle entre Paris et New-York d'environ 5681 km. Vos résultats sont-ils cohérents ? Expliquez les éventuelles différences.

```{code-cell}
---
nbgrader:
  grade: true
  grade_id: cell-07c5ad63443ed0e5
  locked: false
  points: 0
  schema_version: 3
  solution: true
---
### BEGIN SOLUTION
from numpy import radians,degrees,cos,sin,arccos
pparis=48.86
ppa=radians(pparis)
lparis=2.35
lpa=radians(lparis)
plondres=51.51
plo=radians(plondres)
llondres=-0.13
llo=radians(llondres)
pnewyork=40.71
pne=radians(pnewyork)
lnewyork=-74.01
lne=radians(lnewyork)
rterre= 6371
dist12=rterre*arccos(sin(ppa)*sin(plo)+cos(ppa)*cos(plo)*cos(llo-lpa))
print('distance Paris Londres: ',int(dist12), ' km')
dist12=rterre*arccos(sin(ppa)*sin(pne)+cos(ppa)*cos(pne)*cos(lne-lpa))
print('distance Paris New-york: ',int(dist12), ' km')
print(arccos(sin(ppa)*sin(plo)+cos(ppa)*cos(plo)*cos(llo-lpa)),arccos(sin(ppa)*sin(pne)+cos(ppa)*cos(pne)*cos(lne-lpa) ))
### END SOLUTION
```

+++ {"nbgrader": {"grade": true, "grade_id": "cell-f7bf94b1fb4a484a", "locked": false, "points": 0, "schema_version": 3, "solution": true, "task": false}}

### BEGIN SOLUTION

Les distances diffèrent car la Terre n'est pas parfaitement ronde mais un peu aplatie aux pôles, or nous avons fait l'hypothèse implicitement que la Terre est parfaitement sphérique avec les formules qui sont données. Cela se voit en particulier pour les longues distances.

### END SOLUTION

+++ {"nbgrader": {"grade": false, "grade_id": "cell-0a4ed2f8651b379c", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## $(\star\!\star\!\star)$ Pour aller plus loin...

Les notebooks Jupyter ne sont pas la seule facçon de coder, loin de là ! Ils ont l'avantage d'être simple pour démarrer l'apprentissage d'un langage de programmation, mais pour des usages plus avancés il est préférable de coder soi-même des scripts ou des librairies python, sous la forme de fichiers textes.

## Exercice 9 :  B.A. BA du shell et d'un script python

Cet exercice explore la capacité du **terminal de l'ordinateur sous Linux** (pas celui du JupyterHub, ni sur Windows).

1. Se déplacer dans le terminal : ouvrir un terminal **en local sur l'ordinateur**. Taper la commande `pwd` pour connaître la position actuelle dans l'arborescence des fichiers.
2. À l’aide de la commande `cd MethNum` vous pouvez vous rendre dans le dossier `MethNum`. Taper de nouveau `pwd` pour le vérifier.
3. La commande `ls` permet de visualiser le contenu de ce dossier, `ls -lhrt` donne plus d'informations.
4. Avec `mkdir mon_dossier`, créer un dossier `TP1`.
5. Télécharger le code `double_pendulum_animated.py` depuis l’adresse http://matplotlib.org/examples/animation/double_pendulum_animated.py par la commande:
`wget http://matplotlib.org/examples/animation/double_pendulum_animated.py`
6. Déplacer le fichier `double_pendulum_animated.py` dans le dossier `MethNum/TP1`, avec la commande `mv fichier mon_dossier/`
7. Dans le terminal toujours, se rendre dans le dossier `MethNum/TP1` avec la commande `cd mon_dossier`.
8. Exécuter le code python à l’aide de la commande `python double_pendulum_animated.py`.
9. Ouvrir le fichier par la commande `spyder double_pendulum_animated.py` et constatez que cette simulation d'un double pendule et la création d'un graphique animé prend à peine 100 lignes de code, bien aérées et commentées. Vous pouvez alors fermer la fenêtre.

+++ {"nbgrader": {"grade": false, "grade_id": "cell-1b3814731bbdd74e", "locked": true, "schema_version": 3, "solution": false, "task": false}}

## Exercice 10 : L'interpréteur Python
Voici quelques commandes pour commencer à utiliser l'interpréteur. Dans un terminal, tapez `python`. Cherchez à comprendre le résultat obtenu et les éventuels messages d'erreur.

a) Affectation d'une variable.
```python
x=10
y=5
x+y
```

+++ {"nbgrader": {"grade": false, "grade_id": "cell-d0dbee6c096a3ec4", "locked": true, "schema_version": 3, "solution": false, "task": false}}

b) Fonctions mathématiques: tapez les commandes suivantes et observez les résultats. Tapez sur la lettre Q pour quitter l'aide après le `help(math)`.
```python
import numpy as np
np.pi
np.sin(2.5)**2+np.cos(2.5)**2
np.exp(np.log(3))
np.sqrt(-1)
```

```{code-cell}

```
