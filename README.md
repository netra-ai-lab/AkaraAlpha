<div align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/netra-logo-transparent-new.png" width="60%" alt="Netra Lab" />
</div>
<hr>

<p align="center">
    <a href="https://huggingface.co/Netra-Lab/AkaraAlpha"><b>Model weights</b></a> |
    <a href="https://pypi.org/project/netra-transliterate/"><b>PyPI</b></a> |
    <a href="https://github.com/Chhunneng/khmer-text-transliteration"><b>Dataset</b></a>
</p>

<h2 align="center">AkaraAlpha: An Efficient Romanized Khmer-Khmer Script Transliteration Model</h2>

<p align="center">
<img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/benchmark.png" width="1000" alt="Character error rate of six models, and Top-1 accuracy against latency for each beam width">
</p>

<p align="center"><em>Performance benchmark and system optimization. (a) Comparison of standalone model architectures based on Character Error Rate (CER). (b) Trade-off analysis between Top-1 accuracy and inference latency across varying beam widths (k). The red dotted line denotes the 100 ms real-time latency threshold, identifying k=5 as the optimal configuration for practical deployment.</em></p>

## Overview
An English–Khmer transliteration system built on an Attention-Based Bidirectional GRU architecture. The model converts romanized Khmer text written in the Latin alphabet into its corresponding Khmer script form: `brodae` → ប្រដែ. It has **78,705 parameters**. To enhance accuracy and ensure linguistic validity, the system checks the model's candidates against a Khmer dictionary of 38,743 words and corrects them.

