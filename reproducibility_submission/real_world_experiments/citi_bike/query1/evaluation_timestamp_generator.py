import argparse
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import expon, norm, poisson, zipf, binom, gamma, beta, geom


class EvaluationTimestampGenerator:
    def __init__(self, summary_size: int, stream_size: int, number_of_evaluation_timestamps: int, distribution_name: str, random_seed=None) -> None:

        self.timestamp_interval = np.arange(summary_size, stream_size)
        self.number_of_evaluation_timestamps = number_of_evaluation_timestamps
        self.distributions = {
                                "uniform": self.uniform_distribution,
                                "exponential": self.exponential_distribution,
                                "normal": self.normal_distribution,
                                "poisson": self.poisson_distribution,
                                "zipf": self.zipf_distribution,
                                "binomial": self.binomial_distribution,
                                "gamma": self.gamma_distribution,
                                "beta": self.beta_distribution,
                                "geometric": self.geometric_distribution
                            }
        
        self.distribution_func = self.distributions.get(distribution_name)
        self.probabilties = []

        if summary_size >= stream_size:
            print(stream_size)
            return

        if not self.distribution_func:
            raise ValueError(f"Invalid distribution name: {distribution_name}")
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        evaluation_timestamps = ""
        if distribution_name=='poisson':
            print(*sorted(list(self.generate_poisson_process(summary_size, stream_size, number_of_evaluation_timestamps))),sep=',')
        else:
            print(*sorted(list(self.get_random_user_sampled_timestamps())),sep=',')

    def uniform_distribution(self) -> None:
        n = len(self.timestamp_interval)
        probabilities = np.ones(n) / n
        return probabilities


    def exponential_distribution(self, lambda_value=.5) -> None:
        n = len(self.timestamp_interval)
        indices = np.arange(1, n + 1)
        probabilities = expon.pdf(indices, scale=1/lambda_value)
        probabilities /= probabilities.sum()
        return probabilities


    def normal_distribution(self, mean=None, std_dev=None) -> None:
        n = len(self.timestamp_interval)
        indices = np.arange(1, n + 1)
        mean = mean if mean else n / 2
        std_dev = std_dev if std_dev else n / 4
        probabilities = norm.pdf(indices, mean, std_dev)
        probabilities /= probabilities.sum()
        return probabilities


    def poisson_distribution(self, lambda_value=3) -> None:
        n = len(self.timestamp_interval)
        indices = np.arange(1, n + 1)
        probabilities = poisson.pmf(indices, lambda_value)
        probabilities /= probabilities.sum()
        return probabilities


    def zipf_distribution(self, s=2) -> None:
        n = len(self.timestamp_interval)
        indices = np.arange(1, n + 1)
        probabilities = zipf.pmf(indices, s)
        probabilities /= probabilities.sum()
        return probabilities


    def binomial_distribution(self, n_trials=10, prob_success=0.5) -> None:
        n = len(self.timestamp_interval)
        indices = np.arange(1, n + 1)
        probabilities = binom.pmf(indices, n_trials, prob_success)
        probabilities /= probabilities.sum()
        return probabilities


    def gamma_distribution(self, shape=2, scale=1) -> None:
        n = len(self.timestamp_interval)
        indices = np.arange(1, n + 1)
        probabilities = gamma.pdf(indices, a=shape, scale=scale)
        probabilities /= probabilities.sum()
        return probabilities


    def beta_distribution(self, alpha_shape=2, beta_shape=2) -> None:
        n = len(self.timestamp_interval)
        indices = np.linspace(0, 1, n)
        probabilities = beta.pdf(indices, alpha_shape, beta_shape)
        probabilities /= probabilities.sum()
        return probabilities


    def geometric_distribution(self, prob_success=0.5) -> None:
        n = len(self.timestamp_interval)
        indices = np.arange(1, n + 1)
        probabilities = geom.pmf(indices, prob_success)
        probabilities /= probabilities.sum()
        return probabilities


    def generate_poisson_process(self, summary_size, stream_size, number_of_evaluation_timestamps):
        lam_low, lam_high = 1e-5, 10 
        max_iterations = 1000 
        
        for _ in range(max_iterations):
            lam = (lam_low + lam_high) / 2
            timestamps = [summary_size]
            current_time = summary_size

            while current_time < stream_size:
                inter_event_time = np.random.exponential(1/lam)
                current_time += inter_event_time
                if current_time < stream_size:
                    timestamps.append(int(current_time))

            if abs(len(timestamps) - (number_of_evaluation_timestamps + 1)) <= 1: 
                return timestamps[1:]
            elif len(timestamps) < number_of_evaluation_timestamps + 1:
                lam_low = lam
            else:
                lam_high = lam

        print(f"Couldn't find a suitable lambda for max_timestamp={stream_size}, required_timestamps={number_of_evaluation_timestamps}, and summary_size={summary_size} after several tries.")
        return None, None

    def get_random_user_sampled_timestamps(self, distribution_func=None, **kwargs):
        distribution_func = distribution_func or self.distribution_func
        self.probabilities = distribution_func(**kwargs)

        if not distribution_func or not self.probabilities.any():
            raise ValueError(f"Invalid distribution name")
        
        sampled_timestamps = np.random.choice(self.timestamp_interval, size=self.number_of_evaluation_timestamps, replace=False, p=self.probabilities)
        #self.plot_timestamp_probability_distribution()
        return set(sampled_timestamps)


def main():
    parser = argparse.ArgumentParser(description='Generate an event stream.')
    parser.add_argument('--summary_size', default=None, type=int, help='Query to define event type universe.')
    parser.add_argument('--stream_size', default=None, type=int, help='Set the stream size.')
    parser.add_argument('--number_of_evaluation_timestamps', default=1, type=int, help='Number of evaluations over time.')
    parser.add_argument('--distribution_name', default=None, type=str, help='Name of the distribution to draw evaluation timestamps from.')
    parser.add_argument('--random_seed', default=None, type=int, help='Random seed')
    args = parser.parse_args()

    EvaluationTimestampGenerator(args.summary_size, args.stream_size, args.number_of_evaluation_timestamps, args.distribution_name, args.random_seed)

if __name__ == "__main__":
    main()
