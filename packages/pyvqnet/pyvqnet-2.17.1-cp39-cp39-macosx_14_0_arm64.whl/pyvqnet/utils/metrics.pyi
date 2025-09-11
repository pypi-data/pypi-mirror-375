from _typeshed import Incomplete
from pyvqnet.tensor import tensor as tensor

def mse(y_true_Qtensor, y_pred_Qtensor):
    """Mean squared error regression loss.

    :param y_true_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Ground truth (correct) target values. a QTensor.

    :param y_pred_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Estimated target values. a QTensor.

    :return: float or ndarray of floats. Mean squared error.

    Example::

            import numpy as np
            from pyvqnet.tensor import tensor
            from pyvqnet.utils import metrics as vqnet_metrics
            from pyvqnet import _core
            _vqnet = _core.vqnet

            y_true_Qtensor = tensor.arange(1, 12)
            y_pred_Qtensor = tensor.arange(4, 15)
            result = vqnet_metrics.MSE(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 9.0

            y_true_Qtensor = tensor.arange(1, 13).reshape([3, 4])
            y_pred_Qtensor = tensor.arange(4, 16).reshape([3, 4])
            result = vqnet_metrics.MSE(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 9.0


    """
MSE = mse

def rmse(y_true_Qtensor, y_pred_Qtensor):
    """Root Mean Absolute Error.

    :param y_true_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Ground truth (correct) target values. a QTensor.

    :param y_pred_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Estimated target values. a QTensor.

    :return: float or ndarray of floats. Root Mean Absolute Error.

    Example::

            import numpy as np
            from pyvqnet.tensor import tensor
            from pyvqnet.utils import metrics as vqnet_metrics
            from pyvqnet import _core
            _vqnet = _core.vqnet

            y_true_Qtensor = tensor.arange(1, 12)
            y_pred_Qtensor = tensor.arange(4, 15)
            result = vqnet_metrics.RMSE(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 3.0

            y_true_Qtensor = tensor.arange(1, 13).reshape([3, 4])
            y_pred_Qtensor = tensor.arange(4, 16).reshape([3, 4])
            result = vqnet_metrics.RMSE(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 3.0

    """
RMSE = rmse

def mae(y_true_Qtensor, y_pred_Qtensor):
    """Mean absolute error.

    :param y_true_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Ground truth (correct) target values. a QTensor.

    :param y_pred_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Estimated target values. a QTensor.

    :return: float or ndarray of floats. Mean absolute error regression loss.

    Example::

            import numpy as np
            from pyvqnet.tensor import tensor
            from pyvqnet.utils import metrics as vqnet_metrics
            from pyvqnet import _core
            _vqnet = _core.vqnet

            y_true_Qtensor = tensor.arange(1, 12)
            y_pred_Qtensor = tensor.arange(4, 15)
            result = vqnet_metrics.MAE(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 3.0

            y_true_Qtensor = tensor.arange(1, 13).reshape([3, 4])
            y_pred_Qtensor = tensor.arange(4, 16).reshape([3, 4])
            result = vqnet_metrics.MAE(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 3.0

    """
MAE = mae

def mape(y_true_Qtensor, y_pred_Qtensor):
    """Mean Absolute Percentage Error.

        :param y_true_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
            Ground truth (correct) target values. a QTensor.

        :param y_pred_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
            Estimated target values. a QTensor.

        :return: float or ndarray of floats. Mean Absolute Percentage Error.

        Example::

                import numpy as np
                from pyvqnet.tensor import tensor
                from pyvqnet.utils import metrics as vqnet_metrics
                from pyvqnet import _core
                _vqnet = _core.vqnet

                y_true_Qtensor = tensor.arange(1, 12)
                y_pred_Qtensor = tensor.arange(4, 15)
                result = vqnet_metrics.MAPE(y_true_Qtensor, y_pred_Qtensor)
                print(result) # 0.82360286

                y_true_Qtensor = tensor.arange(1, 13).reshape([3, 4])
                y_pred_Qtensor = tensor.arange(4, 16).reshape([3, 4])
                result = vqnet_metrics.MAPE(y_true_Qtensor, y_pred_Qtensor)
                print(result) # 0.7758026

        """
MAPE = mape

