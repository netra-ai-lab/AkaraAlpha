<div align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/symbol.png" height="72" alt="Netra Lab" style="vertical-align: middle; margin-right: 24px;" />
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/wordmark-latin.png" height="56" alt="Netra" style="vertical-align: middle;" />
</div>

<hr>

<p align="center">
  <a href="https://github.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration"><b>GitHub</b></a> |
  <a href="https://pypi.org/project/netra-transliterate/"><b>PyPI</b></a> |
  <a href="https://huggingface.co/Netra-Lab/AkaraAlpha"><b>Model Download</b></a> |
  <a href="https://github.com/Chhunneng/khmer-text-transliteration"><b>Dataset</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-e75f1b?labelColor=4f2724" alt="License: MIT" />
  <img src="https://img.shields.io/badge/python-3.9%2B-e75f1b?labelColor=4f2724&logo=python&logoColor=f5efe5" alt="Python 3.9+" />
  <a href="https://huggingface.co/Netra-Lab/AkaraAlpha"><img src="https://img.shields.io/badge/params-78.7K-e75f1b?labelColor=4f2724&logo=huggingface&logoColor=f5efe5" alt="78.7K parameters" /></a>
  <a href="https://pypi.org/project/netra-transliterate/"><img src="https://img.shields.io/badge/pypi-netra--transliterate-e75f1b?labelColor=4f2724&logo=pypi&logoColor=f5efe5" alt="PyPI: netra-transliterate" /></a>
</p>

<h2>
<p align="center">
  AkaraAlpha: An Efficient Romanized Khmer-Khmer Script Transliteration Model
</p>
</h2>

<p align="center">
  Khmer typed in Latin letters in, Khmer script out. A 78.7K-parameter attention-based bidirectional GRU with a dictionary check, fast enough to suggest words as you type.
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/results.png" width="1000" alt="Character error rate of AkaraAlpha and five baselines, and Top-1 and Top-K word accuracy against latency for each beam width" />
</p>

<p align="center">
  <em>(a) Character error rate of each model alone on the 5,714 held-out words, with its parameter count; lower is better. (b) The full system with the dictionary check: word accuracy against latency per word for greedy decoding and beam widths 3–10. k=5 is the widest beam under 100 ms.</em>
</p>

## 1. Abstract

This repository presents AkaraAlpha, a compact **78,705-parameter** character-level encoder-decoder that converts romanized Khmer, Khmer written in the Latin alphabet, into Khmer script: `brodae` → ប្រដែ. It is trained on **28,569** word pairs.

1. **A bidirectional GRU encoder** reads the romanized word forwards and backwards, so every position carries context from the whole word, including the letters after it.
2. **A GRU decoder with additive attention** writes the Khmer word one character at a time, looking back over the encoded letters at every step.
3. **A dictionary check** after beam search keeps candidates that are Khmer words and corrects the rest to the nearest word within two edits, using a dictionary of 38,743 words.

On the held-out words the model alone has a **character error rate of 15.07%**, lower than every baseline trained on the same data, including a Transformer with three times as many parameters (17.78%). With the dictionary check and five beam candidates, the first suggestion is right **73.60%** of the time and the right word is in the list 83.41% of the time, at **94 ms per word**.

The package is `pip install netra-transliterate`, with a Python API, a command-line tool and a typing interface in the browser.

## 2. Dataset

