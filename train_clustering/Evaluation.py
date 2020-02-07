import pandas as pd
import numpy as np


def metrics(y_true, y_pred):
    """
    I asess the accuarcy of the model based on the 4 metrics below, MAPE, RMSE,
    Mean absolute error and Mean bias
    """
    ape = np.abs(y_true-y_pred)/y_true
    ape = ape[ape < np.percentile(ape, 99)]
    print("MAPE", ape.mean())

    sq_error = (y_true-y_pred) ** 2
    sq_error = sq_error[sq_error < np.percentile(sq_error, 99)]
    print("RMSE:", np.sqrt(sq_error.mean()))

    abs_error = abs(y_true-y_pred)
    abs_error = abs_error[abs_error <
                          np.percentile(abs_error, 99)]
    print("Mean absolute error:", abs_error.mean())

    # bias
    bias = y_true-y_pred
    bias = bias[bias < np.percentile(bias, 99)]
    print("Mean Bias", bias.mean())


result_B = pd.read_csv("predicted_arrivals_B.csv")
result_C = pd.read_csv("predicted_arrivals_C.csv")

print("================= Metrics for stop B =================")
metrics(result_B["arrival_ts"], result_B["predicted_arrival"])

result_B = result_B.iloc[result_B['diff'].abs().argsort()]
print("\nTop 10 worst predictions")
print(result_B.tail(10))


print("\n================= Metrics for stop C =================")
metrics(result_C["arrival_ts"], result_C["predicted_arrival"])

result_C = result_C.iloc[result_C['diff'].abs().argsort()]
print("\nTop 10 worst predictions")
print(result_C.tail(10))