The weights are also on [Hugging Face](https://huggingface.co/Netra-Lab/AkaraAlpha), with a plain-JSON copy of the tokenizers.

## Dataset
The dataset used in this project was sourced from the [Khmer Text Transliteration Dataset by Chhunneng (2023)](https://github.com/Chhunneng/khmer-text-transliteration), which provides parallel pairs of English–Khmer transliterations for machine learning research.

There are 77 unique Khmer characters and 26 unique English characters in the dataset. The maximum sequence length for English (romanized Khmer) inputs is 25 characters, while the maximum Khmer output length is 24 characters.

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/word_length.png" alt="Histograms of word length for romanized Khmer and Khmer script">
</p>

<p><em><strong>Figure 1 | Word Length Distribution of Romanized Khmer, and Khmer Script</strong></em></p>

- **Total Samples:** 28,569
- **Train Set:** 22,855 (80%)
- **Validation Set:** 5,714 (20%, the last fifth of the data)
- **Format:** Parallel text pairs (`brodae: ប្រដែ`)

## Model Architecture

The model is based on an Attention-Based Bidirectional GRU architecture designed for sequence-to-sequence transliteration. It follows an encoder–decoder structure, where the encoder processes the input Latin script (English) sequence, and the decoder generates the corresponding Khmer script sequence character by character.

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/akaraalpha_architecture.png" alt="AkaraAlpha turning brodae into Khmer: a bidirectional GRU encoder reading upwards and a GRU decoder with additive attention reading downwards">
</p>

<p><em><strong>Figure 2 | The proposed Attention-based Bidirectional Gated Recurrent Unit architecture, turning brodae into ប្រដែ.</strong> The encoder reads upwards: each letter becomes a 32-dimensional embedding, a bidirectional GRU reads the letters in both directions, and a projection brings each state to 64 dimensions, the keys and values for attention. The decoder reads downwards. At step 4, with ប ្ រ written, its GRU output is the query for additive attention, and a softmax layer over 81 ids gives ដ with probability 0.997. The chosen character joins the input and the loop repeats until the end marker.</em></p>

### Encoder

The encoder uses a Bidirectional GRU layer to process text from both start and end directions within the input sequence. This allows the model to better understand dependencies across the entire input text, which is particularly useful for transliteration tasks where phonetic relationships depend on both preceding and succeeding characters.

Each input token is first mapped into a continuous vector space through an embedding layer, which converts discrete character indices into dense embeddings of dimension 32. The bidirectional GRU, with 64 units in each direction, then encodes these embeddings into 128-dimensional states that carry forward and backward context. A dense layer applied at every position projects each state to 64 dimensions; these projected states are the keys and values for attention.

### Decoder

The decoder consists of a GRU layer of 64 units that processes the output sequence one Khmer character at a time, starting from a zero state. At each decoding step, it receives the previously predicted character. Additive attention then scores every projected encoder state against the decoder's GRU output to build a context vector, which helps the model focus on the most relevant parts of the input sequence. This context vector is concatenated with the decoder's GRU output and passed through a dense softmax layer over 81 ids (77 Khmer characters, start, end, unknown and padding) to produce the final character prediction.

| Part | Setting |
| :--- | :--- |
| Embedding dimension | 32 |
| Encoder | Bidirectional GRU, 64 units each way, then a projection to 64 |
| Decoder | GRU, 64 units, starting from zeros |
| Attention | Additive (Keras `AdditiveAttention`, learned scale) |
| Encoder parameters | 46,784 |
| Decoder parameters | 31,921 |
| Total parameters | 78,705 |

## Training Configuration
- **Batch Size:** 64
- **Epochs:** 50
- **Validation Split:** 20%
- **Optimizer:** Adam, learning rate 0.001
- **Dropout:** 0.3 on the inputs and recurrent states of both GRUs
- **Loss Function:** Sparse Categorical Crossentropy, with teacher forcing
- **Learning Rate Scheduler:** ReduceLROnPlateau (factor=0.5, patience=3); it halved the learning rate once, after epoch 42
- **Early Stopping:** patience 10, restoring the best weights; the released weights are from epoch 48 (validation loss 0.1034)

## Post-Processing Technique
To maximize accuracy without adding model bloat, our post-processing pipeline checks the outputs against a Khmer dictionary. The model first generates *k* candidate transliterations using beam search, and each is normalised with [khmerspell](https://pypi.org/project/khmerspell/). Candidates that are dictionary words come first. Each remaining candidate is replaced by the closest dictionary word within two edits (Levenshtein distance), unless that word is already in the list. If no candidate is near a dictionary word, the raw candidates are returned.

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/pipeline.png" alt="The full pipeline on konhchreng: preprocessing, encoder and decoder, three beam candidates, the dictionary check, Levenshtein correction and the merged suggestions">
</p>

<p><em><strong>Figure 3 | End-to-end inference pipeline with the post-processing technique, on the held-out word konhchreng with k=3.</strong> The input is cleaned, converted to letter ids and padded, and the encoder-decoder model proposes three candidates by beam search. Candidates that are dictionary words are kept (Yes); the others are replaced by their nearest dictionary word within two edits (No). A replacement that is already kept is dropped (dashed). The model ranked the correct word, កញ្ច្រែង, second; the dictionary puts it first.</em></p>

> **Note:** when several dictionary words are equally close to a candidate, the package keeps whichever it meets first, and that order can change between runs. Later suggestions from `transliterate_with_dict` can therefore differ from run to run.

## Results and Analysis

### 1. Evaluation Metrics - CER
To evaluate the performance of the model, Character Error Rate (CER) was used. CER quantifies the number of errors at the character level, providing a direct measure of the model's accuracy in converting individual Romanized graphemes to their corresponding Khmer script. It is calculated as:

$$\mathrm{CER} = \frac{S + D + I}{N}$$

where $S$ represents the number of substitutions, $D$ is the number of deletions, $I$ is the number of insertions, and $N$ is the total number of characters in the ground truth sequence. A lower CER indicates higher accuracy in the transliteration output.

### 2. Evaluation Metrics – Top-1 and Top-k Hit Accuracy
Additionally, to evaluate the post-processing technique, we also assess word-level accuracy by measuring the Top-1 and Top-k hit accuracy. We define Top-1 accuracy as the percentage of test samples where the highest-ranked candidate produced by the system exactly matches the ground truth:

$$\text{Top-1} = \frac{1}{M} \sum_{i=1}^{M} \mathbb{1}\left[\hat{y}_{i,1} = y_i\right]$$

where $M$ is the total number of test samples, $y_i$ is the ground truth, $\hat{y}_{i,1}$ is the first-ranked candidate produced by the system, and $\mathbb{1}[\cdot]$ is 1 when the condition holds and 0 otherwise.

Top-k hit accuracy measures how often the correct Khmer word appears within the list of $k$ candidates generated by the system:

$$\text{Top-}k = \frac{1}{M} \sum_{i=1}^{M} \mathbb{1}\left[y_i \in \lbrace \hat{y}_{i,1}, \dots, \hat{y}_{i,k} \rbrace\right]$$

### 3. Quantitative Analysis

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/top_k.png" alt="Top-1 and Top-K accuracy and latency for each beam width">
</p>

<p><em><strong>Figure 4 | Analytical trade-off between transliteration accuracy and computational overhead.</strong> (a) Search space benefit analysis illustrating the gap between primary prediction (Top-1) and system recall (Top-K). The shaded region represents the additive benefit of beam search; at the recommended k=5 setting, the system provides a 9.81 percentage-point (pp) recall gain over the top-1 prediction. (b) The computational efficiency frontier, highlighting the relationship between accuracy gains and inference latency. The gray bars represent the absolute magnitude of computational overhead, while the red dotted line tracks the linear latency trajectory across different beam widths. The optimal operating point is k=5, which achieves a 29.16 percentage-point increase in Top-1 accuracy over greedy decoding while remaining under the 100 ms real-time latency threshold; beyond this point, the system exhibits diminishing returns as latency exceeds the limits of user interaction.</em></p>

**Table 1 | Model comparison on the validation set using Character Error Rate (CER %).** Lower CER indicates better performance. The lowest CER is **bold** and the second lowest is *italic*.

| Model | CER (%) | Parameters |
| :--- | ---: | ---: |
| RNN | 102.41 | 42,609 |
| LSTM | 31.78 | 58,417 |
| GRU | 51.64 | 46,385 |
| Transformer | *17.78* | 248,337 |
| Attention BiLSTM | 18.26 | 96,753 |
| **AkaraAlpha** | **15.07** | 78,705 |

**Table 2 | Performance comparison of system configurations.** Top-1 accuracy, Top-K hit rate and average inference latency across greedy decoding and varying beam search widths (*k*), with the dictionary check.

| Configuration | Top-1 | Top-K Hit | Latency (ms/word) |
| :--- | ---: | ---: | ---: |
| Greedy Decoding | 44.44% | 44.44% | 21.92 |
| k=3 | 70.06% | 78.72% | 66.03 |
| **k=5** | **73.60%** | **83.41%** | **94.15** |
| k=7 | 74.87% | 85.60% | 122.10 |
| k=10 | 75.85% | 87.37% | 167.21 |

### 4. Qualitative Analysis

<p align="center">
  <img src="https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/qualitative_analysis.png" width="560" alt="Four romanized words, their correct Khmer spellings, and each model's output with errors marked in red">
</p>

<p><em><strong>Table 3 | Qualitative comparison across all models</strong> on romanized Khmer words ranging from short to long, with errors in red.</em></p>

## Installation

**From PyPI (recommended):**
```bash
pip install netra-transliterate
```

**From source:**
```bash
git clone https://github.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration.git
cd Romanized-Khmer-to-Khmer-Transliteration
pip install -e .
```

## Usage

### Python API

#### 1. Single best transliteration
```python
from khmer_transliterator import transliterate

print(transliterate("brodae"))
# ប្រដែ
```

#### 2. Top-N candidates (raw model output)
```python
from khmer_transliterator import transliterate_top_n

print(transliterate_top_n("brodae", n=3))
# ['ប្រដែ', 'ប្រដែរ', 'បរដែ']
```

#### 3. Top-N candidates with dictionary validation
```python
from khmer_transliterator import transliterate_with_dict

print(transliterate_with_dict("brodae", n=3))
# ['ប្រដែ', ...]  dictionary words first; later entries can vary between runs (see the note above)
```

The `Transliterator` class is also available for explicit instantiation:
```python
from khmer_transliterator import Transliterator

t = Transliterator()
print(t.transliterate("brodae"))
```

> **Note:** The Keras model loads lazily on the first call (~1–2 s one-time cost).

### From Hugging Face

The model and a plain-JSON copy of its tokenizers are on [Hugging Face](https://huggingface.co/Netra-Lab/AkaraAlpha), which shows how to load and run them without this package.

### Command Line

```
usage: netra-transliterate [-h] [-n N] [--no-dict] [--shell] [--serve] [--port PORT] [WORD ...]
```

**Transliterate words directly:**
```bash
netra-transliterate brodae
# brodae    ប្រដែ

netra-transliterate brodae sokha -n 3
# brodae:
#   1. ប្រដែ
#   ...
# sokha:
#   1. សុខា
#   ...
```

**Interactive shell:**
```bash
netra-transliterate --shell
# or just:
netra-transliterate
```

**Skip dictionary post-processing:**
```bash
netra-transliterate brodae --no-dict
```

**Web server:**
```bash
netra-transliterate --serve
# Starting web server at http://localhost:5000

netra-transliterate --serve --port 8080
```

## Web Application

A browser-based UI is bundled with the package. Start it with:

```bash
netra-transliterate --serve
```

Then open http://localhost:5000 in your browser. Type a romanized Khmer word to see live suggestions; use **Tab** to cycle through candidates and **Space** to accept one.

## Demo
![The web application suggesting Khmer words while a romanized word is typed](https://raw.githubusercontent.com/netra-ai-lab/Romanized-Khmer-to-Khmer-Transliteration/main/assets/video.gif)

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

Dataset:
> Chhunneng. (2023). *Khmer Text Transliteration Dataset*. GitHub repository.
> Available at: [https://github.com/Chhunneng/khmer-text-transliteration](https://github.com/Chhunneng/khmer-text-transliteration)

## License

MIT. See [LICENSE](LICENSE).