AkaraAlpha was trained on the [Khmer Text Transliteration Dataset](https://github.com/Chhunneng/khmer-text-transliteration) (Chhunneng, 2023): **28,569** single words, each written in romanized form and in Khmer script (`brodae: ប្រដែ`).

### Split

| Split | Words |
| :--- | ---: |
| Train | 22,855 (80%) |
| Validation | 5,714 (20%, the last fifth of the data) |

### Preprocessing

- **Romanized input:** lowercased, everything but `a`–`z` removed, each letter converted to an id and padded to 25: 26 letters, plus unknown and padding.
- **Khmer output:** characters outside the Khmer Unicode block removed and the character order normalised with [khmerspell](https://pypi.org/project/khmerspell/): 77 Khmer characters, plus start, end, unknown and padding (81 ids).

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/word_length.png" width="1000" alt="Histograms of word length in the dataset, romanized letters and Khmer characters" />
</p>

<p><em>Figure 1: Word lengths in the dataset. Romanized words peak at 7 letters (4,547 words) and Khmer words at 6 characters (6,308); none is longer than 25 letters or 24 Khmer characters.</em></p>

## 3. Model Architecture

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/architecture.png" width="100%" alt="AkaraAlpha turning brodae into Khmer: a bidirectional GRU encoder reading upwards and a GRU decoder with additive attention reading downwards" />
</p>

<p><em>Figure 2: AkaraAlpha turning brodae into ប្រដែ. The encoder (left) reads upwards: each letter becomes a 32-dimensional embedding, a bidirectional GRU reads the letters in both directions, and a projection brings each state to 64 dimensions, the keys and values for attention. The decoder (right) reads downwards. At step 4, with ប ្ រ written, its GRU output is the query for additive attention, and a softmax layer over 81 ids gives ដ with probability 0.997. The chosen character joins the input and the loop repeats until the end marker. Parameter counts are the released model's.</em></p>

- **Encoder.** A character embedding (32 dimensions) and a bidirectional GRU with 64 units in each direction, giving 128-dimensional states that carry forward and backward context. A dense layer applied at every position projects each state to 64 dimensions.
- **Decoder.** A GRU of 64 units that starts from a zero state, so everything it knows about the input reaches it through attention.
- **Additive attention.** At each step the decoder's GRU output is scored against every projected encoder state, $e_{t,j} = \sum_d g_d \tanh(s_{t,d} + k_{j,d})$, with 64 learned scales $g$; the softmax of the scores weights the states into a context vector.
- **Output.** The GRU output and the context are concatenated (128) and a softmax layer scores the 81 Khmer ids.

| Part | Setting |
| :--- | :--- |
| Embedding dimension | 32, separate for input and output |
| Encoder | Bidirectional GRU, 64 units each way, then a projection to 64 |
| Decoder | GRU, 64 units, starting from zeros |
| Attention | Additive (Keras `AdditiveAttention`, learned scale) |
| Vocabulary | 28 romanized ids, 81 Khmer ids |
| Encoder parameters | 46,784 |
| Decoder parameters | 31,921 |
| Total parameters | 78,705 |

### Training

| Setting | Value |
| :--- | :--- |
| Objective | Sparse categorical cross-entropy, teacher forcing |
| Optimiser | Adam, learning rate 0.001 |
| Batch size | 64 |
| Epochs | 50 |
| Dropout | 0.3 on the inputs and recurrent states of both GRUs |
| Learning rate schedule | ReduceLROnPlateau (factor 0.5, patience 3); it halved the rate once, after epoch 42 |
| Early stopping | Patience 10, best weights restored: the released weights are from epoch 48 (validation loss 0.1034) |

### Dictionary check

Beam search proposes *k* candidates, and each is normalised with khmerspell. Candidates that are dictionary words come first, in the model's order. Each remaining candidate is replaced by the closest dictionary word within two edits (Levenshtein distance), unless that word is already in the list. If no candidate is near a dictionary word, the raw candidates are returned.

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/pipeline.png" width="100%" alt="The full pipeline on konhchreng: preprocessing, encoder and decoder, three beam candidates, the dictionary check, Levenshtein correction and the merged suggestions" />
</p>

<p><em>Figure 3: The full system on konhchreng, a held-out word, with k=3. Left, reading upwards: the word is cleaned, turned into letter ids and padded, and the model proposes three candidates by beam search. Right: candidates that are dictionary words are kept (Yes), and the others are replaced by their nearest dictionary word within two edits (No); a replacement that is already kept is dropped (dashed). The model ranked the correct word, កញ្ច្រែង, second; the dictionary puts it first.</em></p>

## 4. Evaluation

| Model | CER (%) ↓ | Parameters |
| :--- | ---: | ---: |
| RNN | 102.41 | 42,609 |
| GRU | 51.64 | 46,385 |
| LSTM | 31.78 | 58,417 |
| Attention BiLSTM | 18.26 | 96,753 |
| Transformer | 17.78 | 248,337 |
| **AkaraAlpha** | **15.07** | **78,705** |

| Decoding, with the dictionary check | Top-1 ↑ | Top-K ↑ | Latency (ms/word) ↓ |
| :--- | ---: | ---: | ---: |
| Greedy | 44.44% | 44.44% | 21.92 |
| Beam, k=3 | 70.06% | 78.72% | 66.03 |
| **Beam, k=5** | **73.60%** | **83.41%** | **94.15** |
| Beam, k=7 | 74.87% | 85.60% | 122.10 |
| Beam, k=10 | 75.85% | 87.37% | 167.21 |

- **Scoring.** All models were trained on the same 22,855 words and scored on the same 5,714 held-out words. CER is $(S + D + I) / N$: substitutions, deletions and insertions over the characters of the correct word. Top-1 is the share of words whose first suggestion is exactly right; Top-K the share whose correct word is anywhere in the list.
- **Attention makes the biggest difference.** Every model without it has a CER above 30%; the plain RNN's is above 100%, which happens when a model inserts more wrong characters than the correct word has. Among the models with attention, AkaraAlpha is the most accurate with under a third of the Transformer's parameters.
- **The dictionary check lifts word accuracy** from 44.44% (greedy, one candidate) to 73.60% Top-1 with five candidates.
- **Most of the gain comes from the first few candidates.** Going from one candidate to five adds 29.16 points of Top-1 accuracy; going from five to ten adds 2.25 more and pushes latency past 100 ms. **k=5 is the recommended setting.**

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/qualitative_analysis.png" width="560" alt="Four romanized words, their correct Khmer spellings, and each model's output with errors marked in red" />
</p>

<p><em>Figure 4: Four romanized words and each model's output, with errors in red. Only AkaraAlpha gets all four right.</em></p>

## 5. Install

```bash
pip install netra-transliterate
# or, from a checkout:  pip install -e .
```

The model (1 MB), its tokenizers and the dictionary ship inside the package; TensorFlow 2.17 or later runs the model. The weights and a plain-JSON copy of the tokenizers are also on [Hugging Face](https://huggingface.co/Netra-Lab/AkaraAlpha), with an example that runs them without the package.

## 6. Usage

**Python.**

```python
from khmer_transliterator import transliterate, transliterate_top_n, transliterate_with_dict

transliterate("brodae")                      # 'ប្រដែ'
transliterate_top_n("brodae", n=3)           # ['ប្រដែ', 'ប្រដែរ', 'បរដែ']  raw beam candidates
transliterate_with_dict("brodae", n=5)       # ['ប្រដែ', ...]  dictionary-checked suggestions
```

`Transliterator` holds one model for repeated use: `Transliterator().transliterate("brodae")`. The model loads on the first call (about 1–2 s).

**Command line.** Words as arguments, or an interactive shell.

```bash
netra-transliterate brodae                   # brodae    ប្រដែ
netra-transliterate brodae sokha -n 3        # up to three suggestions for each word
netra-transliterate brodae --no-dict         # skip the dictionary check
netra-transliterate                          # interactive shell (or --shell)
```

**Typing interface.** A browser page that suggests Khmer words as you type romanized ones: **Tab** cycles through the suggestions and **Space** accepts one.

```bash
netra-transliterate --serve                  # http://localhost:5000
netra-transliterate --serve --port 8080
```

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/demo.gif" width="800" alt="The typing interface suggesting Khmer words while a romanized word is typed" />
</p>

**Charts.** `python assets/make_figures.py` redraws `results.png` and `word_length.png` in the Netra chart style.

## 7. Limitations

- **Words, not sentences.** The model transliterates one word at a time, so it can't use the surrounding sentence to choose between two words with the same romanized spelling.
- **No separate test set.** The held-out words were also used to adjust the learning rate and choose the epoch, so the scores may be slightly optimistic.
- **One way of romanizing.** All the training data comes from one dataset; people who spell Khmer differently in Latin letters may get worse results.
- **The dictionary has edges.** A name or new word that isn't in the dictionary may be "corrected" into a real word within two edits; use `transliterate_top_n` for the raw candidates.
- **Ties.** When several dictionary words are equally close to a candidate, the package keeps whichever it meets first, and that order can change between runs, so later suggestions from `transliterate_with_dict` can differ from run to run.
- **Latency depends on hardware.** The timings were measured on one machine; read them as the relative cost of each setting.

## 8. Licensing

This project is released under the MIT License (see [LICENSE](LICENSE)).
- **Weights:** MIT, like the code.
- **Training data:** the [Khmer Text Transliteration Dataset](https://github.com/Chhunneng/khmer-text-transliteration) keeps the terms of its own repository.

## Citation

```bibtex
@software{akaraalpha2026,
  title     = {AkaraAlpha: Romanized Khmer to Khmer Script Transliteration},
  author    = {Nhem, Darayut},
  year      = {2026},
  publisher = {Netra Lab},
  url       = {https://github.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration}
}
```

## References

1. **Khmer Text Transliteration Dataset**  
   *Chhunneng*  
   GitHub, 2023.  
   [github.com/Chhunneng/khmer-text-transliteration](https://github.com/Chhunneng/khmer-text-transliteration)

2. **Neural Machine Translation by Jointly Learning to Align and Translate**  
   *Dzmitry Bahdanau, Kyunghyun Cho, Yoshua Bengio*  
   ICLR 2015.  
   [arXiv:1409.0473](https://arxiv.org/abs/1409.0473)

3. **Learning Phrase Representations using RNN Encoder–Decoder for Statistical Machine Translation**  
   *Kyunghyun Cho, Bart van Merriënboer, Caglar Gulcehre, Dzmitry Bahdanau, Fethi Bougares, Holger Schwenk, Yoshua Bengio*  
   EMNLP 2014.  
   [arXiv:1406.1078](https://arxiv.org/abs/1406.1078)
