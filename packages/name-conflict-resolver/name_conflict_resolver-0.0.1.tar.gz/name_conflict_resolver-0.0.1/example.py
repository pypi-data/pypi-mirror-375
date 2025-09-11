from pathlib import PurePosixPath as p
from name_conflict_resolver import NameConflictResolver

names = [p("/home/andrew/foo"), p("/home/andrew/bar"), p("/home/andrew/foo")]

# We can currently distinguish these names by their index in the array, so
# we use the list of indices as the keys. Meanwhile, we can obtain a 
# corresponding path from a key using the __getitem__ method of names.
resolver = NameConflictResolver.from_keys(range(len(names)), names.__getitem__)

for f, (orig_destination, destination) in resolver.resolve():
    print(f"Path at index {f}: {orig_destination} -> {destination}")