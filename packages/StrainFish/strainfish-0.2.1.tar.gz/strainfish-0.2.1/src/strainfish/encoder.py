"""
StrainFish custom DNA Sequence Encoders.

Kranti Konganti
(C) HFP, FDA.
"""

import os
import re
import tempfile
from collections import Counter
from typing import Any, List, Optional, Tuple, Union

import numpy as np
import sentencepiece as sp
import sourmash as sm
from Bio import SeqIO
from numpy.typing import NDArray
from rich.progress import TaskID
from scipy.sparse import spmatrix
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from .constants import SFConstants as SFC
from .helpers import GPUMemInfo, SFHelpers
from .logging_utils import log, progress


class SPEncoder:
    """SentencePiece model creation with tokenizer."""

    def __init__(
        self,
        seq: Optional[Union[str, os.PathLike]] = None,
        model_prefix: Optional[Union[str, os.PathLike]] = "StrainFish_sp_dna.model",
        max_sentencepiece_length: int = 512,
        max_sentence_length: int = 8000,
        normalization_rule_name: str = "identity",
        vocab_size: int = 1000,
        model_type: str = "bpe",
        hard_vocab_limit: bool = False,
        character_coverage: float = 1.0,
    ) -> None:
        """
        Initialize the SentencePiece encoder.

        This constructor sets up the SentencePiece tokenizer with specified parameters
        for encoding sequences using various tokenization methods.

        Args:
            seq (str | os.PathLike, optional): Input sequence(s) for encoding.
                Can be a string or path to file. Defaults to None.
            model_prefix (os.PathLike, optional): Prefix for output model files.
                Defaults to "StrainFish_sp_dna.model" in current working directory.
            max_sentencepiece_length (int): Maximum length of sentencepieces.
                Defaults to 512.
            max_sentence_length (int): Specifies the maximum length of an input sentence, measured in bytes.
                During training, sentences exceeding this length are simply ignored, helping prevent issues like
                overflow during Unigram model training and performance degradation with BPE.
                Defaults to 8000.
            normalization_rule_name (str): Normalization rule to apply.
                Defaults to "identity".
            vocab_size (int): Size of vocabulary. Defaults to 1000.
            model_type (str): Type of model ('bpe', 'unigram', etc.).
                Defaults to "bpe".
            hard_vocab_limit (bool): Whether to enforce strict vocabulary limit.
                Defaults to False.
            character_coverage (float): Character coverage percentage.
                Defaults to 1.0.

        Note:
            The model will be trained on the provided sequence data during initialization.
            All parameters except 'seq' have sensible defaults for typical use cases.
        """
        self.seq = seq
        self.model_prefix = model_prefix
        self.max_sentencepiece_length = max_sentencepiece_length
        self.max_sentence_length = max_sentence_length
        self.normalization_rule_name = normalization_rule_name
        self.vocab_size = vocab_size
        self.model_type = model_type
        self.hard_vocab_limit = hard_vocab_limit
        self.character_coverage = character_coverage

    def split_seq_into_cols(
        self, seq: Optional[str] = None, columns: int = SFC.SPCOLS
    ) -> str:
        """
        Split input string into fixed-width columns separated by newlines.

        This method takes a sequence (string) and splits it into chunks of
        specified column width, joining each chunk with a newline character.

        Args:
            seq (str, optional): Input sequence to split. Defaults to None.
            columns (int): Number of characters per column/chunk. Defaults to 100.

        Returns:
            str: Sequence split into columns separated by newlines.

        Raises:
            SystemExit: Exits with code 1 if seq parameter is None (handled internally).
        """

        if not SFHelpers._defined(seq, "Input FASTA file"):
            raise ValueError()

        non_ov_mers = []
        for k in range(0, len(seq), columns):
            non_ov_mers.append(seq[k : k + columns])
        return "\n".join(non_ov_mers)

    def tokenizer(self, seq: Optional[str] = None) -> None:
        """
        SentencePiece with specified tokenizer type.

        This method will create the vocabulary for the specified input DNA corpus.
        It first takes the input DNA string, splits into specified columns, writes
        to a temporary file and then processes the temporary file using SentencePiece.

        Args:
            seq (str, optional): Input sequence to split. Defaults to None.

        Returns:
            None. This will create the vocabulary and save
            to the file.

        Raises:
            SystemExit: Exits the program with status code 1 FASTA file
            does not exist or models directory calculated from
            model prefix does not exist.
        """

        model_prefix = self.model_prefix
        c_model_prefix = os.path.join(model_prefix + f"{SFC.SP_C_CRPS_SUFFIX}")
        sp_models_dir = os.path.split(model_prefix)[0]
        tmp_suffix = ".tmp"

        if SFHelpers._defined(seq, "Input FASTA Sequence"):
            self.seq = seq

        if not SFHelpers._defined(self.seq, "Input FASTA Sequence"):
            raise ValueError()
        if not os.path.exists(sp_models_dir):
            os.makedirs(sp_models_dir)

        log.info(
            f"SP vocabulary will be saved to [bold cyan]{os.path.basename(sp_models_dir)}[/bold cyan]."
        )
        # log.info(f"Will overwrite if {os.path.basename(model_prefix)} exists.")

        if os.path.exists(c_model_prefix):
            log.info(
                (
                    f"Will overwrite SP vocabulary creation for corpus "
                    f"[bold cyan]{os.path.basename(model_prefix)}[/bold cyan] to "
                    "maintain parity with prediction(s)."
                )
            )

        with tempfile.NamedTemporaryFile(
            mode="w+",
            prefix=os.path.basename(model_prefix),
            suffix=tmp_suffix,
            dir=sp_models_dir,
            delete=False,
            delete_on_close=False,
        ) as temp_seq:
            temp_seq.write(self.seq)
            temp_seq.flush()

            if os.path.exists(temp_seq.name):
                sp.SentencePieceTrainer.train(
                    input=temp_seq.name,
                    model_prefix=str(model_prefix),
                    max_sentencepiece_length=self.max_sentencepiece_length,
                    normalization_rule_name=self.normalization_rule_name,
                    vocab_size=self.vocab_size,
                    model_type=self.model_type,
                    hard_vocab_limit=self.hard_vocab_limit,
                    character_coverage=self.character_coverage,
                    max_sentence_length=self.max_sentence_length,
                    pad_id=0,
                    unk_id=1,
                    bos_id=2,
                    eos_id=3,
                )

                log.info(
                    (
                        f"SentencePiece vocabulary created for corpus: "
                        f"[bold cyan]{os.path.basename(model_prefix)}[/bold cyan]"
                    )
                )

            temp_seq.close()
            os.unlink(temp_seq.name)
        # else:
        #     log.info(
        #         (
        #             f"Skipped SP vocabulary creation for corpus: "
        #             f"[bold cyan]{os.path.basename(model_prefix)}[/bold cyan]. "
        #             "Already exists."
        #         )
        #     )

    def load_sp_model(self) -> sp.SentencePieceProcessor:
        """
        Load the created SentencePiece model from file.

        This method loads a pre-trained SentencePiece model using the specified
        model prefix. It validates the existence of the model file before loading
        and will exit the program if the file is not found.

        Args:
            None

        Returns:
            sentencepiece.SentencePieceProcessor: Loaded SentencePiece processor object
            that can be used for encoding/decoding text.

        Raises:
            SystemExit: Exits the program with status code 1 if the model file does not exist.
        """
        model_file = os.path.join(self.model_prefix + f"{SFC.SP_C_CRPS_SUFFIX}")

        if not SFHelpers._defined(model_file, "SentencePiece model file"):
            raise ValueError()
        if not SFHelpers._input_file_exists(model_file, "SentencePiece model file"):
            raise ValueError()

        # Load and return the SentencePiece processor
        encoder = sp.SentencePieceProcessor()
        encoder.load(model_file)
        return encoder


