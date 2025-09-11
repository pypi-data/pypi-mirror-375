"""
StrainFish predictor class for DNA sequences.

Kranti Konganti
(C) HFP, FDA.
"""

import os
from pathlib import Path
from typing import Any, Mapping

import joblib
import numpy as np
import pandas as pd
import psutil
import sentencepiece as sp
import treelite as tl
import xgboost as xgb
from rich.panel import Panel
from rich.table import Table as T
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB as CNB

from .configs.prediction_defaults import PredictionResult
from .constants import SFConstants as SFC
from .encoder import StrainFishEncoder as sfe
from .helpers import GPUMemInfo, SFHelpers
from .logging_utils import console, log, progress
from .models import SFModels
from .probabilities import SFProbs


class SFPredictor:
    def __init__(
        self,
        fasta_file: os.PathLike,
        model: str,
        output: os.PathLike,
        encode_method: str,
        all_params: dict,
    ) -> None:
        """
        Predicts outcomes based on input FASTA files and trained models.

        Takes in either a FASTA file or a directory containing FASTA files,
        encodes input sequences according to StrainFish algorithm,
        performs predictions, and generates a report of the results.

        Args:
            fasta_file (os.PathLike): Path to a FASTA file or directory of FASTA files.
            model (str): Path to the trained model file.
            output (os.PathLike): Path to the output file for results.
            all_params (dict): Dictionary of parameters used for prediction.
        """
        self.fasta_file = fasta_file
        self.model = model
        self.output = output
        self.encode_method = encode_method
        self.all_params = all_params

    @staticmethod
    def runner(
        xgt: xgb.Booster,
        rf: tl.Model,
        nbt: CNB,
        s_model_file: os.PathLike,
        t_crps_file: os.PathLike,
        sfe_predict: sfe,
        fasta_file: os.PathLike,
        labels: os.PathLike,
        encode_method: str,
        padding_length: int,
        all_params: Mapping[str, Any],
        chunk_size: int = SFC.CHKS,
        kmer_size: int = SFC.DKMER,
    ) -> pd.DataFrame:
        """
        Runs the prediction process for a single FASTA file.

        Args:
            xgt (xgb.Booster): Trained XGBoost booster.
            rf (tl.Model): Trained RandomForest model.
            s_model_file (os.PathLike): SP corpus file.
            t_crps_file (os.PathLike): TF corpus file.
            sfe_predict (sfe): SFEncoder object for sequence encoding.
            fasta_file (os.PathLike): Path to the FASTA file.
            labels (Mapping[str, Any]): Mapping of labels to values.
            encode_method (str): The encoding method used during training.
            padding_length (int): The padding length calculated during training and stored in model.
            all_params (Mapping[str, Any]): Dictionary of parameters.
            chunk_size (int, optional): Chunk size for sequence encoding. Defaults to CHKS.
            kmer_size (int, optional): k-mer size used for training.

        Returns:
            pd.DataFrame: DataFrame containing the prediction results.
        """

        # Validate inputs
        if not SFHelpers._defined(
            fasta_file, "FASTA file"
        ) or not SFHelpers._input_file_exists(fasta_file, "Input FASTA file"):
            raise ValueError()

        if encode_method in (SFC.SOMH, SFC.TFIDF):
            if encode_method == SFC.SOMH:
                dna_encoder = False
            elif encode_method == SFC.TFIDF:
                if not SFHelpers._defined(
                    t_crps_file, "TF Corpus file"
                ) or not SFHelpers._input_file_exists(t_crps_file, "TF Corpus file"):
                    raise ValueError()

                dna_encoder: TfidfVectorizer = joblib.load(t_crps_file)

            seqs, max_encoded_len = sfe_predict.encode_seq_chunks(
                seq=sfe.join_seqs(fasta_file, min_length=int(chunk_size)),
                encoder=dna_encoder,
            )

            seqs_arr = sfe_predict.pad_or_truncate(seqs, max_encoded_len)
            Seqs = seqs_arr[:, : int(padding_length)]
        elif encode_method == SFC.SPEC:
            if not SFHelpers._defined(
                s_model_file, "SP Corpus file"
            ) or not SFHelpers._input_file_exists(s_model_file, "SP Corpus file"):
                raise ValueError()
            seqs_csr, _ = sfe_predict.encode_seq_chunks(
                seq=sfe.join_seqs(fasta_file, min_length=int(chunk_size)),
                encoder=sp.SentencePieceProcessor(s_model_file),
            )
            Seqs = seqs_csr[:, : int(padding_length)].toarray()

        Sample = (
            all_params[SFC.SMPNM]
            if all_params[SFC.SMPNM] is not None
            else Path(fasta_file).stem
        )

        # XGBoost prediction
        xg_probs = xgt.predict(xgb.DMatrix(Seqs), output_margin=False)

        # Get average probabilities
        xg_avg_probs = SFProbs.get_avg_probs(
            xg_probs,
            min_percent=all_params[SFC.PRMIP],
            threshold=all_params[SFC.PRTHR],
        )

        rf_probs = tl.gtil.predict(rf, Seqs).squeeze(axis=1)

        rf_avg_probs = SFProbs.get_avg_probs(
            rf_probs,
            min_percent=all_params[SFC.PRMIP],
            threshold=all_params[SFC.PRTHR],
        )

        # Naive Bayes prediction
        nb_probs = nbt.predict_proba(Seqs)

        nb_avg_probs = SFProbs.get_avg_probs(
            nb_probs,
            min_percent=all_params[SFC.PRMIP],
            threshold=all_params[SFC.PRTHR],
        )

        # Initialize empty DataFrame.
        # 0: Top hit (hard predict, for now)
        res_df = pd.DataFrame()
        results = PredictionResult()
        calculated_probability_weights, calculated_model_supports = [], []

        # Create list of raw and avg probabolities
        all_raw_probs = [xg_probs, rf_probs, nb_probs]
        all_probs = [xg_avg_probs, rf_avg_probs, nb_avg_probs]

        # Create list of avg probablility lengths
        all_probs_lens = [
            len(xg_avg_probs[SFC.PRKIDX]),
            len(rf_avg_probs[SFC.PRKIDX]),
            len(nb_avg_probs[SFC.PRKIDX]),
        ]

        # User defined weights to be applied
        user_probs_weights = [
            all_params[SFC.XGBWT],
            (1 - all_params[SFC.XGBWT]) / 2,
            (1 - all_params[SFC.XGBWT]) / 2,
        ]

        if all(probs_len != 0 for probs_len in all_probs_lens):
            agreed_idxs, agreed_label = SFModels.check_ensemble_model_agreement(
                [
                    labels[xg_avg_probs[SFC.PRKIDX][0]],
                    labels[rf_avg_probs[SFC.PRKIDX][0]],
                    labels[nb_avg_probs[SFC.PRKIDX][0]],
                ]
            )

            for idx in agreed_idxs:
                # if len(agreed_idxs) > 1:
                #     user_prob_weight = user_probs_weights[idx]
                # else:
                #     user_prob_weight = 1

                calculated_probability_weights.insert(
                    idx, all_probs[idx][SFC.PRAVG] * user_probs_weights[idx]
                )
                calculated_model_supports.insert(
                    idx,
                    (all_probs[idx][SFC.PRCNT] / np.shape(all_raw_probs[idx])[0]) * 100,
                )

            # At least one index is returned
            results.predicted = agreed_label
            results.num_agreed = len(agreed_idxs)
            results.weighted_prob = sum(calculated_probability_weights)
            results.weighted_support = (
                sum(calculated_model_supports) / results.num_agreed
            )

            if 1 < results.num_agreed <= SFC.NUM_MODELS:
                results.confidence = SFC.VHCONF
            elif results.weighted_prob >= SFC.MODTHR:
                results.confidence = SFC.HCONF
            elif SFC.LOWTHR < results.weighted_prob <= SFC.MODTHR:
                results.confidence = SFC.MCONF
            elif results.weighted_prob < SFC.LOWTHR:
                results.confidence = SFC.LCONF

            if results.num_agreed == 1:
                log.info(
                    (
                        "[orange_red1]The models showed disagreement between its predictions"
                        f" for sample [/orange_red1][ [bold cyan]{Sample}[/bold cyan] ]"
                        ". [orange_red1]Consider verifying the results using "
                        "alternative methods[/orange_red1]."
                    )
                )

        # Bayesian posterior probability
        # weighted_support_frac = weighted_support / 100.0
        # post_prob = (weighted_support_frac * weighted_prob) / (
        #     weighted_support_frac * weighted_prob
        #     + (1 - weighted_support_frac) * (1 - weighted_prob)
        # )

        # Consturct results row
        res_df = (
            pd.DataFrame(
                np.concatenate(
                    [
                        np.array([Sample]),
                        np.array([results.predicted]),
                        np.array([results.confidence]),
                        np.array([results.weighted_prob]),
                        np.array([results.weighted_support]),
                        np.array([results.num_agreed]),
                    ]
                ),
            )
            .transpose()
            .set_axis(
                [
                    "Sample",
                    f"{SFC.PKG_NAME} Prediction",
                    "Confidence",
                    "Probability",
                    "% Support",
                    "Num Agreed",
                ],
                axis=1,
            )
        )

        return res_df

    def predict(self) -> None:
        """
        Perform predictions on a collection of FASTA files and produce a
        CSV report and a console table.

        The method loads the StrainFish trained models that belong
        to the instance, runs the encoder and the prediction routine for
        every FASTA file, prints the results in a table on CLI and writes
        a CSV file with the full prediction set.  It also logs the memory
        consumption of the run.

        Args:
            None. The method works only with the instance state.

        Returns:
            None. Just calls the `runner` and stores results in CSV format.

        Raises:
            FileNotFoundError:
                If any of the model files or the label vector file cannot be
                located on disk.
            RuntimeError:
                If, for any of the StrainFish trained models deserialization
                fails.
        """
        # Basic check
        if not os.path.exists(self.fasta_file):
            log.error(f"Path [bold cyan]{self.fasta_file}[/bold cyan] does not exist!")
            raise FileNotFoundError()

        # Determine if the input is a input FASTA or directory
        # of FASTA files.
        fa_files = []
        if os.path.isdir(self.fasta_file):
            for suffix in SFC.FASUFFIXES:
                fa_files.extend(Path(self.fasta_file).rglob(f"*{suffix.lower()}"))
                fa_files.extend(Path(self.fasta_file).rglob(f"*{suffix.upper()}"))
            if len(fa_files) == 0:
                log.error(
                    (
                        f"[bold cyan]{os.path.basename(self.fasta_file)}[/bold cyan] "
                        "is a directory and not FASTA files found that match the following "
                        f"suffixes: {SFC.FASUFFIXES}"
                    )
                )
        elif os.path.isfile(self.fasta_file):
            fa_files.append(self.fasta_file)

        # Initiate progress bars
        process = psutil.Process()
        total_system_mem = psutil.virtual_memory().total
        progress.start()
        (
            encode_status,
            chunk_status,
            max_encoded_len_status,
            padding_status,
            curr_memory_status,
            gpu_memory_status,
        ) = sfe.init_progress_bars(
            total_system_mem=total_system_mem, total=len(fa_files)
        )

        # Load the models and labels (with validate)
        # Check if user is requesting to load custom model path
        if len(Path(self.model).parts) > 1:
            # Load models
            xgb_model, rf_model, l_vectors, s_model_file, t_crps_file, nb_model = (
                SFModels.list_models(
                    get_this_model=Path(self.model).name,
                    models_dir=Path(self.model).parent,
                )
            )
        else:
            # Load models
            xgb_model, rf_model, l_vectors, s_model_file, t_crps_file, nb_model = (
                SFModels.list_models(get_this_model=self.model)
            )

        if all(
            m is None
            for m in [
                xgb_model,
                rf_model,
                l_vectors,
                s_model_file,
                t_crps_file,
                nb_model,
            ]
        ):
            log.error("Looks like models store is empty!")
            progress.stop()
            raise FileNotFoundError()

        log.info(
            (
                "[green3]Using existing XGBoost trained model[/green3] "
                f"[bold cyan]({os.path.basename(xgb_model)})[/bold cyan] "
                "[green3]for predictions[/green3]."
            )
        )
        xgt = xgb.Booster()
        xgt.load_model(fname=xgb_model)
        xgt_attrs = xgt.attributes()
        log.info("[green3]Loaded parameters from trained model[/green3].")
        SFHelpers._log_params(xgt_attrs)

        # Labels
        labels = {v: k for k, v in joblib.load(l_vectors).items()}

        # RandomForest
        log.info(
            (
                "[green3]Using existing RandomForest trained model[/green3] "
                f"[bold cyan]({os.path.basename(rf_model)})[/bold cyan] "
                "[green3]for predictions[/green3]."
            )
        )
        rf = tl.Model.deserialize(rf_model)

        # Naive Bayes
        log.info(
            (
                "[green3]Using existing Naive Bayes trained model[/green3] "
                f"[bold cyan]({os.path.basename(nb_model)})[/bold cyan] "
                "[green3]for predictions[/green3]."
            )
        )
        nbt = joblib.load(nb_model)

        # Initialize SFEncoder.
        sfe_predict = sfe(
            seq="Initializing...",
            encoder=False,
            chunk_size=int(xgt_attrs[SFC.CHKSN]),
            factor=int(xgt_attrs[SFC.FCN]),
            k=int(xgt_attrs[SFC.DKMERN]),
            n_hashes=int(xgt_attrs[SFC.NHN]),
            chunk_status=chunk_status,
            padding_status=padding_status,
            max_encoded_len_status=max_encoded_len_status,
        )

        if self.encode_method == SFC.SOMH:
            progress_root_info = (
                f", n_hashes=[bold cyan]{int(xgt_attrs[SFC.NHN])}[/bold cyan]"
            )
        else:
            progress_root_info = ""

        predictions = []
        for fa_file in fa_files:
            progress.update(
                encode_status,
                advance=1,
                info=(
                    f"[bold cyan]{os.path.basename(fa_file)}[/bold cyan]"
                    f"{progress_root_info}"
                    f", k=[bold cyan]{xgt_attrs[SFC.DKMERN]}[/bold cyan]."
                ),
            )

            predictions.append(
                SFPredictor.runner(
                    xgt=xgt,
                    rf=rf,
                    nbt=nbt,
                    s_model_file=s_model_file,
                    t_crps_file=t_crps_file,
                    sfe_predict=sfe_predict,
                    fasta_file=fa_file,
                    labels=labels,
                    encode_method=self.encode_method,
                    padding_length=xgt_attrs[SFC.PDLEN],
                    all_params=self.all_params,
                    chunk_size=xgt_attrs[SFC.CHKSN],
                    kmer_size=xgt_attrs[SFC.DKMERN],
                )
            )

            progress.update(
                curr_memory_status,
                completed=process.memory_info().rss,
                info=(
                    f"[bold cyan]{SFHelpers._human_bytes(process.memory_info().rss)}[/bold cyan]"
                    f" / [bold cyan]{SFHelpers._human_bytes(total_system_mem)}[/bold cyan]."
                ),
            )
            progress.update(
                gpu_memory_status,
                completed=GPUMemInfo.fetch().used,
                info=(
                    f"[bold cyan]{SFHelpers._human_bytes(GPUMemInfo.fetch().used)}[/bold cyan]"
                    f" / [bold cyan]{SFHelpers._human_bytes(GPUMemInfo.fetch().total)}[/bold cyan]."
                ),
            )

        all_predictions = pd.concat(predictions, ignore_index=True)

        # Create a rich table
        table = T(show_lines=False, show_edge=False)

        # Add columns to the table
        for column in all_predictions.columns:
            table.add_column(str(column), justify="center")

        # Add head rows from DataFrame data
        for _, row in all_predictions.iloc[: SFC.HROWS].iterrows():
            table.add_row(*[str(i) for i in row.values])

        num_all_predictions = len(all_predictions)

        # Add tail rows for N number of inputs
        if SFC.HROWS + SFC.TROWS < num_all_predictions:
            table.add_row(*["..." for _ in range(all_predictions.shape[1])])
            final_rows = SFC.TROWS
        else:
            final_rows = len(all_predictions) - SFC.TROWS

        for _, row in all_predictions.iloc[-final_rows:].iterrows():
            table.add_row(*[str(i) for i in row.values])

        console.print(
            "\n",
            Panel.fit(
                table,
                title=f"{SFC.PKG_NAME} Predictions",
                border_style="spring_green3",
                padding=(1, 1, 1, 1),
            ),
            "\n",
        ),

        results_file = Path(self.output, SFC.PKG_NAME + "_results.csv")
        Path(self.output).mkdir(exist_ok=True, parents=True)

        all_predictions.to_csv(f"{results_file}", index=False)
        log.info(
            (
                "[green3]Results are saved to[/green3] "
                f"[bold cyan]{os.path.basename(results_file)}[/bold cyan]."
            )
        )
        sfe.log_memory_used(
            memory_used=process.memory_info().rss,
            total_system_mem=total_system_mem,
        )
        progress.stop()
