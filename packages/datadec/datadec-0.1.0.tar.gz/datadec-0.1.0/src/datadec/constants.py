import re
from itertools import product
from typing import Any, Dict, List, Set

MODEL_DETAILS_DF_NAME = "model_details"
DATASET_DETAILS_DF_NAME = "dataset_details"


# --------- Model Architecture Details ---------

# This is the list of sizes we're using
ALL_MODEL_SIZE_STRS: List[str] = [
    "4M",
    "6M",
    "8M",
    "10M",
    "14M",
    "16M",
    "20M",
    "60M",
    "90M",
    "150M",
    "300M",
    "530M",
    "750M",
    "1B",
]

# Below here is mostly taken directly from the OLMO Ladder Code
MAX_SEQ_LEN: int = 2_048
TOKEN_LEN_XC_MULTIPLIER: int = 20
MODEL_SIZE_NORM_VALUE: int = 108_000_000
LR_EXPONENT: float = -1 / 3
LR_MAX_BASE: float = 0.0047
LR_FINAL_RATIO: float = 0.01
BS_COEFFICIENT: int = 160
BS_EXPONENT: float = 2 / 3
GPUS_PER_NODE: int = 8
MICROBATCH_SIZE: int = 4

MODEL_SHAPES: Dict[str, Dict[str, int]] = {
    "4M": {"d_model": 64, "n_heads": 8, "n_layers": 8, "mlp_ratio": 8},
    "6M": {"d_model": 96, "n_heads": 8, "n_layers": 8, "mlp_ratio": 8},
    "8M": {"d_model": 128, "n_heads": 8, "n_layers": 8, "mlp_ratio": 8},
    "10M": {"d_model": 144, "n_heads": 8, "n_layers": 8, "mlp_ratio": 8},
    "14M": {"d_model": 192, "n_heads": 8, "n_layers": 8, "mlp_ratio": 8},
    "16M": {"d_model": 208, "n_heads": 8, "n_layers": 8, "mlp_ratio": 8},
    "20M": {"d_model": 192, "n_heads": 8, "n_layers": 16, "mlp_ratio": 8},
    "60M": {"d_model": 384, "n_heads": 12, "n_layers": 16, "mlp_ratio": 8},
    "90M": {"d_model": 528, "n_heads": 12, "n_layers": 16, "mlp_ratio": 8},
    "150M": {"d_model": 768, "n_heads": 12, "n_layers": 12, "mlp_ratio": 8},
    "300M": {"d_model": 1024, "n_heads": 16, "n_layers": 16, "mlp_ratio": 8},
    "530M": {"d_model": 1344, "n_heads": 16, "n_layers": 16, "mlp_ratio": 8},
    "750M": {"d_model": 1536, "n_heads": 16, "n_layers": 16, "mlp_ratio": 8},
    "1B": {"d_model": 2048, "n_heads": 16, "n_layers": 16, "mlp_ratio": 8},
}

HARDCODED_SIZE_MAPPING: Dict[str, int] = {
    "4M": 3_744_832,
    "6M": 6_010_464,
    "8M": 8_538_240,
    "10M": 9_900_432,
    "14M": 14_380_224,
    "16M": 16_004_560,
    "20M": 19_101_888,
    "60M": 57_078_144,
    "90M": 97_946_640,
    "150M": 150_000_000,
    "300M": 300_000_000,
    "530M": 530_000_000,
    "750M": 750_000_000,
    "1B": 1_000_000_000,
}

# Selected by me based on a combo of the max consistent step in the dfs
# and the hpms listed in the appendix of the paper
MAX_STEP_TO_USE: Dict[str, int] = {
    "1B": 67500,
    "750M": 62500,
    "530M": 51250,
    "300M": 45000,
    "150M": 37500,
    "90M": 29901,
    "60M": 29042,
    "20M": 14584,
    "16M": 24432,
    "14M": 21953,
    "10M": 15117,
    "8M": 13039,
    "6M": 9182,
    "4M": 5725,
}


