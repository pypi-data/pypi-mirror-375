import matplotlib.pyplot as plt


class VisualizeMixin:
    def plot_training_metrics(self, figsize=(16, 4)):
        """plots the loss and validation accuracy during training for a model"""
        if self.training_metrics:
            fig = plt.figure(figsize=figsize)
            num_iterations = len(self.training_metrics["loss"])
            plt.plot(self.training_metrics["accuracy"], label="training")
            plt.plot(self.training_metrics["val_accuracy"], label="validation")
            plt.xlabel("epochs")
            plt.ylabel("Accuracy")
            plt.xlim(0, num_iterations)
            plt.ylim(0, 1)
            plt.legend(loc="best")
            plt.show()
            fig = plt.figure(figsize=figsize)
            num_iterations = len(self.training_metrics["loss"])
            plt.plot(self.training_metrics["loss"], label="training")
            plt.plot(self.training_metrics["val_loss"], label="validation")
            plt.xlabel("epochs")
            plt.ylabel("Loss")
            plt.xlim(0, num_iterations)
            plt.legend(loc="best")
            plt.show()
        else:
            print("No training metrics for this model")
