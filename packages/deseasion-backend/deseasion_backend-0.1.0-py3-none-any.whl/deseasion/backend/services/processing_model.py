import random

import pulp as pp

from ..exceptions import InferenceError, RequestError
from ..models.geo_data import DataAttribute
from ..models.geo_data_utils import ModelProcessingService
from ..models.mrsort_inference import MRSortInferenceAlternative
from ..models.processing_models import ProcessingModel
from ..tasks import process_and_set_model, update_stream_data


class ProcessingModelService:
    def get_used_input_attributes(self, model_id) -> list[DataAttribute]:
        """Get list of used input attributes in a model definition.

        :param model_id:
        :raises RequestError: 404, if model `model_id` does not exist.
        :return:
        """
        model = ProcessingModel.get_by_id(model_id)
        if model is None:
            raise RequestError("The model does not exist", 404)
        return model.get_used_input_attributes()

    def task_process(self, model_id):
        """
        Start a celery task to process the model.

        Args:
            model_id: The id of the processing model.

        Returns:
            A celery task.
        """
        return process_and_set_model.si(model_id=model_id)

    def update_stream_process(
        self,
        data_id,
    ):
        return update_stream_data.si(
            data_id=data_id,
        )

    def _get_mrsort_alternatives(self, model, data, count=100):
        """
        Choose alternatives for the inference model.

        Args:
            model: A MR-Sort model.
            data: A list of the data for each attribute in the form
                  [{'attr1': val, 'attr2': val}, {'attr1': val, ...}, ...]
            count (int): The number of alternatives to propose. Default: 100.
        """
        # Make sure the criteria are up to date
        model.init_criteria()
        criteria = {c.attribute: c for c in model.criteria}
        choices = []
        for d in data:
            # Filter duplicates and ignore when the value of an attribute is
            # None
            if d not in choices and all((v is not None for v in d.values())):
                choices.append(d)
        try:
            final_choices = random.sample(choices, count)
        except ValueError:
            final_choices = choices
        alternatives = []
        for c in final_choices:
            alternative = MRSortInferenceAlternative(mrsort=model)
            for attr, val in c.items():
                # Only consider model criteria (i.e quantitative data)
                if attr in criteria:
                    alternative.values[criteria[attr]] = val
            alternatives.append(alternative)
        return alternatives

    def load_mrsort_inference_data(self, model):
        """
        Decompose the geometries to generate the alternatives for the MR-Sort
        inference.
        """
        processing_service = ModelProcessingService()
        data = processing_service.get_decomposed_data(model)
        alternatives = self._get_mrsort_alternatives(model, data)
        model.inference_alternatives = alternatives
        model.update()
        return alternatives

    def _solve_lp(self, X, F, Fdir, Fmin, Fmax, K, A, PTx, gamma):
        """
        Solve the linear problem for the inference of the MR-Sort model.

        Args:
            X: Number of alternatives.
            F: Number of criteria.
            Fdir:
                Criteria perference directions
                (1 for maximizing, -1 for minimizing).
            Fmin: Minimum values for the criteria.
            Fmax: Maximum values for the criteria.
            K: Number of categories.
            A: Assignements for the alternatives (0 is best, K-1 is worst).
            PTx: Performance table for the alternatives.
            gamma: Separation value for the inequalities and parameters.
        """
        # Convert the list to a dict
        PTx = {(x, i): PTx[x][i] for x in range(X) for i in range(F)}

        # Initialize the problem
        prob = pp.LpProblem("MR-Sort inference", pp.LpMinimize)

        # Variables
        _lambda = pp.LpVariable("majority threshold", 0.5, 1)
        w = pp.LpVariable.dicts("weight", range(F), 0, 1)
        PTk = pp.LpVariable.dicts(
            "performance profiles",
            ((k, i) for k in range(K + 1) for i in range(F)),
        )
        lCupp = pp.LpVariable.dicts(
            "upper profile",
            ((x, i) for x in range(X) for i in range(F)),
            cat=pp.LpBinary,
        )
        lClow = pp.LpVariable.dicts(
            "lower profile",
            ((x, i) for x in range(X) for i in range(F)),
            cat=pp.LpBinary,
        )
        wlCupp = pp.LpVariable.dicts(
            "weighted upper", ((x, i) for x in range(X) for i in range(F))
        )
        wlClow = pp.LpVariable.dicts(
            "weighted lower", ((x, i) for x in range(X) for i in range(F))
        )

        # Constraints
        prob += pp.lpSum(w) == 1, "normalizedWeights"
        for i in range(F):
            prob += (
                PTk[K, i] == Fmin[i] - gamma
                if Fdir[i] > 0
                else Fmax[i] + gamma
            )
            prob += (
                PTk[0, i] == Fmax[i] + gamma
                if Fdir[i] > 0
                else Fmin[i] - gamma
            )
            for x in range(X):
                f_diff = Fmax[i] - Fmin[i] + 1
                prob += (
                    Fdir[i] * (PTx[x, i] - PTk[A[x], i]) + gamma
                    <= lCupp[x, i] * f_diff
                )
                prob += (lCupp[x, i] - 1) * f_diff <= Fdir[i] * (
                    PTx[x, i] - PTk[A[x], i]
                )
                prob += (
                    Fdir[i] * (PTx[x, i] - PTk[A[x] + 1, i]) + gamma
                    <= lClow[x, i] * f_diff
                )
                prob += (lClow[x, i] - 1) * f_diff <= Fdir[i] * (
                    PTx[x, i] - PTk[A[x] + 1, i]
                )
                prob += wlCupp[x, i] <= w[i]
                prob += 0 <= wlCupp[x, i]
                prob += wlCupp[x, i] <= lCupp[x, i]
                prob += lCupp[x, i] + w[i] - 1 <= wlCupp[x, i]
                prob += wlClow[x, i] <= w[i]
                prob += 0 <= wlClow[x, i]
                prob += wlClow[x, i] <= lClow[x, i]
                prob += lClow[x, i] + w[i] - 1 <= wlClow[x, i]
            for k in range(K):
                prob += Fdir[i] * PTk[(k + 1), i] <= Fdir[i] * PTk[k, i]
        for x in range(X):
            prob += _lambda <= pp.lpSum([wlClow[x, i] for i in range(F)])
            prob += (
                pp.lpSum([wlCupp[x, i] for i in range(F)]) + gamma <= _lambda
            )

        # Solve the problem
        # use prob.solve(pp.GLPK(msg=False)) to solve with GLPK
        prob.solve()

        if pp.LpStatus[prob.status] != "Optimal":
            raise InferenceError()

        result = {
            "lambda": _lambda.varValue,
            "weights": [w[i].varValue for i in range(F)],
            "profiles": [
                [PTk[k, i].varValue for i in range(F)] for k in range(K + 1)
            ],
        }
        return result

    def infer_model(self, mrsort):
        """
        Infer the MR-Sort model and update its parameters from the
        alternatives.

        Args:
            mrsort: The MR-Sort object.
        """
        alternatives = list(
            filter(
                lambda a: a.category is not None, mrsort.inference_alternatives
            )
        )
        categories = list(mrsort.categories)
        model = self._solve_lp(
            X=len(alternatives),
            F=len(mrsort.criteria),
            Fdir=[1 if c.maximize else -1 for c in mrsort.criteria],
            Fmin=[
                min((v.value for v in c.inference_values))
                for c in mrsort.criteria
            ],
            Fmax=[
                max((v.value for v in c.inference_values))
                for c in mrsort.criteria
            ],
            K=len(mrsort.categories),
            A=[categories.index(a.category) for a in alternatives],
            PTx=[[a.values[c] for c in mrsort.criteria] for a in alternatives],
            gamma=0.1,
        )

        majority_threshold = model.get("lambda")
        weights = model.get("weights", [])
        profiles = model.get("profiles", [[]])

        mrsort.majority_threshold = majority_threshold
        for index, criterion in enumerate(mrsort.criteria):
            criterion.maximize = mrsort.criteria[index].maximize
            criterion.weight = weights[index]
            prof = [p[index] for p in profiles]
            criterion.profiles = prof[
                len(prof) - 2 : 0 : -1
            ]  # reverse order (worst first)
        mrsort.update()