MODEL_CONFIG_BASE: Dict[str, Any] = {
    "default_seed": 6198,
    "length_str": "5xC",
    "lr_warmup_start": 0.0,
    "d_model": 768,
    "n_heads": 12,
    "n_layers": 12,
    "mlp_ratio": 8,
    "weight_tying": False,
    "alibi": False,
    "rope": True,
    "flash_attention": True,
    "attention_dropout": 0.0,
    "attention_layer_norm": False,
    "include_bias": False,
    "layer_norm_type": "rms",
    "layer_norm_with_affine": True,
    "layer_norm_eps": 1e-6,
    "bias_for_layer_norm": False,
    "attention_layer_norm_with_affine": False,
    "activation_type": "swiglu",
    "residual_dropout": 0.0,
    "embedding_dropout": 0.0,
    "max_sequence_length": 2048,
    "vocab_size": 50280,
    "embedding_size": 50304,
    "eos_token_id": 50279,
    "pad_token_id": 1,
    "init_device": "cuda",
    "init_fn": "normal",
    "init_std": 0.02,
    "init_cutoff_factor": 3,
}

# Used to parse any numeric strings
NUMBER_UNIT_RE = re.compile(r"^([0-9]+)([a-zA-Z]+)$")

# --------- Huggingface Dataset Info ---------
HF_DATASET_NAMES: Dict[str, str] = {
    "ppl_eval_ds": "allenai/DataDecide-ppl-results",
    "dwn_eval_ds": "allenai/DataDecide-eval-results",
    "dwn_instance_ds": "allenai/DataDecide-eval-instances",
}
HF_DATASET_SPLIT: str = "train"

# --------- Data Recipe Consts ---------

DATA_RECIPE_FAMILIES: Dict[str, List[str]] = {
    "dolma17": [
        "Dolma1.7",
        "Dolma1.7 (no code)",
        "Dolma1.7 (no math, code)",
        "Dolma1.7 (no Reddit)",
        "Dolma1.7 (no Flan)",
    ],
    "dolma16pp": ["Dolma1.6++"],
    "c4": ["C4"],
    "fineweb": ["FineWeb-Pro", "FineWeb-Edu"],
    "falcon": ["Falcon"],
    "falcon_cc": [
        "Falcon+CC",
        "Falcon+CC (QC 10%)",
        "Falcon+CC (QC 20%)",
        "Falcon+CC (QC Orig 10%)",
        "Falcon+CC (QC Tulu 10%)",
    ],
    "dclm": [
        "DCLM-Baseline",
        "DCLM-Baseline (QC 10%)",
        "DCLM-Baseline (QC 20%)",
        "DCLM-Baseline (QC 7%, FW3)",
        "DCLM-Baseline (QC 7%, FW2)",
        "DCLM-Baseline (QC FW 3%)",
        "DCLM-Baseline (QC FW 10%)",
    ],
    "mix": [
        "DCLM-Baseline 25% / Dolma 75%",
        "DCLM-Baseline 50% / Dolma 50%",
        "DCLM-Baseline 75% / Dolma 25%",
    ],
}

ALL_DATA_NAMES: List[str] = [
    name for family in DATA_RECIPE_FAMILIES.values() for name in family
]

# --------- Seed and Metric Consts ---------

SEED_MAP: Dict[str, int] = {
    "default": 0,
    "small aux 2": 1,
    "small aux 3": 2,
    "large aux 2": 3,
    "large aux 3": 4,
}

