from collections import defaultdict
from copy import deepcopy

from ..exceptions import PermissionError, RequestError
from ..models import DataAttribute, DataGenerator, DataStream, ProjectData
from .permission_service import has_permission


class ProjectDataService:
    __model__ = ProjectData

    def get_used_input_attributes(self, data_id) -> list[DataAttribute]:
        """Get used input attributes of project data if the user is authorized
        to access it.

        This list contains al inputl attributes used at least once in a
        processing model of the project data.

        Raises:
            PermissionError if the user is not authorized to access the data's
            project.
            RequestError (code 404) if the project data does not exist.

        Returns:
            Used input attributes.
        """
        data = self.get_if_authorized(data_id)
        return data.get_used_input_attributes()

    def get_used_attributes(self, data_id) -> list[DataAttribute]:
        """Get used attributes of project data if the user is authorized
        to access it.

        This list contains all attributes used at least once in a processing
        model of the downstream project data.

        Raises:
            PermissionError if the user is not authorized to access the data's
            project.
            RequestError (code 404) if the project data does not exist.

        Returns:
            Used attributes.
        """
        data = self.get_if_authorized(data_id)
        return data.get_used_attributes()

    def _filter_input_data(self, data):
        """Returns the list of data that need to be processed

        A data needs to be processed if its input data is more recent.
        """

        def recursive_filter(nodes, data, level=0):
            data_process = False
            if data.is_outdated():
                nodes[data.id]
                data_process = True
            for d in data.input_data:
                if isinstance(d, DataGenerator) or isinstance(d, DataStream):
                    if recursive_filter(nodes, d, level=level + 1):
                        nodes[data.id].append(d.id)
                        data_process = True
            return data_process

        nodes = defaultdict(list)
        nodes[data.id]
        recursive_filter(nodes, data)
        return dict(nodes)

    def _topological_sort(self, n):
        """Returns a topological sort of the nodes using Kahn's algorithm"""
        nodes = deepcopy(n)
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
        return sorted_data

    def get_grouped_dependant_data_ids(self, data):
        """Return the ids of project data that need to be processed, sorted and
        grouped by depth.

        The grouped project data are independant and can be processed in
        parallel.
        """
        nodes_depth = {}
        nodes = self._filter_input_data(data)
        sorted_data = self._topological_sort(nodes)
        for node in sorted_data:
            depths = [0]
            for src in nodes[node]:
                if src in nodes_depth.keys():
                    depths.append(nodes_depth[src] + 1)
            nodes_depth[node] = max(depths)
        result = []
        for current_depth in set(sorted(nodes_depth.values())):
            result.append([])
            for node, depth in list(nodes_depth.items()):
                if depth == current_depth:
                    del nodes_depth[node]
                    result[-1].append(node)
        return result

    def get_if_authorized(self, project_data_id) -> ProjectData:
        """Load the the project data if the user is authorized to access it.

        Raises:
            PermissionError if the user is not authorized to access the data's
            project.
            RequestError (code 404) if the project data does not exist.

        Returns:
            The project data object.
        """
        project_data = self.__model__.get_by_id(project_data_id)
        if project_data is None:
            raise RequestError(
                "The project data requested does not exist", 404
            )
        if not has_permission(project_data.project):
            raise PermissionError
        return project_data
