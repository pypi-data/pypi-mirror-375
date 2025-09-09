# %%
# type: ignore
%load_ext autoreload
%autoreload 2

from datadec import DataDecide
import datadec.constants as consts

# %%
data_dir = "../outputs/example_data"
dd = DataDecide(
    data_dir=data_dir,
    verbose=True,
)
print(f">> Available dataframes: {dd.paths.available_dataframes}")
print(f">> Full Eval DF:")
dd.load_dataframe("full_eval").head(20)

# %%
print(">> Indexing Example, params=10M, data=C4, seed=0")
dd.easy_index_df(
    params="10M", data="C4", seed=0, keep_cols=consts.PREFIX_COLS_WITH_LR + ['pile-valppl', 'mmlu_average_correct_prob']
)

# %%