PPL_NAME_MAP: Dict[str, str] = {
    "eval/wikitext_103-validation/Perplexity": "wikitext_103-valppl",
    "eval/pile-validation/Perplexity": "pile-valppl",
    "eval/c4_en-validation/Perplexity": "c4_en-valppl",
    "eval/m2d2_s2orc-validation/Perplexity": "m2d2_s2orc-valppl",
    "eval/ice-validation/Perplexity": "ice-valppl",
    "eval/dolma_wiki-validation/Perplexity": "dolma_wiki-valppl",
    "eval/dolma_stack-validation/Perplexity": "dolma_stack-valppl",
    "eval/dolma_reddit-validation/Perplexity": "dolma_reddit-valppl",
    "eval/dolma_pes2o-validation/Perplexity": "dolma_pes2o-valppl",
    "eval/dolma_common-crawl-validation/Perplexity": "dolma_common-crawl-valppl",
    "eval/dolma_books-validation/Perplexity": "dolma_books-valppl",
}
PPL_TYPES: List[str] = list(PPL_NAME_MAP.values())


MMLU_TASKS: List[str] = [
    "mmlu_abstract_algebra",
    "mmlu_anatomy",
    "mmlu_astronomy",
    "mmlu_average",
    "mmlu_business_ethics",
    "mmlu_clinical_knowledge",
    "mmlu_college_biology",
    "mmlu_college_chemistry",
    "mmlu_college_computer_science",
    "mmlu_college_mathematics",
    "mmlu_college_medicine",
    "mmlu_college_physics",
    "mmlu_computer_security",
    "mmlu_conceptual_physics",
    "mmlu_econometrics",
    "mmlu_electrical_engineering",
    "mmlu_elementary_mathematics",
    "mmlu_formal_logic",
    "mmlu_global_facts",
    "mmlu_high_school_biology",
    "mmlu_high_school_chemistry",
    "mmlu_high_school_computer_science",
    "mmlu_high_school_european_history",
    "mmlu_high_school_geography",
    "mmlu_high_school_government_and_politics",
    "mmlu_high_school_macroeconomics",
    "mmlu_high_school_mathematics",
    "mmlu_high_school_microeconomics",
    "mmlu_high_school_physics",
    "mmlu_high_school_psychology",
    "mmlu_high_school_statistics",
    "mmlu_high_school_us_history",
    "mmlu_high_school_world_history",
    "mmlu_human_aging",
    "mmlu_human_sexuality",
    "mmlu_international_law",
    "mmlu_jurisprudence",
    "mmlu_logical_fallacies",
    "mmlu_machine_learning",
    "mmlu_management",
    "mmlu_marketing",
    "mmlu_medical_genetics",
    "mmlu_miscellaneous",
    "mmlu_moral_disputes",
    "mmlu_moral_scenarios",
    "mmlu_nutrition",
    "mmlu_philosophy",
    "mmlu_prehistory",
    "mmlu_professional_accounting",
    "mmlu_professional_law",
    "mmlu_professional_medicine",
    "mmlu_professional_psychology",
    "mmlu_public_relations",
    "mmlu_security_studies",
    "mmlu_sociology",
    "mmlu_us_foreign_policy",
    "mmlu_virology",
    "mmlu_world_religions",
]

OLMES_TASKS: List[str] = [
    "mmlu_average",
    "arc_challenge",
    "arc_easy",
    "boolq",
    "csqa",
    "hellaswag",
    "openbookqa",
    "piqa",
    "socialiqa",
    "winogrande",
]

METRIC_NAMES: List[str] = [
    "correct_choice",
    "acc_raw",
    "acc_per_token",
    "acc_per_char",
    "acc_per_byte",
    "acc_uncond",
    "no_answer",
    "sum_logits_corr",
    "logits_per_token_corr",
    "logits_per_char_corr",
    "bits_per_byte_corr",
    "correct_prob",
    "correct_prob_per_token",
    "correct_prob_per_char",
    "margin",
    "margin_per_token",
    "margin_per_char",
    "total_prob",
    "total_prob_per_token",
    "total_prob_per_char",
    "uncond_correct_prob",
    "uncond_correct_prob_per_token",
    "uncond_correct_prob_per_char",
    "uncond_total_prob",
    "norm_correct_prob",
    "norm_correct_prob_per_token",
    "norm_correct_prob_per_char",
    "primary_metric",
]

# --------- Proj Specific Consts ---------

