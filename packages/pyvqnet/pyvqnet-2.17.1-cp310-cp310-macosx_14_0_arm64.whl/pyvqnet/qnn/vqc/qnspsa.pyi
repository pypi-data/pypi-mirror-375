from ...device import DEV_CPU as DEV_CPU
from ...dtype import complex_dtype_to_float_dtype as complex_dtype_to_float_dtype, kfloat32 as kfloat32
from ...tensor import QTensor as QTensor
from _typeshed import Incomplete
from pyvqnet.qnn.vqc import MeasureAll as MeasureAll, Probability as Probability
from pyvqnet.qnn.vqc.qmachine import QMachine as QMachine, not_just_define_op as not_just_define_op, not_save_op_history as not_save_op_history, return_op_list as return_op_list
from pyvqnet.qnn.vqc.qmachine_utils import find_qmachine as find_qmachine

def construct_tape(qmodel, *args_plus, **kwargs): ...

class QNSPSAOptimizer:
    """
    \u200b\u200bQuantum Natural SPSA (QNSPSA) Optimizer\u200b\u200b

    A second-order stochastic optimizer for quantum circuits that combines gradient descent with Fubini-Study metric tensor information. Key features:

    \u200b\u200bGradient Estimation\u200b\u200b (like SPSA):
    Uses symmetric perturbations:
    
    .. math::

        \x08egin{equation}
    \\widehat{
abla f}(\\mathbf{x}) \x07pprox \x0crac{f(\\mathbf{x}+\\epsilon \\mathbf{h})-f(\\mathbf{x}-\\epsilon \\mathbf{h})}{2\\epsilon}
    \\end{equation}
    
    \u200b\u200bMetric Tensor Estimation\u200b\u200b:
    Computes Fubini-Study metric via state overlap measurements:
    
    .. math::

        \x08egin{equation}
        \\widehat{\\mathbf{g}}(\\mathbf{x}) \x07pprox \x0crac{\\delta F}{8\\epsilon^2}(\\mathbf{h}_1\\mathbf{h}_2^\\intercal + \\mathbf{h}_2\\mathbf{h}_1^\\intercal)
        \\end{equation}
        where:
        \x08egin{equation}
        \\delta F = F(\\mathbf{x}+\\epsilon\\mathbf{h}_1+\\epsilon\\mathbf{h}_2) - F(\\mathbf{x}+\\epsilon\\mathbf{h}_1) - F(\\mathbf{x}-\\epsilon\\mathbf{h}_1+\\epsilon\\mathbf{h}_2) + F(\\mathbf{x}-\\epsilon\\mathbf{h}_1)
        \\end{equation}

    where δF measures overlap differences from four circuit evaluations
    \u200b\u200bUpdate Rule\u200b\u200b:

    .. math::

        \x08egin{equation}
        \\mathbf{x}^{(t+1)} = \\mathbf{x}^{(t)} - \\eta \\widehat{\\mathbf{g}}^{-1}(\\mathbf{x}^{(t)})\\widehat{
abla f}(\\mathbf{x}^{(t)})
        \\end{equation}
    \u200b\u200b
    """
    stepsize: Incomplete
    reg: Incomplete
    finite_diff_step: Incomplete
    metric_tensor: Incomplete
    k: int
    resamplings: Incomplete
    blocking: Incomplete
    last_n_steps: Incomplete
    rng: Incomplete
    def __init__(self, stepsize: float = 0.001, regularization: float = 0.001, finite_diff_step: float = 0.01, resamplings: int = 1, blocking: bool = True, history_length: int = 5, seed=None) -> None:
        '''
        :param stepsize: the user-defined hyperparameter :math:`\\eta` for learning rate (default: 1e-3)
        :type stepsize: float

        :param regularization: regularization term :math:`\\beta` to the Fubini-Study metric tensor
            for numerical stability (default: 1e-3)
        :type regularization: float

        :param finite_diff_step: step size :math:`\\epsilon` to compute the finite difference
            gradient and the Fubini-Study metric tensor (default: 1e-2)
        :type finite_diff_step: float

        :param resamplings: the number of samples to average for each parameter update (default: 1)
        :type resamplings: int

        :param blocking: when True, only accepts updates that lead to a loss value no larger than
            the previous loss plus tolerance (helps convergence) (default: True)
        :type blocking: bool

        :param history_length: when ``blocking`` is True, tolerance is set as average of last
            ``history_length`` cost values (default: 5)
        :type history_length: int

        :param seed: seed for the random sampling (default: None)
        :type seed: Optional[int]

        Examples::

            from pyvqnet.tensor import QTensor,ones,randu
            from pyvqnet.qnn.vqc import rx,cry,QMachine,MeasureAll,QModule

            num_qubits = 2
            class QModuleDemo(QModule):
                def __init__(self, name=""):
                    super().__init__(name)
                    self.qm = QMachine(num_qubits)
                    self.ma = MeasureAll({"Z1 Z0":1})
                def forward(self,params):
                    qm = self.qm
                    qm.reset_states(1)
                    rx(qm, 0, params[0])
                    cry(qm, [0, 1], params[1])
                    return self.ma(qm)

            qmd = QModuleDemo()

            from pyvqnet.qnn.vqc.qnspsa import QNSPSAOptimizer
            params = QTensor([0.37454012, 0.95071431])

            params.requires_grad = True
            opt =  QNSPSAOptimizer(stepsize=5e-2,seed=1)
            for i in range(51):
                params = opt.step(qmd, params)
                loss =qmd(params)
                if i % 10 == 0:
                    print(f"Step {i}: cost = {loss}")

        '''
    def step(self, qmodel, *args, **kwargs):
        """Update trainable arguments with one step of the optimizer.
        
        :param qmodel: A trainable quantum model
        :param args: variable length trainable qtensor for qmodel.
        :param kwargs: variable length of keyword arguments for qmodel

        :return: updated parameters.
        """
    def step_and_cost(self, cost, *args, **kwargs):
        """Update trainable parameters with one step of the optimizer and return
        the corresponding objective function value after the step.

        """
    @staticmethod
    def execute(tapes, qm): ...
