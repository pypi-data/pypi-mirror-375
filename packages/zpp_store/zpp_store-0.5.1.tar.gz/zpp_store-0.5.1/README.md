# zpp_store

## Informations

Outil de s�rialisation d'objet Python.
Il peut prendre en charge:
- les formats classiques: str, int, float, bool, type, none, complex, bytes, decimal
- les formats structur�s: list, dict, tuple, array, bytearray, frozenset
- les formats io: BytesIO, StringIO, TextIOWrapper, BufferedReader
- les objets: Class, datetime, function, builtin function

Le fichier de sortie peut-�tre soit un yaml, soit un fichier binaire; et celui-ci peut �tre chiffr� avec un mot de passe.
Le syst�me fonctionne comme un coffre dans lequel on peut stocker plusieurs donn�es et utilise le syst�me cl�/valeur pour identifier les donn�es.

Il int�gre �galement un outil pour stocker des donn�es sous forme de Class pour les structurer et faciliter leurs manipulations.

### Pr�requis
- Python 3

## Installation


```shell
pip install zpp_store
```

## Utilisation
### Initialisation du connecteur

Le store est accessible de deux fa�ons:
- En initialisant le store dans une variable
```python
import zpp_store

vault = zpp_store.Store()
```
- Ou avec la m�thode **with**
```python
import zpp_store

with zpp_store.Store() as vault:
	'''Traitement'''
```

La Classe Store peut prendre plusieurs arguments:
- ***filename***: pour sp�cifier le fichier de sortie
	Si le fichier de sortie n'est pas pr�cis�, le r�sultat restera dans le stockage de la classe. Il sera alors possible de r�cup�rer le r�sultat avec la m�thode **get_content()**
- ***protected***: pour sp�cifier si le fichier doit �tre chiffr� (si le mot de passe n'est pas sp�cifi�. Un prompt demandera le mot de passe)
- ***password***: pour sp�cifier le mot de passe pour le chiffrement (active protected)
- ***format***: pour sp�cifier le format de sortie. **zpp_store.Formatstore.to_yaml**, **zpp_store.Formatstore.to_binary** ou **zpp_store.Formatstore.to_dict**. 
	Attention, le format to_dict n'accepte pas la sortie dans un fichier.
<br>

###  S�rialisation de donn�es

Pour s�rialiser des donn�es, il suffit d'appeler la classe **Store** et d'utiliser la m�thode **push** avec comme param�tre le nom de la cl� � utiliser et la donn�e � s�rialiser.

```python
import zpp_store

class Person:
	def __init__(self, name, age, city):
		self.name = name
		self.age = age
		self.city = city

new_person = Person("Bob", 35, "Paris")

with zpp_store.Store() as vault:
	vault.push("utilisateur_bob", new_person)
```

Possibilit� de travailler avec des donn�es hi�rarchiques en s�parant les cl�s par un point.
```python
vault.push("config.app.data", "data_line")  #Ce qui donnera {"config": {"app": {"data": "data_line"}}}
```

<br>

###  D�s�rialisation de donn�es

Pour d�s�rialiser des donn�es, il suffit d'appeler la classe **Store** et d'utiliser la m�thode **pull** avec comme param�tre le nom de la cl� � r�cup�rer.

```python
import zpp_store

class Person:
	def __init__(self, name, age, city):
		self.name = name
		self.age = age
		self.city = city

with zpp_store.Store() as vault:
	new_person = vault.pull("utilisateur_bob")
```
<br>

### Suppression de donn�es

Il est possible de supprimer des donn�es avec la m�thode **erase()** en pr�cisant en param�tre la cl�.

```python
import zpp_store

with zpp_store.Store() as vault:
	vault.erase("utilisateur_bob")
```

La m�thode retournera alors **True** si une donn�e a �t� supprim�e, sinon **False**.
<br>

### Liste des cl�s

Il est possible de lister l'ensemble des cl�s disponibles dans un store.

```python
import zpp_store

with zpp_store.Store() as vault:
	print(vault.list()) # Affiche: ['app', 'app.config', 'app.users']
```

### Structuration de donn�es

Il est possible de structurer un dictionnaire pour le transformer en **DataStore** et pour nous permettre de manipuler ces donn�es comme une Class avec a.b.c
Pour cela, il nous suffit d'appeler la m�thode **structure()** avec comme argument le dictionnaire

```python
import zpp_store

dict_data = {"Bonjour": "Hello world", "Data": {"insert": True, "false": True}}

data = zpp_store.structure(dict_data)
```

Le dictionnaire devient alors un **zpp_store.structure.DataStore**

Pour permettre de contr�ler la modification, le DataStore permet de r�cup�rer un hash du contenu avec la m�thode **get_hash()**

```python
import zpp_store

dict_data = {"Bonjour": "Hello world", "Data": {"insert": True, "false": True}}

data = zpp_store.structure(dict_data)
hash_dict = data.get_hash()
```
<br>

### D�structuration de donn�es

Pour r�cup�rer un dictionnaire � partir d'un **DataStore**, il suffit d'appeler la m�thode **destructure()**.

```python
import zpp_store

data = zpp_store.destructure(datastore)
```