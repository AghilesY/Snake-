import matplotlib.pyplot as plt
from IPython import display
import os

plt.ion()

def plot(scores, mean_scores, mean_healthy_seed, mean_drug_seed, save_path = None, filename = None):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.plot(mean_healthy_seed)
    plt.plot(mean_drug_seed)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], "S : " + str(mean_scores[-1]))
    plt.text(len(mean_healthy_seed)-1, mean_healthy_seed[-1], "H : " + str(mean_healthy_seed[-1]))
    plt.text(len(mean_drug_seed)-1, mean_drug_seed[-1], "D : " + str(mean_drug_seed[-1]))
    plt.show(block=False)
    plt.pause(.1)

    if save_path != None:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        plt.savefig(save_path + filename) 