from collections import namedtuple, Counter

def append_to_stem(path, add):
    return path.with_stem("{}{}".format(path.stem, add))
    
# key some object that distinguishes between files with the same path.
# path is the path corresponding to the key.
Destination = namedtuple("Destination", ["key", "path"])
    
class NameConflictResolver:
    def __init__(self, destinations):
        self.destinations = list(destinations)
        
    def resolve(self):
        new_locations = {}
        location_counter = Counter()
        for f, p in sorted(self.destinations, key=lambda x: x.path):
            if not p in new_locations:
                new_locations[p] = {f: (p, p)}
            else:
                new_path = append_to_stem(
                    p,
                    "_{}".format(location_counter[p])
                )
                new_locations[p][f] = (p, new_path)
                new_locations[new_path] = {}
                location_counter[new_path] += 1
            location_counter[p] += 1
        # Note that the code below depends on dict remembering the order in
        # which keys are inserted.
        for files in reversed(new_locations.values()):
            yield from reversed(files.items())
            
    @classmethod
    def from_keys(cls, keys, get_path):
        key_list = list(keys)
        if len(set(key_list)) != len(key_list):
            raise ValueError("keys must be distinct.")
        return cls(Destination(key=k, path=get_path(k)) for k in key_list)