def smape(y_true_Qtensor, y_pred_Qtensor):
    """Symmetric Mean Absolute Percentage Error.

        :param y_true_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
            Ground truth (correct) target values. a QTensor.

        :param y_pred_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
            Estimated target values. a QTensor.

        :return: float or ndarray of floats. Symmetric Mean Absolute Percentage Error.

        Example::

                import numpy as np
                from pyvqnet.tensor import tensor
                from pyvqnet.utils import metrics as vqnet_metrics
                from pyvqnet import _core
                _vqnet = _core.vqnet

                y_true_Qtensor = tensor.arange(1, 12)
                y_pred_Qtensor = tensor.arange(4, 15)
                result = vqnet_metrics.SMAPE(y_true_Qtensor, y_pred_Qtensor)
                print(result) # 0.5078287720680237

                y_true_Qtensor = tensor.arange(1, 13).reshape([3, 4])
                y_pred_Qtensor = tensor.arange(4, 16).reshape([3, 4])
                result = vqnet_metrics.SMAPE(y_true_Qtensor, y_pred_Qtensor)
                print(result) # 0.48402824997901917

        """
SMAPE = smape

def r_square(y_true_Qtensor, y_pred_Qtensor, sample_weight: Incomplete | None = None):
    """R^2 (coefficient of determination) regression score function.

    Best possible score is 1.0 and it can be negative (because the
    model can be arbitrarily worse). A constant model that always
    predicts the expected value of y, disregarding the input features,
    would get a R^2 score of 0.0.


    :param y_true_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Ground truth (correct) target values. a QTensor.

    :param y_pred_Qtensor: array-like of shape (n_samples,) or (n_samples, n_outputs)
        Estimated target values. a QTensor.

    :param sample_weight: array-like of shape (n_samples,), optional Sample weights.

    :return: float or ndarray of floats. R Square Coefficient of determination.

    Notes
    -----
    This is not a symmetric function.

    Unlike most other scores, R^2 score may be negative (it need not actually
    be the square of a quantity R).

    This metric is not well-defined for single samples and will return a NaN
    value if n_samples is less than two.

    Example::

            import numpy as np
            from pyvqnet.tensor import tensor
            from pyvqnet.utils import metrics as vqnet_metrics
            from pyvqnet import _core
            _vqnet = _core.vqnet

            y_true_Qtensor = tensor.arange(1, 12)
            y_pred_Qtensor = tensor.arange(4, 15)
            result = vqnet_metrics.R_Square(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 0.09999999999999998

            y_true_Qtensor = tensor.arange(1, 13).reshape([3, 4])
            y_pred_Qtensor = tensor.arange(4, 16).reshape([3, 4])
            result = vqnet_metrics.R_Square(y_true_Qtensor, y_pred_Qtensor)
            print(result) # 0.15625


    """
R_Square = r_square

def precision_recall_f1_2_score(y_true_Qtensor, y_pred_Qtensor):
    """Compute the precision, recall and f1 score of the binary classification task.

    :param y_true_Qtensor: 1d array-like
        Ground truth (correct) target values. a QTensor.

    :param y_pred_Qtensor: 1d array-like
        Estimated target values. a QTensor.

    :return: float or ndarray of floats. Precision, recall, f1 score.

    Example::

            import numpy as np
            from pyvqnet.tensor import tensor
            from pyvqnet.utils import metrics as vqnet_metrics
            from pyvqnet import _core
            _vqnet = _core.vqnet

            y_true_Qtensor = tensor.QTensor([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
            y_pred_Qtensor = tensor.QTensor([0, 0, 1, 1, 1, 0, 0, 1, 1, 1])

            precision, recall, f1 = vqnet_metrics.precision_recall_f1_2_score(
                y_true_Qtensor, y_pred_Qtensor)
            print(precision, recall, f1) # 0.5 0.6 0.5454545454545454

    """
