from typing import Optional, Tuple, List
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.base import BaseEstimator
from generalize.model.transformers import PCAByExplainedVariance
from generalize.model.pipeline.pipeline_designer import PipelineDesigner


def prepare_transformers_fn(
    pca_target_variance: List[float],
    min_var_thresh: List[float] = [0.0],
    scale_rows: List[str] = ["mean", "std"],
    post_scale_feature_indices: Optional[List[int]] = None,
    standardize: bool = True,
    add_dim_transformer_wrappers: bool = False,
):
    def transformers_fn(
        model_dict: dict,
    ) -> Tuple[List[Tuple[str, BaseEstimator]], dict]:
        designer = PipelineDesigner()

        # Add minimum variance feature selector
        if min_var_thresh:
            if len(min_var_thresh) != 1:
                if add_dim_transformer_wrappers:
                    model_dict["grid"]["near_zero_variance__kwargs"] = [
                        {"threshold": vt} for vt in min_var_thresh
                    ]
                else:
                    model_dict["grid"]["near_zero_variance__threshold"] = min_var_thresh
            kwargs = {}
            if len(min_var_thresh) == 1:
                kwargs["threshold"] = min_var_thresh[0]
            designer.add_step(
                name="near_zero_variance",
                transformer=VarianceThreshold,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
                kwargs=kwargs,
            )
            del kwargs

        # Add row-scaling
        # NOTE: Must come after the variance-based selection steps
        if scale_rows:
            if len(scale_rows) != 2:
                raise ValueError(
                    "When `--scale_rows` is specified, it must have length 2."
                )
            kwargs = {}
            kwargs["center"], kwargs["scale"] = [
                metric if metric != "none" else None for metric in scale_rows
            ]
            designer.add_step(
                name="row_standardize",
                transformer="scale_rows",
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
                kwargs=kwargs,
            )
            del kwargs

        # NOTE: Cannot have selection based on min_var_thresh or max_corr_thresh
        # prior to this
        if post_scale_feature_indices is not None:
            if min_var_thresh:
                raise ValueError(
                    "Cannot perform `post_scale_feature_indices` selection when "
                    "`--min_var_thresh` is specified."
                )
            designer.add_step(
                name="select_features_post_scaling",
                transformer="feature_selector",
                add_dim_transformer_wrapper=True,
                kwargs={"feature_indices": post_scale_feature_indices},
            )

        if pca_target_variance:
            if len(pca_target_variance) != 1:
                if add_dim_transformer_wrappers:
                    model_dict["grid"]["pca__kwargs"] = [
                        {"target_variance": tv} for tv in pca_target_variance
                    ]
                else:
                    model_dict["grid"]["pca__target_variance"] = pca_target_variance
            kwargs = {}
            if len(pca_target_variance) == 1:
                kwargs["target_variance"] = pca_target_variance[0]
            designer.add_step(
                name="pre_pca_standardize",
                transformer=StandardScaler,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
            )
            designer.add_step(
                name="pca",
                transformer=PCAByExplainedVariance,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
                kwargs=kwargs,
            )
            del kwargs

        # Add standard scaler
        if standardize:
            designer.add_step(
                name="standardize",
                transformer=StandardScaler,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
            )

        # If no non-split/collect steps were added
        if not designer.n_transformers:
            designer.add_step(
                name="identity",
                transformer="identity",
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
            )

        return designer.build(), model_dict

    return transformers_fn


def prepare_benchmark_transformers_fn(
    feature_type: str,
    pca_target_variance: List[float],
    min_var_thresh: List[float] = [0.0],
    standardize: bool = True,
    add_dim_transformer_wrappers: bool = False,
):
    def transformers_fn(
        model_dict: dict,
    ) -> Tuple[List[Tuple[str, BaseEstimator]], dict]:
        designer = PipelineDesigner()

        if feature_type in ["bin_depths"]:
            # Divide by row-mean (1-centered but keep proportional variance)
            designer.add_step(
                name="row_scale",
                transformer="scale_rows",
                add_dim_transformer_wrapper=True,
                kwargs={
                    "center": None,
                    "scale": "mean",
                },
            )

        if feature_type in ["lengths"]:
            # Divide by row-sum (--> distribution)
            designer.add_step(
                name="row_scale",
                transformer="scale_rows",
                add_dim_transformer_wrapper=True,
                kwargs={
                    "center": None,
                    "scale": "sum",
                },
            )

        # Add minimum variance feature selector
        if min_var_thresh:
            if len(min_var_thresh) != 1:
                if add_dim_transformer_wrappers:
                    model_dict["grid"]["near_zero_variance__kwargs"] = [
                        {"threshold": vt} for vt in min_var_thresh
                    ]
                else:
                    model_dict["grid"]["near_zero_variance__threshold"] = min_var_thresh
            kwargs = {}
            if len(min_var_thresh) == 1:
                kwargs["threshold"] = min_var_thresh[0]
            designer.add_step(
                name="near_zero_variance",
                transformer=VarianceThreshold,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
                kwargs=kwargs,
            )
            del kwargs

        if pca_target_variance:
            if len(pca_target_variance) != 1:
                if add_dim_transformer_wrappers:
                    model_dict["grid"]["pca__kwargs"] = [
                        {"target_variance": tv} for tv in pca_target_variance
                    ]
                else:
                    model_dict["grid"]["pca__target_variance"] = pca_target_variance
            kwargs = {}
            if len(pca_target_variance) == 1:
                kwargs["target_variance"] = pca_target_variance[0]
            designer.add_step(
                name="pre_pca_standardize",
                transformer=StandardScaler,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
            )
            designer.add_step(
                name="pca",
                transformer=PCAByExplainedVariance,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
                kwargs=kwargs,
            )
            del kwargs

        # Add standard scaler
        if standardize:
            designer.add_step(
                name="standardize",
                transformer=StandardScaler,
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
            )

        # If no non-split/collect steps were added
        if not designer.n_transformers:
            designer.add_step(
                name="identity",
                transformer="identity",
                add_dim_transformer_wrapper=add_dim_transformer_wrappers,
            )

        return designer.build(), model_dict

    return transformers_fn
