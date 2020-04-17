## Workflow

1. **Start from a full sentence** [optional, can also start with things already masked]
    - e.g. `What are the best things to do in Seattle for a five-year-old kid?`
2. **Tag tokens with (labeled) masks**. In addition to `[MASK]` (meaning the fill-in is from BERT and should just be general stuff), people can choose one from a list of predefined candidate words for a given context (`male_adj`, `female_adj`, `city`.)
    - e.g. `What are the [MASK] [NOUN] to do in [CITY] for a [MASK] [human_ref] ?`
3. **Get suggestions.** People can choose how flexible the suggestion should be through two interactions on tagged tokens:
    - _link/unlink_: If all the [MASK] should be dependent of each other, or if they should be filled in independently (to collect invariance), assuming other words are fixed to default (e.g., in prev. example, default of `[CITY]` would be `Seattle`. If it's an added `[MASK]`, then its default is `""`.)
    - _lock/unlock_: If locked, even when a token is labeled, it should not get suggestions. In the linked case, the lock changes how flexible a suggestion should be.
4. **Save the suggestions**. In two cases:
    - Save full sentences for testing.
    - Save suggestions from `[MASK]`, create new context candidates for future use.