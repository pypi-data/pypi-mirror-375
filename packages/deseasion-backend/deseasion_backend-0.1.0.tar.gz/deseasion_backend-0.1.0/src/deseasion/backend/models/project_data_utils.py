from copy import deepcopy

from . import db
from .geo_data import DataAttribute
from .processing_models import (
    ContinuousRule,
    DiscreteRules,
    MRSort,
    MRSortCriterion,
    PrefDefaultValues,
    WeightedSum,
    _replace_variables_code,
)
from .project import Project
from .project_data import DataGenerator, ProjectData


class ProjectDataProcessingService:
    def rename_data(self, data: ProjectData, new_name: str):
        """Rename project data and modify models using it.

        :param data:
        :param new_name: new project data name
        """
        if data.data is None:
            data.name = new_name
            return

        var_mapping = {}
        for attr in data.data.attributes:
            var_mapping[(data.name, attr.name)] = (new_name, attr.name)

        for d in data.output_data:
            for model in d._processing_models:
                match model:
                    case DiscreteRules():
                        for category in model.categories:
                            rules = []
                            for rule in category.rules:
                                rules.append(
                                    _replace_variables_code(rule, var_mapping)
                                )
                            category.rules = rules
                            db.session.add(category)
                    case ContinuousRule():
                        model.rule = _replace_variables_code(
                            model.rule, var_mapping
                        )
                        db.session.add(model)
        data.name = new_name

    def detach_input(
        self, data: ProjectData, removable_input_data: list[ProjectData]
    ):
        """Detach input from project data.

        Only necessary to remove operands/criteria/default values from
        processing models that used to use those inputs.

        :param data:
        :param removable_input_data: sequence of data inputs to remove

        .. note:: do not actually remove input, simply clean afterwards
        """
        if not isinstance(data, DataGenerator):
            return

        attributes = []
        for d in removable_input_data:
            if d.data is None:
                continue
            attributes += list(d.data.attributes)

        if len(attributes) == 0:
            return

        for model in data._processing_models:
            match model:
                case PrefDefaultValues():
                    for def_value in model.default_values:
                        if def_value.attribute in attributes:
                            db.session.delete(def_value)
            match model:
                case WeightedSum():
                    for op in model.operands:
                        if op.attribute in attributes:
                            db.session.delete(op)
                case MRSort():
                    for criterion in model.criteria:
                        if criterion.attribute in attributes:
                            db.session.delete(criterion)

    def _topological_sort(self, graph):
        """Sort nodes topologically using Kahn's algorithm.

        :param graph: directed graph
        :raises TypeError: if `graph` is not acyclic
        :return: topologically ordered nodes
        """
        nodes = deepcopy(graph)
        sorted_data = []
        set_queue = []
        for node, edges in list(nodes.items()):
            if len(edges) == 0:
                del nodes[node]
                set_queue.append(node)
        while len(set_queue) > 0:
            current = set_queue.pop()
            sorted_data.append(current)
            for node, edges in list(nodes.items()):
                if current in edges:
                    edges.remove(current)
                    if len(edges) == 0:
                        del nodes[node]
                        set_queue.append(node)
        if len(nodes) > 0:
            raise TypeError("Graph is not acyclic")
        return sorted_data

    def get_project_data_graph(
        self, project: Project
    ) -> dict[ProjectData, list[ProjectData]]:
        """Return complete project data graph.

        :param project:
        :return:
        """
        return {data: list(data.input_data) for data in project.data_list}

    def get_input_graph(
        self, data: ProjectData
    ) -> dict[ProjectData, list[ProjectData]]:
        """Return graph of input data spanning from current project data.

        :param data:
        :return:
        """
        graph = {}
        nodes = [data]
        while len(nodes) > 0:
            node = nodes.pop(0)
            if node in graph:
                continue
            graph[node] = list(node.input_data)
            nodes += list(set(node.input_data) - set(nodes))
        return graph

    def get_output_graph(
        self, data: ProjectData
    ) -> dict[ProjectData, list[ProjectData]]:
        """Return graph of output data spanning from current project data.

        :param data:
        :return:
        """
        graph = {}
        nodes = [data]
        while len(nodes) > 0:
            node = nodes.pop(0)
            if node in graph:
                continue
            graph[node] = list(node.output_data)
            nodes += list(set(node.output_data) - set(nodes))
        return graph

    def _replace_attributes_code(
        self,
        data: ProjectData,
        code: str,
        attributes_mapping: dict[DataAttribute, DataAttribute],
    ) -> str:
        """Replace attributes by others in code safely.

        :param data: project data to modify model's code
        :param code: code to modify
        :param attributes_mapping: mapping of old attributes to new ones
        :return: modified code
        """
        var_mapping = {}
        for d in data.project.data_list:
            if d.data is None:
                continue
            for attr in d.data.attributes:
                new_attr = attributes_mapping.get(attr, attr)
                var_mapping[(d.name, attr.name)] = (d.name, new_attr.name)
        return _replace_variables_code(code, var_mapping)

    def replace_input_attributes(
        self,
        data: ProjectData,
        attributes_mapping: dict[DataAttribute, DataAttribute],
    ):
        """Replace input attributes of project data by new ones.

        :param data:
        :param attributes_mapping: mapping of old attributes to new ones
        :raise ValueError:
            * if some new attributes introduced were already in the data inputs
            * if attributes from a different project are used
        :raise TypeError: if an attribute has changed its type
        """
        if not isinstance(data, DataGenerator):
            return

        # Mapping between data id and project data
        project_data_map = {}
        for p_data in data.project.data_list:
            if p_data.data is None:
                continue
            project_data_map[p_data.data.id] = p_data

        # List of data in downstream
        # (that would create cycles if used as inputs)
        unusable_data = sorted(
            set.union(
                *[
                    set(outputs)
                    for outputs in self.get_output_graph(data).values()
                ]
            ),
            key=lambda pdata: pdata.id,
        )
        unusable_data.append(data)  # Also add project data (avoid self loop)

        # Loop over attributes mapping
        new_project_data = set()
        for old_attr, new_attr in attributes_mapping.items():
            # Ignore mapping if old attribute's data is not an input
            if project_data_map[old_attr.data.id] not in data.input_data:
                continue
            # Check new attribute is not already an used input of project data
            if new_attr in data.get_used_input_attributes():
                raise ValueError(
                    "new attribute given was already among used inputs: "
                    f"{new_attr.id}"
                )
            if old_attr.type != new_attr.type:
                raise TypeError(
                    "cannot change attribute type through remapping: "
                    f"{old_attr.id}"
                )
            # Gather set of new project data
            new_project_data.add(project_data_map[new_attr.data.id])

        for new_input_data in new_project_data - set(data.input_data):
            data.add_input(new_input_data)

        for model in data._processing_models:
            match model:
                case PrefDefaultValues():
                    for def_value in model.default_values:
                        if def_value.attribute not in attributes_mapping:
                            continue
                        def_value.attribute = attributes_mapping.get(
                            def_value.attribute, def_value.attribute
                        )
                        db.session.add(def_value)
            match model:
                case WeightedSum():
                    for op in model.operands:
                        if op.attribute not in attributes_mapping:
                            continue
                        op.attribute = attributes_mapping.get(
                            op.attribute, op.attribute
                        )
                        db.session.add(op)
                case MRSort():
                    for criterion in model.criteria:
                        if criterion.attribute not in attributes_mapping:
                            continue
                        new_criterion = MRSortCriterion(
                            mrsort_id=model.id,
                            profiles=criterion.profiles,
                            weight=criterion.weight,
                            maximize=criterion.maximize,
                            attribute_id=(
                                attributes_mapping[criterion.attribute].id,
                            ),
                        )
                        db.session.add(new_criterion)
                        db.session.delete(criterion)
                case DiscreteRules():
                    for category in model.categories:
                        rules = []
                        for rule in category.rules:
                            rules.append(
                                self._replace_attributes_code(
                                    data, rule, attributes_mapping
                                )
                            )
                        category.rules = rules
                        db.session.add(category)
                case ContinuousRule():
                    model.rule = self._replace_attributes_code(
                        data, model.rule, attributes_mapping
                    )
            db.session.add(model)
        data.on_modification()
        db.session.add(data)