class DNAEncoder:
    """Encoder for DNA sequences."""

    def __init__(
        self,
    ) -> None:
        """
        Initialize the custom DNA Encoder methods for StrainFish.
        """
        pass

    @staticmethod
    def get_kmers(seq: Optional[str] = None, size: Optional[int] = SFC.DKMER) -> List:
        """
        Generate k-mers from a DNA sequence.

        The method removes all ambiguous nucleotides (`N`/`n`) from the
        input sequence, converts the remaining characters to upper case and
        then slices the sequence into overlapping k-mers of the specified
        `size`.  The k-mer list is returned as plain Python strings.

        Args:
            seq (str, optional): Input DNA sequence. If `None` the method
                prints an error and exits.  The sequence may contain
                ambiguous bases which are removed before k-mer generation.
            size (int, optional): Length of each k-mer. Defaults to the
                module-level constant `DKMER` (51).

        Returns:
            list[str]: A list containing all valid k-mers.  If the input
                sequence is empty after removal of `N`/`n` the method
                returns an empty list.

        Raises:
            SystemExit: Exits the program with status code 1 if `seq` is
                not defined (`None` or an empty string).
        """
        if not SFHelpers._defined(seq, "Input DNA sequence"):
            raise ValueError()

        # Remove ambiguous nucleotides (N) from sequence
        kmers = []
        seq = re.sub("[Nn]", "", str(seq.upper()))

        # After replace N/n's if size is zero, return empty
        # array
        if len(seq) == 0:
            return list(np.empty(0))

        for i in range(0, len(seq)):
            chunk = seq[i : i + size]
            if len(chunk) >= size:
                kmers.append(str(chunk))

        return kmers

    @staticmethod
    def compute_vectors(
        vectorizer: TfidfVectorizer = None, kmers: Optional[List] = None
    ) -> List:
        """
        Transform a list of k-mers into a TF-IDF feature matrix.

        The method verifies that a valid `TfidfVectorizer` instance and a
        non-empty list of k-mers have been supplied, then fits the vectoriser
        on the provided k-mers and returns the resulting dense NumPy array.
        An empty input list yields an empty array.

        Args:
            vectorizer (TfidfVectorizer, optional): A scikit-learn
                `TfidfVectorizer` instance.  The vectoriser will be
                fitted on `kmers`; if `None`, the method terminates.
            kmers (list[str], optional): A list of k-mer strings.  If the
                list is empty or ``None`` the method exits.

        Returns:
            np.ndarray: A dense NumPy array of shape
                `(len(kmers), n_features)` containing the TF-IDF
                representation.  When `kmers` is empty an array of
                shape `(0,)` is returned.

        Raises:
            SystemExit: Exits the program with status code 1 if either
                `vectorizer` or `kmers` are not defined, or if
                `vectorizer` is not an instance of
                `sklearn.feature_extraction.text.TfidfVectorizer`.
        """
        if not SFHelpers._defined(kmers, "A list of k-mer's"):
            raise ValueError()
        if not SFHelpers._defined(vectorizer, "Vectorizer"):
            raise ValueError()
        if not isinstance(vectorizer, TfidfVectorizer):
            log.error(f"The vectorizer {vectorizer} is not of type TfidfVectorizer!")
            raise TypeError(f"Got {type(vectorizer).__name__} instead")

        return (
            np.round(vectorizer.transform(kmers).toarray(), decimals=4)
            if len(kmers) > 0
            else list(np.array(0))
        )

        # if len(kmers) > 0:
        #     variances = []
        #     vectorized = vectorizer.fit_transform(kmers)

        #     for n in range(1, vectorized.shape[1]):
        #         curr_svd = SVD(n_components=n, algorithm="arpack")
        #         curr_svd.fit(vectorized)
        #         variances.append(curr_svd.explained_variance_radio_.sum())
        #     calculated_optimal_compnonent = np.argmax(np.array(variances) >= 0.97) + 1
        #     optimal_svd = SVD(
        #         n_components=calculated_optimal_compnonent, algorithm="arpack"
        #     )
        #     print(calculated_optimal_compnonent)
        #     print(optimal_svd)
        #     exit(0)
        #     return optimal_svd.fit_transform(vectorized)
        # else:
        #     return list(np.array(0))

    @staticmethod
    def compute_hashes(
        seq: Optional[str] = None,
        k: int = SFC.DKMER,
        n_hashes: int = SFC.NH,
        pseknc_w: float = SFC.PSEKNC_W,
    ) -> List:
        """
        Compute MinHashes given a sequence.

        This method generates MinHash signatures for a given DNA sequence using
        the Sourmash library. It removes ambiguous nucleotides (N) from the sequence
        before computing the hashes and returns the hash values as a list.

        Args:
            seq (str, optional): Input DNA sequence string. Defaults to None.
            k (int): K-mer size for MinHash computation. Defaults to 51.
            n_hashes (int): Number of hash values to generate. Defaults to 100.
            pseknc_w (float): The weight factor for PseKNC during DNA encoding.

        Returns:
            list[int]: List of integer hash values representing the MinHash signature
                of the input sequence.

        Raises:
            SystemExit: Exits the program with status code 1 if input sequence is None.

        Note:
            - The function removes all 'N' characters from the sequence before processing.
            - Uses MinHash implementation for efficient hash computation.
            - The returned list contains hash representation of DNA strings.
        """
        if not SFHelpers._defined(seq, "Input DNA sequence"):
            raise ValueError()

        # Create MinHash object with specified parameters
        if n_hashes == 0:
            mh = sm.MinHash(n=n_hashes, ksize=k, scaled=1)
        else:
            mh = sm.MinHash(n=n_hashes, ksize=k)

        # Remove ambiguous nucleotides (N) from sequence
        seq = re.sub("[Nn]", "", str(seq))

        # After replace N/n's if size is zero, return empty
        # array
        if len(seq) == 0:
            return list(np.empty(0))

        # Add sequence to MinHash object
        mh.add_sequence(seq)

        # Normalize to value between 0 and 1
        m_hashes = np.array(mh.hashes, dtype=np.uint64) / np.iinfo(np.uint64).max

        # Calculate PseKNC weights.
        ratio_of_gc = (seq.count("G") + seq.count("C")) / len(seq)
        ratio_of_at = (seq.count("A") + seq.count("T")) / len(seq)

        nuc_counts = Counter(seq)
        valid_nucs = list("ATGC")
        nuc_distribution = [
            nuc_counts[n] / len(seq) for n in valid_nucs if n in nuc_counts
        ]
        shannon_entropy = -sum(
            freq * np.log2(freq) for freq in nuc_distribution if freq > 0
        )

        if not nuc_distribution:
            shannon_entropy = 0.0

        kmer_properties = np.array(
            [ratio_of_gc, ratio_of_at, shannon_entropy], dtype=np.float32
        )
        weighted_kmer_properties = 1 + (pseknc_w * kmer_properties.sum())

        pseknc_kmer_properties = pseknc_w * kmer_properties

        # Return the hash values as a list
        return list(
            np.concatenate(
                [
                    pseknc_kmer_properties / weighted_kmer_properties,
                    m_hashes / weighted_kmer_properties,
                ]
            )
        )

        # return list(np.array(mh.hashes, dtype=np.uint64) / np.iinfo(np.uint64).max)


