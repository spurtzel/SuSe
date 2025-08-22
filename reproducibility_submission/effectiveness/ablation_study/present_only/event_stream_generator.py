import argparse
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.stats import expon, norm, poisson, zipf, binom, gamma, beta, geom


class EventStreamGenerator:
    def __init__(self, query: str, distribution_name: str, produce_stream: bool, produce_alphabet_probs: bool, stream_size: int,  random_seed: int) -> None:
        self.event_type_universe = sorted(list(set(re.sub(r'[^a-zA-Z0-9]', '', query))))

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

        if not self.distribution_func:
            raise ValueError(f"Invalid distribution name: {distribution_name}")
        
        if random_seed is not None:
            np.random.seed(random_seed)

        if produce_alphabet_probs:
            self.get_probabilities()

        if produce_stream:
            self.generate_stream(stream_size=stream_size)
        
        
    def uniform_distribution(self) -> None:
        n = len(self.event_type_universe)
        probabilities = np.ones(n) / n
        return probabilities


    def exponential_distribution(self, lambda_value=.5) -> None:
        n = len(self.event_type_universe)
        indices = np.arange(1, n + 1)
        probabilities = expon.pdf(indices, scale=1/lambda_value)
        probabilities /= probabilities.sum()
        return probabilities


    def normal_distribution(self, mean=None, std_dev=None) -> None:
        n = len(self.event_type_universe)
        indices = np.arange(1, n + 1)
        mean = mean if mean else n / 2
        std_dev = std_dev if std_dev else n / 4
        probabilities = norm.pdf(indices, mean, std_dev)
        probabilities /= probabilities.sum()
        return probabilities


    def poisson_distribution(self, lambda_value=3) -> None:
        n = len(self.event_type_universe)
        indices = np.arange(1, n + 1)
        probabilities = poisson.pmf(indices, lambda_value)
        probabilities /= probabilities.sum()
        return probabilities


    def zipf_distribution(self, s=2) -> None:
        n = len(self.event_type_universe)
        indices = np.arange(1, n + 1)
        probabilities = zipf.pmf(indices, s)
        probabilities /= probabilities.sum()
        return probabilities


    def binomial_distribution(self, n_trials=10, prob_success=0.5) -> None:
        n = len(self.event_type_universe)
        indices = np.arange(1, n + 1)
        probabilities = binom.pmf(indices, n_trials, prob_success)
        probabilities /= probabilities.sum()
        return probabilities


    def gamma_distribution(self, shape=2, scale=1) -> None:
        n = len(self.event_type_universe)
        indices = np.arange(1, n + 1)
        probabilities = gamma.pdf(indices, a=shape, scale=scale)
        probabilities /= probabilities.sum()
        return probabilities


    def beta_distribution(self, alpha_shape=2, beta_shape=2) -> None:
        n = len(self.event_type_universe)
        indices = np.linspace(0, 1, n)
        probabilities = beta.pdf(indices, alpha_shape, beta_shape)
        probabilities /= probabilities.sum()
        return probabilities


    def geometric_distribution(self, prob_success=0.5) -> None:
        n = len(self.event_type_universe)
        indices = np.arange(1, n + 1)
        probabilities = geom.pmf(indices, prob_success)
        probabilities /= probabilities.sum()
        return probabilities


    def generate_stream(self, stream_size: int, distribution_func=None, **kwargs):
        distribution_func = distribution_func or self.distribution_func
        probabilities = distribution_func(**kwargs)
        stream = np.random.choice(self.event_type_universe, size=stream_size, p=probabilities)
        resulting_stream = ''
        for timestamp, event in enumerate(stream):
            resulting_stream += event + " " + str(timestamp) +  " "
        print(resulting_stream)

    def plot_stream_distribution(self, stream: str) -> None:
        counts = {event: stream.count(event) for event in self.event_type_universe}
        print(counts)
        plt.bar(counts.keys(), counts.values(), color='blue')
        plt.xlabel('Event Type')
        plt.ylabel('Number of Occurrences')
        plt.title('Distribution of Event Types in the Stream')
        plt.show()

    def get_probabilities(self, distribution_func=None, **kwargs) -> dict:
        distribution_func = distribution_func or self.distribution_func
        probabilities = {}
        resulting_probabilities = ''
        for idx,event_type in enumerate(self.event_type_universe):
            resulting_probabilities += event_type + " " + str(distribution_func(**kwargs)[idx]) + " "
        print(resulting_probabilities)


def main():
    parser = argparse.ArgumentParser(description='Generate an event stream.')
    parser.add_argument('--query', default=None, type=str, help='Query to define event type universe.')
    parser.add_argument('--distribution_name', default=None, type=str, help='Name of the distribution to use.')
    parser.add_argument('--produce_stream', default=False, action='store_true', help='If set, produce stream.')
    parser.add_argument('--produce_alphabet_probs', default=False, action='store_true', help='If set, produce alphabet probabilities.')
    parser.add_argument('--stream_size', default=None, type=int, help='If produce stream, set the stream size.')
    parser.add_argument('--random_seed', default=None, type=int, help='Random seed')
    args = parser.parse_args()

    EventStreamGenerator(args.query, args.distribution_name, args.produce_stream, args.produce_alphabet_probs, args.stream_size, args.random_seed)

    
if __name__ == "__main__":
    main()
