from .ranges import Ranges
from .utils import as_key, force_hash


class Dict:
    """
    Range-to-value mapping using slice syntax.

    Stores mappings from ranges to values efficiently without storing
    individual positions. Supports slice syntax: d[100:200] = "value"
    """

    def __init__(self, *args, **kwargs):
        self._ranges = {}  # {range_key: hash_key} - rebuilt lazily when dirty
        self._values = {}  # {hash_key: (actual_value, Ranges)}
        self._dirty = False  # Flag to trigger rebuilding _ranges

        # Handle initialization like dict
        if args:
            if len(args) > 1:
                raise TypeError(f"Dict expected at most 1 argument, got {len(args)}")
            self.update(args[0])
        if kwargs:
            self.update(kwargs)

    def __setitem__(self, key, value):
        """Set a range to a value: d[100:200] = "highlight" """
        range_ranges = as_key(key)
        hash_key = force_hash(value)

        # Find existing ranges that intersect using query
        matches = self._query(range_ranges)
        affected_hashes = set(hash_key for _, hash_key in matches)

        # Remove intersecting ranges from their values
        for existing_hash_key in affected_hashes:
            existing_value, existing_ranges = self._values[existing_hash_key]
            remaining_ranges = existing_ranges - range_ranges
            if remaining_ranges:
                self._values[existing_hash_key] = (existing_value, remaining_ranges)
            else:
                del self._values[existing_hash_key]

        # Add/update the new value's ranges
        if hash_key in self._values:
            # Value already exists, add to its ranges
            old_value, old_ranges = self._values[hash_key]
            new_ranges = old_ranges | range_ranges
            self._values[hash_key] = (value, new_ranges)
        else:
            # New value
            self._values[hash_key] = (value, range_ranges)

        self._dirty = True

    def __getitem__(self, key):
        """Get value for a range or position: d[150] or d[100:200]"""
        query_ranges = as_key(key)

        # Check if the query is completely covered by our ranges
        if not query_ranges or query_ranges not in self.ranges:
            raise KeyError(query_ranges)

        matches = self._query(query_ranges)

        # Check for ambiguous multi-value ranges - group by actual hash key
        unique_hash_keys = set(hash_key for _, hash_key in matches)
        if len(unique_hash_keys) > 1:
            raise ValueError(
                f"Range query {query_ranges} matched multiple different values"
            )

        # Return the (single) value
        range_key, hash_key = matches[0]
        return self._values[hash_key][0]

    def __contains__(self, key):
        """Check if a position/range is covered: 150 in d"""
        try:
            query_ranges = as_key(key)
            return bool(self.ranges & query_ranges)
        except ValueError:
            # Invalid range keys just don't exist
            return False

    def __delitem__(self, key):
        """Delete a key and update ranges"""
        delete_ranges = as_key(key)

        # Check if the key exists
        if not delete_ranges or not (delete_ranges & self.ranges):
            raise KeyError(delete_ranges)

        matches = self._query(delete_ranges)

        # Remove the deletion range from all intersecting values
        affected_hashes = set(hash_key for _, hash_key in matches)
        for hash_key in affected_hashes:
            value, existing_ranges = self._values[hash_key]
            remaining_ranges = existing_ranges - delete_ranges
            if remaining_ranges:
                self._values[hash_key] = (value, remaining_ranges)
            else:
                del self._values[hash_key]

        self._dirty = True

    def clear(self):
        """Clear all items and update ranges"""
        self._ranges.clear()
        self._values.clear()

    def pop(self, key, *args):
        """Pop a key and update ranges"""
        try:
            result = self[key]
            del self[key]
            return result
        except KeyError:
            if args:
                return args[0]
            raise

    def popitem(self):
        """Pop an item and update ranges"""
        self._update()
        if not self._ranges:
            raise KeyError("popitem(): dictionary is empty")
        range_key = next(iter(self._ranges))
        value = self._values[self._ranges[range_key]][0]
        del self[range_key]
        return range_key, value

    def update(self, *args, **kwargs):
        """Update dict and ranges"""
        # Use our own __setitem__ to get key conversion
        if len(args) > 1:
            raise TypeError(f"update expected at most 1 argument, got {len(args)}")

        if args:
            other = args[0]
            if hasattr(other, "keys"):
                for k in other.keys():
                    self[k] = other[k]
            else:
                for k, v in other:
                    self[k] = v

        for k, v in kwargs.items():
            self[k] = v

    def setdefault(self, key, default=None):
        """Set default and update ranges if key was added"""
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def get(self, key, default=None):
        """Get value with default, converting key"""
        try:
            return self[key]
        except (KeyError, ValueError):
            return default

    def __or__(self, other):
        """Union operator (|): return new Dict with combined contents"""
        result = self.copy()
        result.update(other)
        return result

    def __ror__(self, other):
        """Reverse union operator: other | self"""
        result = type(other)(other)
        result.update(self)
        return result

    def __ior__(self, other):
        """Inplace union operator (|=): update self with other"""
        self.update(other)
        return self

    def copy(self):
        """Return a copy of this Dict"""
        new_dict = Dict()
        new_dict._values = self._values.copy()
        new_dict._dirty = True  # Force rebuild on first access
        return new_dict

    def keys(self):
        """Return view of range keys"""
        self._update()
        return self._ranges.keys()

    def values(self):
        """Return view of values"""
        return (v[0] for v in self._values.values())

    def items(self):
        """Return view of (range_key, value) pairs"""
        self._update()
        return ((k, self._values[v][0]) for k, v in self._ranges.items())

    def __len__(self):
        """Return number of stored ranges"""
        self._update()
        return len(self._ranges)

    def __bool__(self):
        """Return True if not empty"""
        return bool(self._values)

    def __iter__(self):
        """Iterate over range keys"""
        self._update()
        return iter(self._ranges)

    def __reversed__(self):
        """Iterate over range keys in reverse order"""
        self._update()
        return reversed(list(self._ranges.keys()))

    def __eq__(self, other):
        """Check equality with another dict"""
        try:
            if len(self) != len(other):
                return False
            for k, v in self.items():
                if k not in other or other[k] != v:
                    return False
            return True
        except (TypeError, AttributeError):
            return False

    def __repr__(self):
        """String representation"""
        items = list(self.items())
        return f"Dict({dict(items)})"

    def _update(self):
        """Rebuild _ranges if dirty"""
        if not self._dirty:
            return

        # Rebuild algorithm: collect all segments by value
        value_segments = {}  # hash_key -> [segments]
        for hash_key, (value, ranges) in self._values.items():
            value_segments[hash_key] = list(ranges.segments)

        # Rebuild _ranges from consolidated ranges
        self._ranges.clear()
        for hash_key, segments in value_segments.items():
            if segments:
                consolidated_ranges = Ranges(segments)
                for segment in consolidated_ranges.segments:
                    self._ranges[str(segment)] = hash_key

        self._dirty = False

    def _query(self, query_ranges):
        """Find matching ranges for a Ranges object (private method)"""
        self._update()  # Ensure we're up to date

        matches = []
        for range_key, hash_key in self._ranges.items():
            if query_ranges & Ranges(range_key):
                matches.append((range_key, hash_key))
        return matches

    @property
    def ranges(self):
        """Union of all stored ranges (for compatibility)"""
        self._update()
        if not self._ranges:
            return Ranges("")
        return Ranges(",".join(self._ranges.keys()))