class StrainFishEncoder:
    """Global encoder for SP, TF and MH."""

    def __init__(
        self,
        seq: Optional[str] = None,
        encoder: Optional[Any] = None,
        chunk_size: int = SFC.CHKS,
        factor: int = SFC.FC,
        k: int = SFC.DKMER,
        n_hashes: int = SFC.NH,
        chunk_status: Optional[Any] = None,
        padding_status: Optional[Any] = None,
        max_encoded_len_status: Optional[Any] = None,
    ) -> None:
        """
        Initialize the Global Encoder to encode DNA sequence into chunks
        with optional padding.

        Args:
            seq (str, optional): Input DNA sequence string. Defaults to None.
            encoder: SentencePiece encoder object. Defaults to None.
            chunk_size (int): Size of each sequence chunk. Defaults to 21.
            factor (int): Factor used to calculate overlap. Defaults to 21.
            k (int): K-mer size for MinHash computation. Defaults to 51.
            n_hashes (int): Number of hash values for MinHash. Defaults to 100.
            chunk_status: Progress bar status object for chunking. Defaults to None.
            padding_status: Progress bar status object for padding. Defaults to None.
            max_encoded_len_status: Progress bar status object for max length calculation.
                Defaults to None.

        Note:
            - Sequences are split with overlapping or non-overlapping chunks based on factor parameter.
            - If no encoder is provided, MinHash signatures are computed instead.
            - All sequences are padded to the maximum length for uniform processing.
            - Progress bars are updated during each major step of the process.
        """
        self.seq = seq
        self.encoder = encoder
        self.chunk_size = chunk_size
        self.factor = factor
        self.k = k
        self.n_hashes = n_hashes
        self.chunk_status = chunk_status
        self.padding_status = padding_status
        self.max_encoded_len_status = max_encoded_len_status

    @staticmethod
    def max_encode_len(encoded: Optional[List[List]] = None) -> Union[np.int64, bool]:
        """
        Use NumPy to get the index of maximum list length.

        This method determines the index of the longest list within a nested list structure
        using NumPy's argmax function. It handles both nested list inputs and single list inputs.

        Args:
            encoded (list[list], optional): Nested list structure containing sequences or lists.
                Can be None, in which case the function will exit with status code 1.
                Defaults to None.

        Returns:
            numpy.int64 | bool: Index of the longest list in the nested structure if input is a list,
                False if input is not a list.

        Raises:
            SystemExit: Exits the program with status code 1 if input encoded is None.

        Note:
            - For nested list inputs, the function calculates the length of each sublist.
                and returns the index of the longest one using NumPy's argmax.
            - If input is not a list type, the function returns False.
            - The function uses NumPy for efficient computation of maximum length indices.
        """
        if not SFHelpers._defined(encoded, "Encoded list"):
            raise ValueError()

        if isinstance(encoded, list):
            # Calculate lengths of all sublists
            lengths = [len(enc) for enc in encoded]

            # Return index of maximum length using NumPy
            return np.argmax(np.array(lengths))
        else:
            return False

    @staticmethod
    def count_fa_recs(fasta_file: Optional[os.PathLike]) -> int:
        """
        Count the number of FASTA records in a file.

        Args:
            fasta_file (Optional[os.PathLike]): Path to a FASTA file.
                If ``None`` the function returns ``0`` and exits with an
                error message.

        Returns:
            int: The total number of FASTA records found in *fasta_file*.
        """
        if not SFHelpers._defined(fasta_file, "FASTA file"):
            raise ValueError()

        # Get total FASTA records.
        with open(fasta_file, "r") as fah:
            return sum(1 for _ in SeqIO.parse(fah, "fasta"))
        fah.close()

    @staticmethod
    def init_progress_bars(
        total_system_mem: Optional[int],
        total: int = 1,
    ) -> Tuple[TaskID, TaskID, TaskID, TaskID, TaskID, TaskID]:
        """
        Initialise six Rich progress bars used by the encoder.

        Args:
            total_system_mem (Optional[int]): Total physical RAM in bytes.
                The value is used to initialise the "Memory used" bar and
                is validated with :py:meth:`SFHelpers._defined`. If
                `None` the program exits with an error.
            total (Optional[int]): Expected number of tasks for the
                "Computing hashes", "Chunked sequence into" and
                "Maximum length for padding" bars. Defaults to `1`.

        Returns:
            Tuple[TaskID, TaskID, TaskID, TaskID, TaskID, TaskID]:
                Identifiers for the six progress bars in the order
                returned.

        Note:
            - The helper function relies on the global `progress` instance
                defined in logging_utils.
            - Each bar is created with an empty `info` field because
              Rich automatically displays the bar's *total* value.
            - The "GPU Memory used" bar fetches its maximum value from
                :pyclass:`GPUMemInfo`.
        """

        # Try loading GPU helpers first.
        try:
            _ = GPUMemInfo.fetch().total
        except Exception as e:
            raise RuntimeError() from e

        if not SFHelpers._defined(total_system_mem, "Total system memory used"):
            raise ValueError()

        encode_status = progress.add_task("Processing sequence", total=total, info=": ")
        chunk_status = progress.add_task(
            "  - Chunked sequence into", total=total, info=": "
        )
        max_encoded_len_status = progress.add_task(
            "  - Maximum length for padding", total=total, info=": "
        )
        padding_status = progress.add_task("  - Padded", total=total, info=": ")
        curr_memory_status = progress.add_task(
            "  - Memory used", total=total_system_mem, info=": "
        )
        gpu_memory_status = progress.add_task(
            "  - GPU Memory used", total=GPUMemInfo.fetch().total, info=": "
        )

        return (
            encode_status,
            chunk_status,
            max_encoded_len_status,
            padding_status,
            curr_memory_status,
            gpu_memory_status,
        )

    @staticmethod
    def log_memory_used(
        memory_used: Optional[int], total_system_mem: Optional[int]
    ) -> None:
        """
        Log the current process memory and the GPU memory consumption.

        Args:
            memory_used (Optional[int]): Bytes of RAM used by the
                current process. If `None` the program exits with
                an error.
            total_system_mem (Optional[int]): Total physical RAM in bytes,
                validated with :py:meth:`SFHelpers._defined`. If
                `None` the program exits with an error.

        Returns:
            None

        Note:
            - The helper function writes two log messages in Rich
                style: one for system RAM and one for GPU RAM.
            - The values are converted to a human-readable string via
                :py:meth:`SFHelpers._human_bytes`.
            - If either *memory_used* or *total_system_mem* is undefined
                the program terminates immediately with exception.
        """
        if not SFHelpers._defined(memory_used, "Process memory used"):
            raise ValueError()

        if not SFHelpers._defined(total_system_mem, "Total system memory used"):
            raise ValueError()

        log.info(
            (
                f"Memory used: [bold cyan]{SFHelpers._human_bytes(memory_used)}[/bold cyan]"
                f" / [bold cyan]{SFHelpers._human_bytes(total_system_mem)}[/bold cyan]."
            ),
        )
        log.info(
            (
                f"GPU Memory used: [bold cyan]{SFHelpers._human_bytes(GPUMemInfo.fetch().used)}[/bold cyan]"
                f" / [bold cyan]{SFHelpers._human_bytes(GPUMemInfo.fetch().total)}[/bold cyan]."
            ),
        )

    @staticmethod
    def join_seqs(
        fasta_file: Optional[os.PathLike],
        min_length: Optional[int] = 1000,
        sep: Optional[str] = "",
    ) -> str:
        """
        Concatenate all qualifying sequences in a multi-FASTA file into
        a single contiguous FASTA string.

        Args:
            fasta_file (Optional[os.PathLike]): Path to the input FASTA
                file. If `None` the function terminates with an
                error.
            min_length (Optional[int]): Minimum sequence length
                (in bases) required for a record to be included.
                Shorter sequences are ignored. Defaults to `1000`.
            sep: (Optional[str]): Joine by this separator. Default
                is empty string.

        Returns:
            str: The concatenated sequence with all `N`/`n` characters
            removed.

        Note:
            - The function streams the input with `SeqIO.parse`,
                therefore it can handle files of arbitrary size.
            - Sequences shorter than *min_length* are filtered out before
                concatenation.
            - The regular expression substitution removes any ambiguous
                bases (`N` or `n`) from the final string.
        """
        # Return a single FASTA for a multi-FASTA file.
        seqs = [
            str(rec.seq)
            for rec in SeqIO.parse(fasta_file, "fasta")
            if len(rec.seq) >= int(min_length)
        ]

        if len(seqs) == 0:
            log.error(
                (
                    f"All sequences in the input FASTA are less than {min_length} bp. "
                    "Cannot proceed!"
                )
            )
            log.info(
                (
                    "You can try to retrain with a smaller chunk size "
                    "or create rough contigs."
                )
            )
            progress.stop()
            raise ValueError()

        joined_seqs = sep.join(seqs)

        return re.sub("[Nn]", "", joined_seqs)

    @staticmethod
    def pad_or_truncate(
        seqs: Optional[NDArray[np.integer]],
        pad_length: Optional[int],
    ) -> np.ndarray:
        """
        Pad or truncate each sequence so that every resulting array
        has the same length ``median_pad_length``.

        Args:
            seqs : iterable of numpy array of sequence objects
            pad_length (int): Desired length for every output sequence.

        Returns:
            np.ndarray
                A 2D array where each row is a padded and/pr truncated
                copy of the corresponding input sequence.
        """
        processed_seqs = np.array(
            [
                # Pad with zeros if the sequence is too short
                (
                    np.pad(
                        np.asarray(seq),
                        (0, max(0, pad_length - len(seq))),
                        mode="constant",
                        constant_values=0,
                    )
                    if len(seq) < pad_length  # pad
                    else np.asarray(seq)[:pad_length]  # else truncate
                )  # truncate if too long
                for seq in seqs
            ]
        )
        return processed_seqs

    def encode_seq_chunks(
        self,
        seq: Optional[str] = None,
        encoder: Optional[Any] = None,
    ) -> List[Union[Union[NDArray[Any], spmatrix], int]]:
        """
        This method splits a DNA sequence into overlapping chunks and encodes them
        using either a provided encoder or computes MinHash signatures. The encoded
        sequences are then padded to the maximum length for uniform processing.

        Args:
            seq (str, optional): Input DNA sequence string. Defaults to None.
            encoder: SentencePiece encoder object. Defaults to None.

        Returns:
            list: List containing encoded sequences as numpy array or sparse matrix
                and maximum length as integer.

        Raises:
            SystemExit: Exits with status code 1 if any required parameter is None.
        """
        if not SFHelpers._defined(self.seq, "DNA Sequence"):
            raise ValueError()
        if not SFHelpers._defined(self.encoder, "Encoder"):
            raise ValueError()
        if not SFHelpers._defined(self.chunk_status, "Chunk status"):
            raise ValueError()
        if not SFHelpers._defined(
            self.padding_status,
            "Padding status",
        ):
            raise ValueError()
        if not SFHelpers._defined(
            self.max_encoded_len_status,
            "Maximum length status",
        ):
            raise ValueError()

        if SFHelpers._defined(seq, "DNA Sequence"):
            self.seq = seq
        if SFHelpers._defined(encoder, "Encoder"):
            self.encoder = encoder

        if len(self.seq) < self.chunk_size:
            chunk_size = len(self.seq)
        else:
            chunk_size = self.chunk_size

        if isinstance(self.encoder, TfidfVectorizer):
            factor = chunk_size
        else:
            factor = self.factor

        overlap = round(chunk_size / factor)
        overlap = overlap if overlap != 1 else 0

        if overlap > chunk_size:
            log.error(
                (
                    f"Overlap size ({overlap}) cannot be"
                    f"greater than chunk size ({chunk_size})."
                )
            )
            raise ValueError()

        eseqs, num_seqs_padded = [], []

        if isinstance(self.encoder, TfidfVectorizer):
            step_size = chunk_size - overlap
            y_range = len(self.seq)
        elif self.encoder:
            step_size = overlap
            y_range = len(self.seq) - chunk_size + 1

        for i in range(0, y_range, step_size):
            chunk = self.seq[i : i + chunk_size]
            if len(chunk) > overlap:
                if isinstance(self.encoder, TfidfVectorizer):
                    eseqs.append(DNAEncoder.get_kmers(seq=chunk, size=self.k))
                elif self.encoder:
                    eseqs.append(self.encoder.encode_as_ids(chunk))
                else:
                    eseqs.append(
                        DNAEncoder.compute_hashes(
                            chunk, k=self.k, n_hashes=self.n_hashes
                        )
                    )

        progress.update(
            self.chunk_status,
            advance=1,
            info=(
                f": [bold cyan]{len(eseqs)}[/bold cyan] sequence(s) with chunk size of "
                f"[bold cyan]{chunk_size}[/bold cyan] and an overlap of [bold cyan]{overlap}[/bold cyan]."
            ),
        )

        if isinstance(self.encoder, TfidfVectorizer):
            chunk_kmer_vocabulary = []
            all_chunks_kmers_list = eseqs

            for chunk_kmer_list in all_chunks_kmers_list:
                chunk_kmer_vocabulary.append(" ".join(chunk_kmer_list))

            eseqs = DNAEncoder.compute_vectors(
                self.encoder, [" ".join(chunk_kmer_vocabulary)]
            )

            max_encoded_len = eseqs.shape[1]
        elif not self.encoder:
            max_encoded_len = len(eseqs[StrainFishEncoder.max_encode_len(eseqs)])

            for eseq in eseqs:
                if len(eseq) < max_encoded_len:
                    num_seqs_padded.append(0)
                    for _ in range(0, max_encoded_len - len(eseq)):
                        eseq.append(0)

            eseqs = np.array(eseqs)
        else:
            sp_tokens = [" ".join(map(str, eseq)) for eseq in eseqs]
            vec = CountVectorizer(analyzer="word", token_pattern=r"\b\d+\b")
            eseqs = vec.fit_transform(sp_tokens)
            max_encoded_len = eseqs.shape[1]

        progress.update(
            self.max_encoded_len_status,
            advance=1,
            info=f": [bold cyan]{max_encoded_len}[/bold cyan].",
        )

        progress.update(
            self.padding_status,
            advance=1,
            info=(
                f": [bold cyan]{len(num_seqs_padded)}[/bold cyan] sequence chunk(s) with up "
                f"to a maximum length of [bold cyan]{max_encoded_len}[/bold cyan]."
            ),
        )

        return [eseqs, max_encoded_len]
