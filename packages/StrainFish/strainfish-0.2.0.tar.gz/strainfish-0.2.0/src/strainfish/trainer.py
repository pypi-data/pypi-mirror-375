"""
StrainFish training class for DNA sequences.

Kranti Konganti
(C) HFP, FDA.
"""

import os
from pathlib import Path
from typing import Dict

import cudf
import joblib
import numpy as np
import pandas as pd
import psutil
import scipy.sparse as scs
import xgboost as xgb
from Bio import SeqIO
from cuml.ensemble import RandomForestClassifier as rfc
from imblearn.combine import SMOTEENN
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import EditedNearestNeighbours as ENN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB as CNB

from .constants import SFConstants as SFC
from .encoder import DNAEncoder, SPEncoder, StrainFishEncoder
from .helpers import GPUMemInfo, SFHelpers
from .logging_utils import log, progress

# from sklearn.utils.class_weight import compute_sample_weight


class SFTrainer:

    def __init__(
        self,
        fasta_file: os.PathLike,
        label_file: os.PathLike,
        encode_method: int = SFC.SOMH,
        n_hashes: int = SFC.NH,
        k: int = SFC.DKMER,
        factor: int = SFC.FC,
        chunk_size: int = SFC.CHKS,
        pseknc_weight: float = SFC.PSEKNC_W,
        save_prefix: os.PathLike = None,
        xgb_params: Dict = {},
        rf_params: Dict = {},
        sp_params: Dict = {},
        imb_params: Dict = {},
    ) -> None:
        """
        StrainFish Trainer for DNA sequence based machine learning models.
        It orchestrates validation, k-mer production, chunking, padding and/or
        truncating and the full training and evaluation pipeline for sequence
        data.
        """
        self.fasta_file = fasta_file
        self.label_file = label_file
        self.encode_method = encode_method
        self.n_hashes = n_hashes
        self.k = k
        self.factor = factor
        self.chunk_size = chunk_size
        self.pseknc_weight = pseknc_weight
        self.save_prefix = save_prefix
        self.xgb_params = xgb_params
        self.rf_params = rf_params
        self.sp_params = sp_params
        self.imb_params = imb_params

    def train(self):
        """
        StrainFish core training using GPU-accelerated XGBoost and RandomForest.

        This method handles data loading, preprocessing, model training, and saving.
        It also includes progress tracking and logging for monitoring the training process.

        Args:
            fasta_file (str): Path to the FASTA file containing the sequences.
            label_file (str): Path to the CSV file containing labels for each sequence in the FASTA file.
            encode_method (str): The encoding method to use ("sm" is default).
            save_prefix (str): Prefix for the saved model files (e.g., "StrainFish"). If None, default filenames are used.
            xgb_params (dict): Dictionary of parameters for the XGBoost model.
            rf_params (dict): Dictionary of parameters for the RandomForest model.
            sp_params (dict): Dictionary of parameters for the SentencePiece corpus builder.
            imb_params (dict): Dictionary of imbalance parameters for performing balancing samples before training.
            chunk_size (int): The size of the chunks to split the sequences into during encoding.
            pseknc_weight (float): The weight factor for PseKNC during DNA encoding.
            factor (int): A factor used to calcualte base-pair overlap to be used during the encoding process.
            k (int):  The k-mer size for hash calculation.
            n_hashes (int): The number of hash functions to use during encoding.


        Returns:
            None. The trained models are saved to disk.

        Raises:
            SystemExit: If input files are missing or parameters are invalid, the program exits.
        """
        # Initial checks.
        if not SFHelpers._is_gpu_available():
            raise RuntimeError()
        if self.save_prefix is None:
            save_as_xgb = os.path.join(SFC.MODELS_DIR, SFC.PKG_NAME + SFC.XGB_SUFFIX)
            save_as_rf = os.path.join(SFC.MODELS_DIR, SFC.PKG_NAME + SFC.RF_SUFFIX)
            save_as_nb = os.path.join(SFC.MODELS_DIR, SFC.PKG_NAME + SFC.NB_SUFFIX)
            save_as_sp_crps = os.path.join(
                SFC.MODELS_DIR, SFC.PKG_NAME + SFC.SP_CRPS_SUFFIX
            )
            save_as_tf_crps = os.path.join(
                SFC.MODELS_DIR, SFC.PKG_NAME + SFC.TF_CRPS_SUFFIX
            )
            save_as_lbls = os.path.join(SFC.MODELS_DIR, SFC.PKG_NAME + SFC.LBL_SUFFIX)
        elif len(Path(self.save_prefix).parts) == 1:
            save_as_xgb = os.path.join(
                SFC.MODELS_DIR, f"{SFC.PKG_NAME}.{self.save_prefix}{SFC.XGB_SUFFIX}"
            )
            save_as_rf = os.path.join(
                SFC.MODELS_DIR, f"{SFC.PKG_NAME}.{self.save_prefix}{SFC.RF_SUFFIX}"
            )
            save_as_nb = os.path.join(
                SFC.MODELS_DIR, f"{SFC.PKG_NAME}.{self.save_prefix}{SFC.NB_SUFFIX}"
            )
            save_as_sp_crps = os.path.join(
                SFC.MODELS_DIR, f"{SFC.PKG_NAME}.{self.save_prefix}{SFC.SP_CRPS_SUFFIX}"
            )
            save_as_tf_crps = os.path.join(
                SFC.MODELS_DIR, f"{SFC.PKG_NAME}.{self.save_prefix}{SFC.TF_CRPS_SUFFIX}"
            )
            save_as_lbls = os.path.join(
                SFC.MODELS_DIR, f"{SFC.PKG_NAME}.{self.save_prefix}{SFC.LBL_SUFFIX}"
            )
        else:
            if Path(self.save_prefix).is_dir():
                log.info(
                    f"[green3]Model prefix is[/green3] [bold cyan]{SFC.PKG_NAME}[/bold cyan]."
                )
                self.save_prefix = os.path.join(self.save_prefix, SFC.PKG_NAME)
            else:
                log.info(
                    (
                        "[green3]Model prefix is[/green3] "
                        f"[bold cyan]{os.path.basename(self.save_prefix)}[/bold cyan]."
                    )
                )

            save_as_xgb = os.path.join(self.save_prefix + SFC.XGB_SUFFIX)
            save_as_rf = os.path.join(self.save_prefix + SFC.RF_SUFFIX)
            save_as_nb = os.path.join(self.save_prefix + SFC.NB_SUFFIX)
            save_as_sp_crps = os.path.join(self.save_prefix + SFC.SP_CRPS_SUFFIX)
            save_as_tf_crps = os.path.join(self.save_prefix + SFC.TF_CRPS_SUFFIX)
            save_as_lbls = os.path.join(self.save_prefix + SFC.LBL_SUFFIX)

        calculated_x_model_file_path = Path(save_as_xgb)
        models_dir = calculated_x_model_file_path.parent.resolve()

        try:
            if not os.path.exists(models_dir):
                log.info(
                    (
                        "Creating models directory "
                        f"[bold cyan]{os.path.basename(models_dir)}[/bold cyan]."
                    )
                )
                os.makedirs(models_dir)
        except Exception as e:
            log.error(
                (
                    "Unable to create models directory "
                    f"[bold cyan]{os.path.basename(models_dir)}[/bold cyan]. "
                    f"{e}"
                )
            )
            raise

        if not self.xgb_params or not self.rf_params:
            log.warning("Empty parameters for XGBoost and/or RandomForest.")
            log.error("Unable to proceed!")
            raise ValueError()

        # Current process
        process = psutil.Process()
        total_system_mem = psutil.virtual_memory().total

        log.info(
            (
                "[green3]Loading FASTA sequences from[/green3] "
                f"[bold cyan]{os.path.basename(self.fasta_file)}[/bold cyan]."
            )
        )

        if not SFHelpers._defined(
            self.fasta_file, "FASTA file"
        ) or not SFHelpers._input_file_exists(self.fasta_file, "Input FASTA file"):
            raise ValueError()

        if not SFHelpers._defined(
            self.label_file, "Lables file"
        ) or not SFHelpers._input_file_exists(
            self.label_file, "For each input FASTA sequence, we need a single label.\n"
        ):
            raise ValueError()

        labels_unfiltered_df = pd.read_csv(self.label_file)
        labels_counts = labels_unfiltered_df.label.value_counts()

        # Store which FASTA's to skip since there are less than
        # minority threshold
        if self.imb_params[SFC.IMBSKN] < self.imb_params[SFC.IMBSEN]:
            log.error(
                f"Value of {SFC.IMBSKN} for SMOTE should be less than {SFC.IMBSEN} for ENN."
            )
            raise ValueError()

        passed_fasta_labels = labels_counts[
            labels_counts > self.imb_params[SFC.IMBSKN]
        ].index

        # Remove features represented less than certain
        # number of times
        labels_df_min_removed = labels_unfiltered_df[
            labels_unfiltered_df.label.isin(passed_fasta_labels)
        ].copy()

        log.info(
            (
                f"[spring_green3]Removed[/spring_green3]"
                f" {labels_unfiltered_df.shape[0] - labels_df_min_removed.shape[0]}"
                " [spring_green3]sequences that are represented less than[/spring_green3]"
                f" {self.imb_params[SFC.IMBSKN]} [spring_green3]times[/spring_green3]."
            )
        )

        # Remove features represented more than certain
        # number of times
        if self.n_hashes is not None and self.encode_method == SFC.TFIDF:
            labels_df = labels_df_min_removed.groupby(labels_df_min_removed.label.name)[
                labels_df_min_removed.columns.tolist()
            ].apply(
                lambda d: d.sample(
                    n=min(len(d), self.n_hashes), random_state=self.rf_params[SFC.RFRS]
                )
            )
            log.info(
                "[spring_green3]Removed[/spring_green3]"
                f" {labels_df_min_removed.shape[0] - labels_df.shape[0]}"
                " [spring_green3]sequences that are repsented more than[/spring_green3]"
                f" {self.n_hashes} [spring_green3]times[/spring_green3]."
            )
        else:
            labels_df = labels_df_min_removed

        unique_labels = {label: i for i, label in enumerate(labels_df.label.unique())}

        labels_dict = {
            row.id: int(unique_labels[row.label]) for _, row in labels_df.iterrows()
        }

        log.info(
            (
                f"[green3]Saving label vectors to[/green3][bold cyan] "
                f"{os.path.basename(save_as_lbls)}[/bold cyan]."
            )
        )
        joblib.dump(unique_labels, save_as_lbls)

        # Start progress bar
        progress.start()
        total_fa_recs = StrainFishEncoder.count_fa_recs(self.fasta_file)

        if total_fa_recs != labels_unfiltered_df.shape[0]:
            log.error("Unequal Labels for input DNA Sequences! Kindly double-check.")
            log.error(
                f"Number of FASTA records: [bold cyan]{total_fa_recs}[/bold cyan]."
            )
            log.error(
                f"Number of Labels: [bold cyan]{labels_unfiltered_df.shape[0]}[/bold cyan]."
            )
            raise ValueError()

        seqs, labels, max_pad_lens = [], [], []
        (
            encode_status,
            chunk_status,
            max_encoded_len_status,
            padding_status,
            curr_memory_status,
            gpu_memory_status,
        ) = StrainFishEncoder.init_progress_bars(
            total_system_mem=total_system_mem, total=labels_df.shape[0]
        )

        # Initialize global StrainFish Encoder
        sfe = StrainFishEncoder(
            seq=str("Initializing..."),
            encoder=False,
            chunk_size=self.chunk_size,
            factor=self.factor,
            k=self.k,
            n_hashes=self.n_hashes,
            chunk_status=chunk_status,
            max_encoded_len_status=max_encoded_len_status,
            padding_status=padding_status,
        )

        # Initialize SP encoder
        sp = SPEncoder(
            seq=str("Intializing..."),
            model_prefix=save_as_sp_crps,
            max_sentencepiece_length=self.sp_params[SFC.SPMPLKN],
            max_sentence_length=self.sp_params[SFC.SPMSLKN],
            normalization_rule_name=self.sp_params[SFC.SPNRKN],
            vocab_size=self.sp_params[SFC.SPVSKN],
            model_type=self.sp_params[SFC.SPETKN],
            hard_vocab_limit=self.sp_params[SFC.SPHVLKN],
            character_coverage=self.sp_params[SFC.SPCCKN],
        )

        if self.encode_method == SFC.SPEC:
            new_line_seqs = StrainFishEncoder.join_seqs(
                fasta_file=self.fasta_file, min_length=int(self.chunk_size), sep="\n"
            )

            # Create SP Corpus model.
            log.info(
                (
                    "Checking to see if SP vocabulary needs to be created for "
                    f"[bold cyan]{os.path.basename(self.fasta_file)}[/bold cyan]."
                )
            )
            sp.tokenizer(seq=new_line_seqs)

            # Load created corpus model.
            log.info(
                f"Loading SP corpus model: [bold cyan]{os.path.basename(save_as_sp_crps)}[/bold cyan]"
            )

            dna_encoder = sp.load_sp_model()
            progress_root_info = ""
        elif self.encode_method == SFC.TFIDF:
            dna_vec: TfidfVectorizer = TfidfVectorizer(
                ngram_range=(1, 1),
                sublinear_tf=True,
                norm="l2",
                smooth_idf=True,
                token_pattern=r"(?u)\b\w+\b",
            )

            # Create TF Corpus.
            all_seqs = StrainFishEncoder.join_seqs(fasta_file=self.fasta_file)
            all_kmers = DNAEncoder.get_kmers(seq=all_seqs, size=self.k)
            dna_encoder = dna_vec.fit(raw_documents=[" ".join(all_kmers)])
            log.info(
                (
                    "[green3]Saving TF vocabulary to[/green3] "
                    f"[bold cyan]{os.path.basename(save_as_tf_crps)}[/bold cyan]."
                )
            )

            joblib.dump(dna_encoder, save_as_tf_crps)
            progress_root_info = ""
        elif self.encode_method == SFC.SOMH:
            dna_encoder = False
            progress_root_info = f"n_hashes=[bold cyan]{self.n_hashes}[/bold cyan], "

            # elif self.encode_method == SOMH:
        for rec in SeqIO.parse(self.fasta_file, format="fasta"):
            if rec.id not in labels_dict.keys():
                continue
            progress.update(
                encode_status,
                advance=1,
                info=(
                    f": [bold cyan]{rec.id}[/bold cyan], {progress_root_info}"
                    f"k=[bold cyan]{self.k}[/bold cyan]."
                ),
            )
            progress.update(
                curr_memory_status,
                completed=process.memory_info().rss,
                info=(
                    f": [bold cyan]{SFHelpers._human_bytes(process.memory_info().rss)}[/bold cyan]"
                    f" / [bold cyan]{SFHelpers._human_bytes(total_system_mem)}[/bold cyan]."
                ),
            )
            progress.update(
                gpu_memory_status,
                completed=GPUMemInfo.fetch().used,
                info=(
                    f": [bold cyan]{SFHelpers._human_bytes(GPUMemInfo.fetch().used)}[/bold cyan]"
                    f" / [bold cyan]{SFHelpers._human_bytes(GPUMemInfo.fetch().total)}[/bold cyan]."
                ),
            )

            seq_chunks, max_pad_len = sfe.encode_seq_chunks(
                seq=str(rec.seq), encoder=dna_encoder
            )
            max_pad_lens.append(max_pad_len)
            seqs.extend(seq_chunks)
            labels.extend([labels_dict[rec.id]] * np.shape(seq_chunks)[0])

        progress.stop()
        sfe.log_memory_used(
            memory_used=process.memory_info().rss, total_system_mem=total_system_mem
        )

        if self.encode_method in (SFC.SOMH, SFC.TFIDF):
            pad_length = int(np.median(max_pad_lens))
            Seqs = sfe.pad_or_truncate(seqs, pad_length)
        elif self.encode_method == SFC.SPEC:
            pad_length = int(np.min(max_pad_lens))

            seqs_csr = [seq[:, :pad_length] for seq in seqs]
            Seqs = scs.vstack(seqs_csr, format="csr").toarray()

        log.info(
            f"Adjusted arrays (padding and/or truncating) to feature size: {pad_length}."
        )
        Labels = np.array(labels)

        log.info(f"Feature matrix created of shape: {np.shape(Seqs)}.")
        log.info(f"Label vector created of shape: {np.shape(Labels)}.")

        log.info("[spring_green3]Balancing label vectors for XGBoost[/spring_green3].")
        # xg_imbal_weights = compute_sample_weight(
        #     class_weight=self.xgb_params[IMCLSW], y=Labels
        # )

        log.info(
            "[spring_green3]Balancing label vectors for RandomForest[/spring_green3]."
        )
        log.info(
            "[spring_green3]Balancing label vectors for Naive Bayes Classifier[/spring_green3]."
        )

        smote = SMOTE(k_neighbors=self.imb_params[SFC.IMBSKN])
        enn = ENN(n_neighbors=self.imb_params[SFC.IMBSEN])

        smote_enn = SMOTEENN(
            random_state=self.rf_params[SFC.RFRS],
            sampling_strategy=self.imb_params[SFC.IMBSENNSS],
            n_jobs=int(self.imb_params[SFC.IMBSENNNJ]),
            smote=smote,
            enn=enn,
        )

        Seqs_Bal, Labels_Bal = smote_enn.fit_resample(Seqs, Labels)
        # xgb_train = xgb.DMatrix(data=Seqs, label=Labels, weight=xg_imbal_weights)
        xgb_train = xgb.DMatrix(data=Seqs_Bal, label=Labels_Bal)
        num_rounds = self.xgb_params.pop(SFC.NBR)  # Number of boosting rounds
        # early_stopping_rounds = self.xgb_params.pop(ESR)
        _ = self.xgb_params.pop(SFC.ESR)
        _ = self.xgb_params.pop(SFC.IMCLSW)
        verbose_eval = self.xgb_params.pop(SFC.VE)
        self.xgb_params[SFC.NUMC] = len(np.unique(Labels))

        log.info("[green3]Starting training using Naive Bayes Classifier")
        cnb_m = CNB()
        cnb_m.fit(Seqs_Bal, Labels_Bal)

        log.info(
            f"[green3]Saving Naive Bayes model to[/green3] [bold cyan]{os.path.basename(save_as_nb)}[/bold cyan]."
        )
        joblib.dump(cnb_m, save_as_nb)

        log.info("[green3]Starting training using XGBoost[/green3].")
        xgt = xgb.train(
            self.xgb_params,
            xgb_train,
            num_rounds,
            verbose_eval=verbose_eval,
        )

        log.info("[green3]Saving StrainFish training parameters.[/green3]")
        xgt.set_attr(
            **{
                SFC.DKMERN: sfe.k,
                SFC.CHKSN: sfe.chunk_size,
                SFC.NHN: sfe.n_hashes,
                SFC.FCN: sfe.factor,
                SFC.ENCDRN: sfe.encoder,
                SFC.PDLEN: pad_length,
            }
        )

        log.info(
            f"[green3]Saving XGBoost model to[/green3] [bold cyan]{os.path.basename(save_as_xgb)}[/bold cyan]."
        )
        xgt.save_model(fname=save_as_xgb)
        sfe.log_memory_used(
            memory_used=process.memory_info().rss, total_system_mem=total_system_mem
        )
        log.info("[green3]Starting training using RandomForest[/green3].")

        # RandomForest
        rf = rfc(
            n_estimators=int(self.rf_params[SFC.RFNE]),
            max_depth=int(self.rf_params[SFC.RFMD]),
            random_state=int(self.rf_params[SFC.RFRS]),
            n_bins=int(self.rf_params[SFC.RFNB]),
            max_features=self.rf_params[SFC.RFMF],
            min_samples_leaf=float(self.rf_params[SFC.RFMSL]),
            min_samples_split=float(self.rf_params[SFC.RFMSS]),
            bootstrap=bool(self.rf_params[SFC.RFBOO]),
            split_criterion=self.rf_params[SFC.RFSC],
            verbose=self.rf_params[SFC.RFVRB],
        )

        rf.fit(cudf.DataFrame(Seqs_Bal), cudf.Series(Labels_Bal))
        sfe.log_memory_used(
            memory_used=process.memory_info().rss, total_system_mem=total_system_mem
        )
        log.info(
            f"[green3]Saving RandomForest[/green3] model to [bold cyan]{os.path.basename(save_as_rf)}[/bold cyan]."
        )
        rf.convert_to_treelite_model().serialize(save_as_rf)