# Mainly for parsing into a standard df format
DROP_METRICS: List[str] = [
    "predicted_index_raw",
    "predicted_index_per_token",
    "predicted_index_per_char",
    "predicted_index_per_byte",
    "predicted_index_uncond",
    "logits_per_byte_corr",
]

# All known metrics (PPL + cross product of OLMES tasks and metric types)
ALL_KNOWN_METRICS: Set[str] = set(PPL_TYPES) | {
    f"{task}_{metric_type}" for task, metric_type in product(OLMES_TASKS, METRIC_NAMES)
}

PARAM_NUMERIC_COL = "params_numeric"
KEY_COLS: List[str] = ["params", "data", "seed", "step"]
STEP_TOK_COMP_COLS: List[str] = ["params", "step", "tokens", "compute"]
DWN_DROP_COLS: List[str] = ["chinchilla", "tokens", "compute"]
PPL_DROP_COLS: List[str] = ["__index_level_0__"]
FINAL_PREFIX_COLS: List[str] = KEY_COLS + [
    "tokens",
    "compute",
    "total_steps",
    "warmup_steps",
    "lr_max",
    "batch_size",
]

LR_INPUT_COLS: List[str] = [
    "step",
    "lr_warmup_start",
    "lr_max",
    "lr_final",
    "warmup_steps",
    "lr_decay_steps",
]
LR_OUTPUT_COLS: List[str] = ["lr_at_step", "cumulative_lr"]
PREFIX_COLS_WITH_LR: List[str] = FINAL_PREFIX_COLS + LR_OUTPUT_COLS


# --------- Recipe Collections for Plotting and Analysis ---------

BASE_RECIPES: List[str] = [
    "C4",
    "Falcon",
    "Falcon+CC",
    "Dolma1.6++",
    "Dolma1.7",
    "FineWeb-Pro",
    "FineWeb-Edu",
    "DCLM-Baseline",
]

BASE_AND_QC: List[str] = [
    "C4",
    "Falcon",
    "Falcon+CC",
    "Falcon+CC (QC 10%)",
    "Falcon+CC (QC 20%)",
    "Falcon+CC (QC Orig 10%)",
    "Falcon+CC (QC Tulu 10%)",
    "Dolma1.6++",
    "Dolma1.7",
    "DCLM-Baseline 25% / Dolma 75%",
    "DCLM-Baseline 50% / Dolma 50%",
    "DCLM-Baseline 75% / Dolma 25%",
    "FineWeb-Pro",
    "FineWeb-Edu",
    "DCLM-Baseline",
    "DCLM-Baseline (QC 10%)",
    "DCLM-Baseline (QC 20%)",
    "DCLM-Baseline (QC 7%, FW3)",
    "DCLM-Baseline (QC 7%, FW2)",
    "DCLM-Baseline (QC FW 3%)",
    "DCLM-Baseline (QC FW 10%)",
]

RECIPES_WITHOUT_ABLATIONS: List[str] = [
    "C4",
    "Falcon",
    "Falcon+CC",
    "Falcon+CC (QC 10%)",
    "Falcon+CC (QC 20%)",
    "Falcon+CC (QC Orig 10%)",
    "Falcon+CC (QC Tulu 10%)",
    "Dolma1.6++",
    "Dolma1.7",
    "FineWeb-Pro",
    "FineWeb-Edu",
    "DCLM-Baseline",
    "DCLM-Baseline (QC 10%)",
    "DCLM-Baseline (QC 20%)",
    "DCLM-Baseline (QC 7%, FW3)",
    "DCLM-Baseline (QC 7%, FW2)",
    "DCLM-Baseline (QC FW 3%)",
    "DCLM-Baseline (QC FW 10%)",
]

