import pandas as pd
from sklearn.cluster import DBSCAN
import argparse
import numpy as np


def get_min_max_arrival_ts(group):
    ret = {}
    ret["max_arrival_ts"] = group["arrival_ts"].max()
    ret["min_arrival_ts"] = group["arrival_ts"].min()
    return pd.Series(ret)


def train_DBSCAN(arrivals_ts, eps, min_samples=20):
    """
    Train the DBScan algorithm.
    """
    def get_cluster_mean(group):
        cluster_center = group["arrival_ts"].mean()
        return pd.Series({"cluster_center": cluster_center})

    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(
        np.array(arrivals_ts).reshape(-1, 1))
    cluster_labels = list(clustering.labels_)
    result = pd.DataFrame(
        {"arrival_ts": arrivals_ts, "cluster_labels": cluster_labels})
    result_clustering = result.groupby("cluster_labels").apply(
        get_cluster_mean)
    result_clustering.reset_index(inplace=True)
    return result_clustering


def generate_result_csv(ground_truth, predictions, stop_name):
    """
    Generate the results and save to CSV for evaluation.
    """
    result = pd.DataFrame({"arrival_ts": list(ground_truth),
                           "predicted_arrival": list(predictions)})
    result["diff"] = result["arrival_ts"] - result["predicted_arrival"]
    result.to_csv(f"predicted_arrivals_{stop_name}.csv", index=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--transition_events", type=str,
                        default="train_detection_challenge/transition_events.csv",
                        help="path to the transition events file")
    parser.add_argument(
        "--arrival_times", type=str,
        default="train_detection_challenge/train_arrival_times.csv",
        help="path to the arrival times file")

    args = parser.parse_args()

    # read the training data
    train_data = pd.read_csv(args.transition_events)
    train_data.sort_values(["to_stop", "arrival_ts"], inplace=True)
    train_data["travel_time"] = train_data["arrival_ts"]-train_data["departure_ts"]
    print("print shape of arrivals data", train_data.shape)

    # read the ground truth of arrivals
    ground_truth = pd.read_csv(args.arrival_times)
    ground_truth.sort_values(["stop", "arrival_ts"], inplace=True)
    print("shape of ground truth", ground_truth.shape)

    stats_ground = ground_truth.groupby("stop").apply(get_min_max_arrival_ts)
    stats_ground.reset_index(inplace=True)

    # filter outliers

    train_data.drop(train_data[((train_data.from_stop == "A") & (
        train_data.to_stop == "B")) & ((train_data.travel_time > 176))].index,
        inplace=True)

    train_data.drop(train_data[((train_data.from_stop == "B") & (
        train_data.to_stop == "C")) & ((train_data.travel_time > 169) |
                                       (train_data.travel_time <= 4))].index,
        inplace=True)

    train_data.drop(train_data[((train_data.from_stop == "A") & (
        train_data.to_stop == "C")) & ((train_data.travel_time > 420))].index,
        inplace=True)

    # remove departure_ts outliers.

    train_data.drop(train_data[(train_data.to_stop == "B") &
                               (train_data.departure_ts >
                                stats_ground.iloc[0, 1])].index, inplace=True)

    train_data.drop(train_data[(train_data.to_stop == "C") &
                               (train_data.departure_ts >
                                stats_ground.iloc[1, 1])].index, inplace=True)

    train_data = train_data[train_data.departure_ts > 0]
    print("Shape of arrivals data after filtering outliers", train_data.shape)

    arrivals_B = train_data[train_data.to_stop == "B"].arrival_ts
    arrivals_C = train_data[train_data.to_stop == "C"].arrival_ts

    result_clustering_stop_C = train_DBSCAN(arrivals_C, eps=16, min_samples=23)
    generate_result_csv(ground_truth[ground_truth.stop == "C"]["arrival_ts"],
                        result_clustering_stop_C.iloc[2:, 1], "C")
    print("Finished generating report for stop C")

    result_clustering_stop_B = train_DBSCAN(arrivals_B, eps=30)
    generate_result_csv(ground_truth[ground_truth.stop == "B"]["arrival_ts"],
                        result_clustering_stop_B.iloc[1:, 1], "B")
    print("Finished generating report for stop B")