def precision_recall_f1_n_score(y_true_Qtensor, y_pred_Qtensor, N, average):
    """Compute the precision, recall and f1 score of the binary classification task.

        :param y_true_Qtensor: 1d array-like
            Ground truth (correct) target values. a QTensor.

        :param y_pred_Qtensor: 1d array-like
            Estimated target values. a QTensor.

        :param N: N Class(Number of categories).

        :param average: string, ['micro', 'macro', 'weighted'].
            This parameter is required for multiclass/multilabel targets.

            ``'micro'``:
                Calculate metrics globally by counting the total true positives,
                false negatives and false positives.

            ``'macro'``:
                Calculate metrics for each label, and find their unweighted
                mean.  This does not take label imbalance into account.

            ``'weighted'``:
                Calculate metrics for each label, and find their average weighted
                by support (the number of true instances for each label). This
                alters 'macro' to account for label imbalance; it can result in an
                F-score that is not between precision and recall.

        :return: float or ndarray of floats. Precision, recall, f1 score.

        Example::

                import numpy as np
                from pyvqnet.tensor import tensor
                from pyvqnet.utils import metrics as vqnet_metrics
                from pyvqnet import _core
                _vqnet = _core.vqnet

                reference_list = [1, 1, 2, 2, 2, 3, 3, 3, 3, 3]
                prediciton_list = [1, 2, 2, 2, 3, 1, 2, 3, 3, 3]
                y_true_Qtensor = tensor.QTensor(reference_list)
                y_pred_Qtensor = tensor.QTensor(prediciton_list)

                precision_micro, recall_micro, f1_micro = vqnet_metrics.precision_recall_f1_N_score(
                    y_true_Qtensor, y_pred_Qtensor, 3, average='micro')
                print(precision_micro, recall_micro, f1_micro) # 0.6 0.6 0.6

                precision_macro, recall_macro, f1_macro = vqnet_metrics.precision_recall_f1_N_score(
                    y_true_Qtensor, y_pred_Qtensor, 3, average='macro')
                print(precision_macro, recall_macro, f1_macro) # 0.5833333333333334 0.5888888888888889 0.5793650793650794

                precision_weighted, recall_weighted, f1_weighted = vqnet_metrics.precision_recall_f1_N_score(
                    y_true_Qtensor, y_pred_Qtensor, 3, average='weighted')
                print(precision_weighted, recall_weighted, f1_weighted) # 0.625 0.6 0.6047619047619047

                reference_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                prediciton_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                y_true_Qtensor = tensor.QTensor(reference_list)
                y_pred_Qtensor = tensor.QTensor(prediciton_list)

                precision_micro, recall_micro, f1_micro = vqnet_metrics.precision_recall_f1_N_score(
                    y_true_Qtensor, y_pred_Qtensor, 3, average='micro')
                print(precision_micro, recall_micro, f1_micro) # 1.0 1.0 1.0

                precision_macro, recall_macro, f1_macro = vqnet_metrics.precision_recall_f1_N_score(
                    y_true_Qtensor, y_pred_Qtensor, 3, average='macro')
                print(precision_macro, recall_macro, f1_macro) # 1.0 1.0 1.0

                precision_weighted, recall_weighted, f1_weighted = vqnet_metrics.precision_recall_f1_N_score(
                    y_true_Qtensor, y_pred_Qtensor, 3, average='weighted')
                print(precision_weighted, recall_weighted, f1_weighted) # 1.0 1.0 1.0


        """
precision_recall_f1_N_score = precision_recall_f1_n_score

