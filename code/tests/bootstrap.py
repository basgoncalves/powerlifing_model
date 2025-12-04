import numpy as np
import matplotlib.pyplot as plt    
from scipy import stats

class Bootstrap:
    def __init__(self):
        self.x = np.array([1.2, 3.6, 5.0, 7.1])
        self.y = np.array([2.4, 20.0, 15.0, 14.2])
        
    def calculate_statistics(self):
        self.mean_x = np.mean(self.x)
        self.mean_y = np.mean(self.y)
        self.std_x = np.std(self.x)
        self.std_y = np.std(self.y)
        print(f"Mean of x: {self.mean_x}, Std of x: {self.std_x}")
        print(f"Mean of y: {self.mean_y}, Std of y: {self.std_y}")
        
    def t_test(self):
        t_stat, p_value = stats.ttest_ind(self.x, self.y)
        print(f"T-statistic: {t_stat}, P-value: {p_value}")
        
    def plot_boxplot(self):
        data = [self.x, self.y]
        plt.boxplot(data, labels=["x", "y"])
        plt.title("Boxplot of x and y")
        
        
    def bootstrap(self, n_iterations=1000):
        combined = np.concatenate([self.x, self.y])
        n_x = len(self.x)
        n_y = len(self.y)
        diff_means = []
        
        for _ in range(n_iterations):
            np.random.shuffle(combined)
            sample_x = combined[:n_x]
            sample_y = combined[n_x:n_x+n_y]    
            diff_means.append(np.mean(sample_x) - np.mean(sample_y))
        
        self.bootstrap_diff_means = np.array(diff_means)
        self.bootstrap_x = np.mean(self.bootstrap_diff_means)
        self.bootstrap_y = np.std(self.bootstrap_diff_means)
        print(f"Bootstrap mean difference: {np.mean(self.bootstrap_diff_means)}")
        
    def show(self):
        plt.show()
        
if __name__ == "__main__":
    analysis = Bootstrap()
    analysis.plot_boxplot()
    analysis.calculate_statistics()
    analysis.t_test()
    analysis.bootstrap(n_iterations=1000)
    print(f"Bootstrap mean difference: {analysis.bootstrap_x}")
    print(f"Bootstrap std difference: {analysis.bootstrap_y}")


    analysis.show()    
