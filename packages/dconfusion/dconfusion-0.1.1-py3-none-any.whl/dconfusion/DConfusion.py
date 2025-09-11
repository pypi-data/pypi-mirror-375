
class DConfusion:

    def __init__(self, true_positive, false_negative, false_positive, true_negative):
        self.true_positive = true_positive
        self.false_positive = false_positive
        self.true_negative = true_negative
        self.false_negative = false_negative
        self.total = true_positive + false_negative + false_positive + true_negative

    def __str__(self):
        return (
            f"Confusion Matrix:\n"
            f"              \t Predicted Positive  Predicted Negative\n"
            f"Actual Positive  {self.true_positive:^15}  {self.false_negative:^15}\n"
            f"Actual Negative  {self.false_positive:^15}  {self.true_negative:^15}"
        )

    def frequency(self):
        if self.total == 0:
            raise ZeroDivisionError("Cannot calculate frequency for an empty confusion matrix")

        tp_freq = (self.true_positive / self.total) * 100
        tn_freq = (self.true_negative / self.total) * 100
        fp_freq = (self.false_positive / self.total) * 100
        fn_freq = (self.false_negative / self.total) * 100

        return (
            f"Confusion Matrix Frequency (%):\n"
            f"              \t Predicted Positive  Predicted Negative\n"
            f"Actual Positive  {tp_freq:^15.2f}  {fn_freq:^15.2f}\n"
            f"Actual Negative  {fp_freq:^15.2f}  {tn_freq:^15.2f}"
        )

    def get_sum_of_all(self):
        return self.total

    def get_confusion_matrix(self):
        return [[self.true_positive, self.false_positive], [self.false_negative, self.true_negative]]

    def get_sum_of_errors(self):
        return self.false_positive + self.false_negative

    def get_sum_of_corrects(self):
        return self.true_positive + self.true_negative

    def get_accuracy(self):
        return (self.true_positive + self.true_negative) / self.get_sum_of_all()

    def get_error_rate(self):
        return self.get_sum_of_errors() / self.get_sum_of_all()

    def get_recall(self):
        return self.true_positive / (self.true_positive + self.false_negative)

    def get_true_positive_rate(self):
        return self.get_recall()

    def get_sensitivity(self):
        return self.get_recall()

    def get_probability_of_detection(self):
        return self.get_recall()

    def get_true_negative_rate(self):
        return self.true_negative / (self.true_negative + self.false_positive)

    def get_specificity(self):
        return self.get_true_negative_rate()

    def get_false_positive_rate(self):
        return self.false_positive / (self.false_positive + self.true_negative)

    def get_type_1_error(self):
        return self.get_false_positive_rate()

    def get_probability_of_false_alarm(self):
        return self.get_false_positive_rate()

    def get_false_negative_rate(self):
        return self.false_negative / (self.false_negative + self.true_positive)

    def get_type_2_error(self):
        return self.get_false_negative_rate()

    def get_precision(self):
        return self.true_positive / (self.true_positive + self.false_positive)

    def get_f1_score(self):
        return 2 * self.get_precision() * self.get_recall() / (self.get_precision() + self.get_recall())

    def get_f_measure(self):
        return self.get_f1_score()

    def get_balance(self):
        import math
        return 1 - (math.sqrt((0-self.get_probability_of_false_alarm())**2 + (1-self.get_probability_of_detection())**2))/(math.sqrt(2))

    def get_g_mean(self):
        return (self.get_precision() * self.get_recall()) ** 0.5

    def get_matthews_correlation_coefficient(self):
        return (self.true_positive * self.true_negative - self.false_positive * self.false_negative) / \
        (
                (self.true_positive + self.false_positive) *
                (self.true_positive + self.false_negative) *
                (self.true_negative + self.false_positive) *
                (self.true_negative + self.false_negative)
        ) ** 0.5

    def false_rate(self):
        return self.get_sum_of_errors() / self.get_sum_of_all()