def precision_recall_f1_multi_score(y_true_Qtensor, y_pred_Qtensor, N, average):
    """Compute the precision, recall and f1 score of the multi classification task.

            :param y_true_Qtensor: 2d array-like (sparse matrix)
                Ground truth (correct) target values. a QTensor.

            :param y_pred_Qtensor: 2d array-like (sparse matrix)
                Estimated target values. a QTensor.

            :param N: N Class(Number of categories).

            :param average: string, ['micro', 'macro', 'weighted'].
                This parameter is required for multiclass/multilabel targets.

                ``'micro'``:
                    Calculate metrics globally by counting the total true positives,
                    false negatives and false positives.

                ``'macro'``:
                    Calculate metrics for each label, and find their unweighted
                    mean.  This does not take label imbalance into account.

                ``'weighted'``:
                    Calculate metrics for each label, and find their average weighted
                    by support (the number of true instances for each label). This
                    alters 'macro' to account for label imbalance; it can result in an
                    F-score that is not between precision and recall.

            :return: float or ndarray of floats. Precision, recall, f1 score.

            Example::

                    import numpy as np
                    from pyvqnet.tensor import tensor
                    from pyvqnet.utils import metrics as vqnet_metrics
                    from pyvqnet import _core
                    _vqnet = _core.vqnet

                    reference_list = [[1, 0], [0, 1], [0, 0], [1, 1], [1, 0]]
                    prediciton_list = [[1, 0], [0, 0], [1, 0], [0, 0], [0, 0]]
                    y_true_Qtensor = tensor.QTensor(reference_list)
                    y_pred_Qtensor = tensor.QTensor(prediciton_list)

                    micro_precision, micro_recall, micro_f1 = vqnet_metrics.precision_recall_f1_Multi_score(reference_list_Qtensor,
                                reference_prediciton_list, 2, average='micro')
                    print(micro_precision, micro_recall, micro_f1) # 0.5 0.2 0.28571428571428575

                    macro_precision, macro_recall, macro_f1 = vqnet_metrics.precision_recall_f1_Multi_score(reference_list_Qtensor,
                                reference_prediciton_list, 2, average='macro')
                    print(macro_precision, macro_recall, macro_f1) # 0.25 0.16666666666666666 0.2

                    weighted_precision, weighted_recall, weighted_f1 = vqnet_metrics.precision_recall_f1_Multi_score(reference_list_Qtensor,
                                reference_prediciton_list, 2, average='weighted')
                    print(weighted_precision, weighted_recall, weighted_f1) # 0.3 0.19999999999999998 0.24

                    reference_list = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1]]
                    prediciton_list = [[1, 0, 0], [1, 0, 0], [1, 1, 1], [1, 0, 0], [0, 1, 1]]
                    y_true_Qtensor = tensor.QTensor(reference_list)
                    y_pred_Qtensor = tensor.QTensor(prediciton_list)

                    micro_precision, micro_recall, micro_f1 = vqnet_metrics.precision_recall_f1_Multi_score(reference_list_Qtensor,
                                reference_prediciton_list, 3, average='micro')
                    print(micro_precision, micro_recall, micro_f1) # 0.5 0.5714285714285714 0.5333333333333333

                    macro_precision, macro_recall, macro_f1 = vqnet_metrics.precision_recall_f1_Multi_score(reference_list_Qtensor,
                                reference_prediciton_list, 3, average='macro')
                    print(macro_precision, macro_recall, macro_f1) # 0.5 0.5555555555555555 0.5238095238095238

                    weighted_precision, weighted_recall, weighted_f1 = vqnet_metrics.precision_recall_f1_Multi_score(reference_list_Qtensor,
                                reference_prediciton_list, 3, average='weighted')
                    print(weighted_precision, weighted_recall, weighted_f1) # 0.5 0.5714285714285714 0.5306122448979592



            """
precision_recall_f1_Multi_score = precision_recall_f1_multi_score

def auc_calculate(y_true_Qtensor, y_pred_Qtensor, pos_label: Incomplete | None = None, sample_weight: Incomplete | None = None, drop_intermediate: bool = True):
    '''Compute Area Under the Curve (AUC).

            :param y_true_Qtensor: 1d array-like. a QTensor.

            :param y_pred_Qtensor: 1d array-like. a QTensor.

            :param pos_label: int or str, default=None
                The label of the positive class.
                When ``pos_label=None``, if y_true is in {-1, 1} or {0, 1},
                ``pos_label`` is set to 1, otherwise an error will be raised.

            :param sample_weight: array-like of shape (n_samples,), default=None
                Sample weights.

            :param drop_intermediate: boolean, optional (default=True)
                Whether to drop some suboptimal thresholds which would not appear
                on a plotted ROC curve. This is useful in order to create lighter
                ROC curves.

            :return: float. Compute the area under the ROC curve.

            Example::

                import numpy as np
                from pyvqnet.tensor import tensor
                from pyvqnet.utils import metrics as vqnet_metrics
                from pyvqnet import _core
                _vqnet = _core.vqnet

                y = np.array([1, 1, 1, 1, 0, 1, 0, 0, 0, 0])
                pred = np.array([0.9, 0.8, 0.7, 0.6, 0.6, 0.4, 0.4, 0.3, 0.2, 0.1])
                y_Qtensor = tensor.QTensor(y)
                pred_Qtensor = tensor.QTensor(pred)
                result = vqnet_metrics.auc_calculate(y_Qtensor, pred_Qtensor)
                print("auc:", result) # 0.92

                y = np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 1])
                pred = np.array([1, 0, 1, 1, 1, 1, 0, 1, 1, 0])
                y_Qtensor = tensor.QTensor(y)
                pred_Qtensor = tensor.QTensor(pred)
                result = vqnet_metrics.auc_calculate(y_Qtensor, pred_Qtensor)
                print("auc:", result) # 0.625

                y = [1, 2, 1, 1, 1, 0, 0, 1, 1, 1]
                pred = [1, 0, 2, 1, 1, 1, 0, 1, 1, 0]
                act_Qtensor = tensor.QTensor(act)
                pre_Qtensor = tensor.QTensor(pre)
                result = vqnet_metrics.auc_calculate(act_Qtensor, pre_Qtensor, pos_label=2)
                print("auc:", result) # 0.1111111111111111

            '''
