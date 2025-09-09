from hashlib import sha256
import json
from .store import Formatstore, Store
import msgpack

class DataStore:
    def __repr__(self):
        return f"{feed_dict({}, self)}"

    def __str__(self):
        return self.__repr__()

    def __setattr__(self, name, value):
        if isinstance(value, dict):
            value = feed_class(DataStore(), value)

        if " " in name:
            name = name.replace(" ", "_")

        super().__setattr__(name, value)

    def __getattribute__(self, name):
        if " " in name:
            name = name.replace(" ", "_")
        try:
            return super().__getattribute__(name)
        
        except AttributeError:
            return None

    def __delattr__(self, name):
        if " " in name:
            name = name.replace(" ", "_")

        super().__delattr__(name)

    def __iter__(self):
        return iter(self.__dict__.items())

    def __len__(self):
        return len(self.__dict__)

    def __bool__(self):
        return bool(self.__dict__)

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def __getitem__(self, key):
        key = key.replace(" ", "_")
        try:
            return super().__getattribute__(key)
        except AttributeError:
            raise KeyError(f"'{key}' not found")

    def __setitem__(self, key, value):
        key = key.replace(" ", "_")
        super().__setattr__(key, value)

    def __delitem__(self, key):
        key = key.replace(" ", "_")
        try:
            super().__delattr__(key)
        except AttributeError:
            raise KeyError(f"'{key}' not found")

    def __contains__(self, key):
        key = key.replace(" ", "_")
        return hasattr(self, key)


    #Construit un hash de la class sérialisée
    def get_hash(self):
        with Store(format=Formatstore.to_dict) as vault:
            #Sérialisation de la class
            vault.push("DA", feed_dict({}, self))

            #Création du hash à partir du dictionnaire de résultat
            return sha256(msgpack.packb(vault.get_content())).hexdigest()

    def get(self, path, default=None):
        keys = path.split('.')
        current = self
        for key in keys:
            key = key.replace(" ", "_")
            if isinstance(current, DataStore):
                current = getattr(current, key, default)
            elif isinstance(current, dict):
                current = current.get(key, default)
            elif isinstance(current, list) and key.isdigit():
                try:
                    current = current[int(key)]
                except (IndexError, TypeError):
                    return default
            else:
                return default
            if current is default and key != keys[-1]: # If an intermediate key is not found, return default immediately
                return default
        return current

    def set(self, path, value):
        keys = path.split('.')
        current = self
        for i, key in enumerate(keys):
            key = key.replace(" ", "_")
            if i == len(keys) - 1:  # Last key
                if isinstance(current, DataStore):
                    setattr(current, key, value)
                elif isinstance(current, dict):
                    current[key] = value
                elif isinstance(current, list) and key.isdigit():
                    try:
                        current[int(key)] = value
                    except IndexError:
                        # Handle out of bounds for list, maybe extend or raise error
                        raise IndexError(f"List index {key} out of bounds for path {path}")
                else:
                    raise TypeError(f"Cannot set value on non-DataStore/dict/list object at path segment '{'.'.join(keys[:i])}'")
            else:  # Intermediate key
                if isinstance(current, DataStore):
                    next_obj = getattr(current, key, None)
                    if next_obj is None:
                        next_obj = DataStore()
                        setattr(current, key, next_obj)
                    elif not isinstance(next_obj, (DataStore, dict, list)):
                        raise TypeError(f"Path segment '{key}' is not a DataStore, dict, or list. Cannot traverse further.")
                    current = next_obj
                elif isinstance(current, dict):
                    next_obj = current.get(key)
                    if next_obj is None:
                        next_obj = {}
                        current[key] = next_obj
                    elif not isinstance(next_obj, (DataStore, dict, list)):
                        raise TypeError(f"Path segment '{key}' is not a DataStore, dict, or list. Cannot traverse further.")
                    current = next_obj
                elif isinstance(current, list) and key.isdigit():
                    try:
                        next_obj = current[int(key)]
                        if not isinstance(next_obj, (DataStore, dict, list)):
                            raise TypeError(f"Path segment '{key}' is not a DataStore, dict, or list. Cannot traverse further.")
                        current = next_obj
                    except IndexError:
                        raise IndexError(f"List index {key} out of bounds for path {path}")
                else:
                    raise TypeError(f"Cannot traverse through non-DataStore/dict/list object at path segment '{'.'.join(keys[:i])}'")

    def pop(self, path, default=None):
        keys = path.split('.')
        current = self
        for i, key in enumerate(keys):
            key = key.replace(" ", "_")
            if i == len(keys) - 1:  # Last key
                if isinstance(current, DataStore):
                    if hasattr(current, key):
                        value = getattr(current, key)
                        delattr(current, key)
                        return value
                    elif default is not None:
                        return default
                    else:
                        raise AttributeError(f"'{key}' not found at path '{path}'")
                elif isinstance(current, dict):
                    if key in current:
                        return current.pop(key)
                    elif default is not None:
                        return default
                    else:
                        raise KeyError(f"'{key}' not found at path '{path}'")
                elif isinstance(current, list) and key.isdigit():
                    try:
                        index = int(key)
                        return current.pop(index)
                    except (IndexError, ValueError):
                        if default is not None:
                            return default
                        else:
                            raise IndexError(f"List index {key} out of bounds or invalid for path '{path}'")
                else:
                    if default is not None:
                        return default
                    else:
                        raise TypeError(f"Cannot pop from non-DataStore/dict/list object at path segment '{'.'.join(keys[:i])}'")
            else:  # Intermediate key
                if isinstance(current, DataStore):
                    current = getattr(current, key, None)
                elif isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    try:
                        current = current[int(key)]
                    except (IndexError, ValueError):
                        if default is not None:
                            return default
                        else:
                            raise IndexError(f"List index {key} out of bounds or invalid for path '{path}'")
                else:
                    if default is not None:
                        return default
                    else:
                        raise TypeError(f"Cannot traverse through non-DataStore/dict/list object at path segment '{'.'.join(keys[:i])}'")
                
                if current is None and default is not None: # If an intermediate key is not found, return default immediately
                    return default
                elif current is None and default is None:
                    raise AttributeError(f"Path '{path}' not found.")


    def clear(self):
        self.__dict__.clear()

    def delete(self, path):
        keys = path.split('.')
        current = self
        for i, key in enumerate(keys):
            key = key.replace(" ", "_")
            if i == len(keys) - 1:  # Last key
                if isinstance(current, DataStore):
                    if hasattr(current, key):
                        delattr(current, key)
                    else:
                        raise AttributeError(f"'{key}' not found at path '{path}'")
                elif isinstance(current, dict):
                    if key in current:
                        del current[key]
                    else:
                        raise KeyError(f"'{key}' not found at path '{path}'")
                elif isinstance(current, list) and key.isdigit():
                    try:
                        index = int(key)
                        del current[index]
                    except (IndexError, ValueError):
                        raise IndexError(f"List index {key} out of bounds or invalid for path '{path}'")
                else:
                    raise TypeError(f"Cannot delete from non-DataStore/dict/list object at path segment '{'.'.join(keys[:i])}'")
            else:  # Intermediate key
                if isinstance(current, DataStore):
                    current = getattr(current, key, None)
                elif isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    try:
                        current = current[int(key)]
                    except (IndexError, ValueError):
                        raise IndexError(f"List index {key} out of bounds or invalid for path '{path}'")
                else:
                    raise TypeError(f"Cannot traverse through non-DataStore/dict/list object at path segment '{'.'.join(keys[:i])}'")
                
                if current is None:
                    raise AttributeError(f"Path '{path}' not found.")


#Ajouter les données d'un dictionnaire dans une Class
def feed_class(data_class, data):
    for key, value in data.items():
        if isinstance(value, dict):
            setattr(data_class, key, feed_class(DataStore(), value))
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(feed_class(DataStore(), item))
                else:
                    new_list.append(item)
            setattr(data_class, key, new_list)
        else:
            setattr(data_class, key, value)
    return data_class


#Ajouter les données d'une Class dans un dictionnaire
def feed_dict(data_dict, data):
    for key, value in data.__dict__.items():
        if isinstance(value, DataStore):
            data_dict[key] = feed_dict({}, value)
        elif isinstance(value, list):
            data_dict[key] = [
                feed_dict({}, item) if isinstance(item, DataStore) else item
                for item in value
            ]
        else:
            data_dict[key] = value
    return data_dict


#Dict to Class
def structure(data):
    new_class = DataStore()
    return feed_class(new_class, data)


#Class to Dict
def destructure(data):
    if isinstance(data, DataStore):
        return feed_dict({}, data)
    else:
        raise TypeError(f"Type {type(data)} not supported")