CUSTOM_RECIPE_FAMILIES: Dict[str, List[str]] = {
    "core_datasets": ["C4", "Falcon", "Dolma1.6++"],
    "dolma17_variants": [
        "Dolma1.7",
        "Dolma1.7 (no code)",
        "Dolma1.7 (no math, code)",
        "Dolma1.7 (no Reddit)",
        "Dolma1.7 (no Flan)",
    ],
    "dclm_variants": [
        "DCLM-Baseline",
        "DCLM-Baseline (QC 10%)",
        "DCLM-Baseline (QC 20%)",
        "DCLM-Baseline (QC 7%, FW3)",
        "DCLM-Baseline (QC 7%, FW2)",
        "DCLM-Baseline (QC FW 3%)",
        "DCLM-Baseline (QC FW 10%)",
    ],
    "falcon_cc_variants": [
        "Falcon+CC",
        "Falcon+CC (QC 10%)",
        "Falcon+CC (QC 20%)",
        "Falcon+CC (QC Orig 10%)",
        "Falcon+CC (QC Tulu 10%)",
    ],
    "fineweb_variants": ["FineWeb-Pro", "FineWeb-Edu"],
    "mix_with_baselines": [
        "Dolma1.7",
        "DCLM-Baseline 25% / Dolma 75%",
        "DCLM-Baseline 50% / Dolma 50%",
        "DCLM-Baseline 75% / Dolma 25%",
        "DCLM-Baseline",
    ],
}

PPL_PERFORMANCE_RECIPE_CHUNKS: Dict[str, List[str]] = {
    "best_ppl_performance": [
        "DCLM-Baseline 25% / Dolma 75%",
        "Dolma1.7 (no code)",
        "Dolma1.7",
        "Dolma1.7 (no Flan)",
        "DCLM-Baseline 50% / Dolma 50%",
        "Dolma1.6++",
        "Dolma1.7 (no Reddit)",
    ],
    "good_ppl_performance": [
        "DCLM-Baseline 75% / Dolma 25%",
        "Dolma1.7 (no math, code)",
        "Falcon+CC (QC Tulu 10%)",
        "Falcon+CC (QC 20%)",
        "Falcon+CC",
        "Falcon+CC (QC Orig 10%)",
    ],
    "medium_ppl_performance": [
        "DCLM-Baseline",
        "Falcon+CC (QC 10%)",
        "DCLM-Baseline (QC 20%)",
        "DCLM-Baseline (QC 7%, FW2)",
        "Falcon",
        "DCLM-Baseline (QC 10%)",
    ],
    "poor_ppl_performance": [
        "DCLM-Baseline (QC FW 10%)",
        "DCLM-Baseline (QC 7%, FW3)",
        "FineWeb-Edu",
        "FineWeb-Pro",
        "DCLM-Baseline (QC FW 3%)",
        "C4",
    ],
}

OLMES_PERFORMANCE_RECIPE_CHUNKS: Dict[str, List[str]] = {
    "best_olmes_performance": [
        "DCLM-Baseline (QC 7%, FW2)",
        "DCLM-Baseline (QC FW 10%)",
        "DCLM-Baseline (QC 20%)",
        "DCLM-Baseline (QC 10%)",
        "Falcon+CC (QC Orig 10%)",
        "DCLM-Baseline (QC 7%, FW3)",
        "Falcon+CC (QC 10%)",
    ],
    "good_olmes_performance": [
        "FineWeb-Pro",
        "FineWeb-Edu",
        "DCLM-Baseline",
        "Falcon+CC (QC 20%)",
        "Falcon+CC (QC Tulu 10%)",
        "DCLM-Baseline (QC FW 3%)",
    ],
    "medium_olmes_performance": [
        "DCLM-Baseline 25% / Dolma 75%",
        "DCLM-Baseline 75% / Dolma 25%",
        "C4",
        "Dolma1.7 (no code)",
        "Dolma1.7 (no Reddit)",
        "Falcon",
    ],
    "poor_olmes_performance": [
        "Dolma1.7 (no math, code)",
        "Dolma1.7 (no Flan)",
        "DCLM-Baseline 50% / Dolma 50%",
        "Falcon+CC",
        "Dolma1.7",
        "Dolma1.6++",
    ],
}
