# Leakage Findings

The leakage experiment compared an honest feature set against a feature set containing harvest-time information.

The honest model achieved ROC-AUC of approximately 0.575.

The leaky model achieved ROC-AUC of 1.000.

The uyer_grade column directly determines met_target in the available data:
- Grade A corresponds to the positive target.
- Grades B and C correspond to the negative target.

Other harvest-time variables, including yield and post-harvest loss, are also unavailable at prediction time.

Therefore harvest-time variables must not be used as predictors for the pre-harvest target.
