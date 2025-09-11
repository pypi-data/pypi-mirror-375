#!/usr/bin/env python3

from gentrie import GeneralizedTrie, TrieEntry

trie = GeneralizedTrie()
keys: list[str] = ['abcdef', 'abc', 'a', 'abcd', 'qrs']
for entry in keys:
    trie.add(entry)
matches: set[TrieEntry] = trie.prefixed_by('abcd')

for trie_entry in sorted(list(matches)):
    print(f'{trie_entry.ident}: {trie_entry.key}')

# 1: abcdef
# 4: abcd
