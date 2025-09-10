# Copyright 2025 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration.  All Rights Reserved.
#
# The Materialite platform is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from abc import abstractmethod
from copy import deepcopy

import numpy as np
import pandas as pd

try:
    import pyvista as pv
except ImportError:
    pv = None
from scipy import spatial

from materialite.tensor import Order2SymmetricTensor, Orientation, Scalar, Vector
from materialite.util import cartesian_grid, power_of_two_below, repeat_data


class Material:
    """
    A 3D point grid representation for materials modeling.

    The Material class provides a unified data structure for representing
    materials as 3D grids of points with associated spatial numerical or
    tensorial fields.

    Parameters
    ----------
    dimensions : list, default [16, 16, 16]
        Number of points in each direction [x, y, z].
    origin : list, default [0, 0, 0]
        Coordinates of the domain origin [x, y, z].
    spacing : list, default [1, 1, 1]
        Distance between points in each direction [x, y, z].
    sizes : list, optional
        Total size of the domain in each direction. If provided, overrides spacing.
    fields : dict or DataFrame, optional
        Initial field data. If None, creates coordinate fields only.
    """

    def __init__(
        self,
        dimensions=[16, 16, 16],
        origin=[0, 0, 0],
        spacing=[1, 1, 1],
        sizes=None,
        fields=None,
    ):
        self._dimensions = np.array(dimensions)
        self._origin = np.array(origin)
        spacing = np.array(spacing)
        sizes = np.array(sizes) if sizes is not None else None
        self._spacing, self._sizes = self._get_spacing_and_sizes(
            spacing, sizes, self.dimensions
        )

        self.fields = self._initialize_fields(fields)
        self.state = dict()
        self._regional_fields = dict()

    @property
    def origin(self):
        """Origin coordinates of the domain."""
        return self._origin.copy()

    @property
    def dimensions(self):
        """Number of points in each direction."""
        return self._dimensions.copy()

    @property
    def spacing(self):
        """Spacing between points in each direction."""
        return self._spacing.copy()

    @property
    def sizes(self):
        """Total size of the domain in each direction."""
        return self._sizes.copy()

    def _get_spacing_and_sizes(self, spacing, sizes, dimensions):
        """Calculate spacing and sizes from given parameters."""
        if sizes is not None:
            spacing = sizes / (dimensions - 1)
        else:
            sizes = spacing * (dimensions - 1)
        return spacing, sizes

    def _initialize_fields(self, fields):
        """Initialize the fields DataFrame with coordinate information."""
        grid = cartesian_grid(self.dimensions)
        if fields is None:
            fields = pd.DataFrame(
                {
                    "x": grid[:, 0] * self.spacing[0] + self.origin[0],
                    "y": grid[:, 1] * self.spacing[1] + self.origin[1],
                    "z": grid[:, 2] * self.spacing[2] + self.origin[2],
                }
            )
        else:
            fields = self._initialize_fields_from_user_input(fields, grid)

        return fields.assign(x_id=grid[:, 0], y_id=grid[:, 1], z_id=grid[:, 2])

    def _initialize_fields_from_user_input(self, fields, grid):
        """Process user-provided fields and validate against grid dimensions."""
        fields = pd.DataFrame(fields)
        if len(fields) != self.num_points:
            raise ValueError(
                "length of fields does not match number of points from dimensions"
            )
        provided_labels = fields.columns
        if np.any(
            ["x" in provided_labels, "y" in provided_labels, "z" in provided_labels]
        ):
            # user provided at least one of x, y, and z
            # fill singleton dimensions with ones in fields
            singleton_dimensions = np.where(self.dimensions == 1)[0]
            xyz = np.array(["x", "y", "z"])
            fields = fields.assign(
                **dict(
                    zip(xyz[singleton_dimensions], self.origin[singleton_dimensions])
                )
            ).sort_values(by=["x", "y", "z"], ignore_index=True)
            inferred_dims = [len(fields[s].unique()) for s in ["x", "y", "z"]]
            if not np.array_equal(inferred_dims, self.dimensions):
                raise ValueError(
                    "provided x, y, and z fields do not match provided dimensions"
                )
            inferred_sizes = (
                fields[["x", "y", "z"]].max() - fields[["x", "y", "z"]].min()
            )
            if not np.array_equal(inferred_sizes, self.sizes):
                raise ValueError(
                    "provided x, y, and z fields do not match provided sizes"
                )
            return fields
        else:
            # x, y, and z were all not provided by the user
            return fields.assign(
                x=grid[:, 0] * self.spacing[0] + self.origin[0],
                y=grid[:, 1] * self.spacing[1] + self.origin[1],
                z=grid[:, 2] * self.spacing[2] + self.origin[2],
            )

    @property
    def num_points(self):
        """Total number of points in the material."""
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]

    def run(self, model, **kwargs):
        """
        Run a model on this material.

        Parameters
        ----------
        model : callable
            A model object or function that takes a Material as first argument.
        **kwargs
            Additional arguments passed to the model.

        Returns
        -------
        Result of the model evaluation.
        """
        return model(self, **kwargs)

    def copy(self):
        """Create a deep copy of the material."""
        return deepcopy(self)

    def get_fields(self):
        """
        Get all fields including regional fields merged in.

        Returns
        -------
        pandas.DataFrame
            Combined field data with regional fields merged.
        """
        fields = self.fields.copy()
        for k, v in self._regional_fields.items():
            try:
                fields = fields.merge(
                    v, on=k, how="left", suffixes=(False, False), validate="many_to_one"
                )
            except ValueError:
                raise ValueError(
                    "Error when merging regional fields. Two different regional fields defined values for the same field."
                )
        return fields

    def extract(self, labels):
        """
        Extract field data as arrays or tensor objects.

        Parameters
        ----------
        labels : str or list
            Field name(s) to extract.

        Returns
        -------
        numpy.ndarray or tensor object
            Extracted field data.
        """
        if isinstance(labels, str):
            data = self.get_fields()[labels].to_list()
            try:
                result = type(data[0]).from_list(data)
            except AttributeError:
                result = np.array(data)
        else:
            result = self.get_fields()[labels].to_numpy()
        return result

    def create_fields(self, fields):
        """
        Create a new material with additional fields.

        Parameters
        ----------
        fields : dict
            Dictionary of field_name: field_data pairs.

        Returns
        -------
        Material
            New material with the added fields.
        """
        material = self.copy()
        material.fields = material.fields.assign(**fields)
        return material

    def create_random_integer_field(
        self, label, low, high=None, rng=np.random.default_rng()
    ):
        """
        Create a field with random integer values.

        Parameters
        ----------
        label : str
            Name of the new field.
        low : int
            Lower bound (inclusive).
        high : int, optional
            Upper bound (exclusive).
        rng : numpy.random.Generator
            Random number generator.

        Returns
        -------
        Material
            New material with the random field added.
        """
        values = rng.integers(
            low=low, high=high, size=self.num_points
        )  # Excludes high value
        return self.create_fields({label: values})

    def create_uniform_field(self, label, value):
        """
        Create a field with uniform values at all points.

        Parameters
        ----------
        label : str
            Name of the new field.
        value : any
            Value to assign to all points.

        Returns
        -------
        Material
            New material with the uniform field added.
        """
        field = {label: [value] * self.num_points}
        return self.create_fields(field)

    def segment(self, label, threshold, low=0, high=1, new_label=None):
        """
        Create a binary segmentation of a field based on a threshold.

        Parameters
        ----------
        label : str
            Name of the field to segment.
        threshold : float
            Threshold value for segmentation.
        low : any, default 0
            Value assigned to points below threshold.
        high : any, default 1
            Value assigned to points above threshold.
        new_label : str, optional
            Name for the new field. Defaults to "segmented_{label}".

        Returns
        -------
        Material
            New material with the segmented field added.
        """
        if new_label is None:
            new_label = "segmented_" + label
        return self.create_fields(
            {new_label: np.where(self.extract(label) > threshold, high, low)}
        )

    def create_voronoi(
        self,
        num_regions=10,
        label="region",
        rng=np.random.default_rng(),
        periodic=False,
    ):
        """
        Create Voronoi regions in the material.

        Parameters
        ----------
        num_regions : int, default 10
            Number of Voronoi regions to create.
        label : str, default "region"
            Name for the region field.
        rng : numpy.random.Generator
            Random number generator for seed points.
        periodic : bool, default False
            Whether to enforce periodic boundary conditions.

        Returns
        -------
        Material
            New material with Voronoi regions added.
        """
        voronoi_points = rng.random((num_regions, 3)) * self.sizes + self.origin
        material_points = self.fields[["x", "y", "z"]].to_numpy()

        if periodic:
            voronoi_ref = np.tile(np.arange(num_regions), 27)
            voronoi_all = np.arange(num_regions * 27)
            voronoi_dict = dict(zip(voronoi_all, voronoi_ref))
            voronoi_points_periodic = repeat_data(voronoi_points, *self.sizes)
            material_points_periodic = repeat_data(material_points, *self.sizes)
            _, point_regions_periodic = spatial.cKDTree(voronoi_points_periodic).query(
                material_points_periodic, k=1
            )
            point_regions = [
                voronoi_dict[p] for p in point_regions_periodic[: self.num_points]
            ]
        else:
            _, point_regions = spatial.cKDTree(voronoi_points).query(
                material_points, k=1
            )

        return self.create_fields({label: point_regions})

    def assign_random_orientations(
        self,
        region_label="region",
        orientation_label="orientation",
        rng=np.random.default_rng(),
    ):
        """
        Assign random crystallographic orientations to regions.

        Parameters
        ----------
        region_label : str, default "region"
            Name of the field containing region IDs.
        orientation_label : str, default "orientation"
            Name for the new orientation field.
        rng : numpy.random.Generator
            Random number generator.

        Returns
        -------
        Material
            New material with random orientations assigned to regions.
        """
        unique_regions = self.fields[region_label].unique()
        num_regions = len(unique_regions)
        orientations = Orientation.random(num=num_regions, rng=rng)
        regional_field = {region_label: unique_regions, orientation_label: orientations}
        return self.create_regional_fields(
            region_label,
            pd.DataFrame(regional_field).sort_values(
                by=region_label, ignore_index=True
            ),
        )

    def insert_feature(self, feature, fields):
        """
        Insert field values into points inside a geometric feature.

        Parameters
        ----------
        feature : Feature
            Geometric feature object defining the region.
        fields : dict
            Dictionary of field_name: value pairs to insert.

        Returns
        -------
        Material
            New material with field values inserted in the feature region.
        """
        is_inside = feature.check_inside(self.fields.x, self.fields.y, self.fields.z)
        new_fields = {}
        for label, values in fields.items():
            new_values = self.extract(label)
            new_values[is_inside] = values
            if isinstance(new_values, np.ndarray) and len(new_values.shape) > 1:
                new_fields[label] = new_values.tolist()
            else:
                new_fields[label] = new_values
        return self.create_fields(new_fields)

    def remove_field(self, field_label, in_regional_field=None):
        """
        Remove a field from the material.

        Parameters
        ----------
        field_label : str
            Name of the field to remove.
        in_regional_field : str, optional
            Name of regional field if removing from regional fields.

        Returns
        -------
        Material
            New material with the specified field removed.
        """
        material = self.copy()
        if in_regional_field is not None:
            material._regional_fields[in_regional_field] = material._regional_fields[
                in_regional_field
            ].drop(field_label, axis=1)
        elif field_label in list(self.fields):
            material.fields = self.fields.drop(field_label, axis=1)
            if field_label in self._regional_fields.keys():
                del material._regional_fields[field_label]
        return material

    def create_regional_fields(self, region_label, regional_fields):
        """
        Create fields that vary by region rather than by point.

        Parameters
        ----------
        region_label : str
            Name of the field containing region IDs.
        regional_fields : dict or DataFrame
            Regional field data with region_label as key column.

        Returns
        -------
        Material
            New material with regional fields added.
        """
        regional_fields = pd.DataFrame(regional_fields)
        if regional_fields[region_label].duplicated().any():
            raise ValueError(
                f"Could not create regional field: {region_label} has non-unique values in regional field"
            )
        material = self.copy()
        if region_label in self._regional_fields:
            # merge with existing regional fields and overwrite any duplicated fields
            old_df = material._regional_fields[region_label].copy()
            old_regions = np.sort(old_df[region_label].to_numpy())
            new_regions = np.sort(regional_fields[region_label].to_numpy())
            if not np.array_equal(old_regions, new_regions):
                raise ValueError(
                    f"Values of {region_label} do not match between new and existing regional field"
                )
            regional_fields = (
                old_df[[region_label]]
                .merge(regional_fields, on=region_label, how="left")
                .combine_first(old_df)
            )
        elif region_label not in list(self.fields):
            raise ValueError(
                f"Could not create regional field: {region_label} is not a field"
            )
        # make sure merges won't produce any NaNs
        try:
            data_check = material.fields.merge(
                regional_fields,
                on=region_label,
                how="left",
                suffixes=(False, False),
                indicator=True,
            )
        except ValueError:
            raise ValueError(
                f"Could not create regional field: the provided regional fields include a field that already exists in the Material"
            )
        if (data_check["_merge"] == "left_only").any():
            missing_keys = (
                data_check.loc[data_check["_merge"] == "left_only", region_label]
                .unique()
                .tolist()
            )
            raise ValueError(
                f"Values of {region_label} not found in regional field: {missing_keys}"
            )
        material._regional_fields[region_label] = regional_fields
        return material

    def extract_regional_field(self, region_label, field_label=None):
        """
        Extract regional field data.

        Parameters
        ----------
        region_label : str
            Name of the regional field.
        field_label : str, optional
            Specific field within the regional data to extract.

        Returns
        -------
        DataFrame or array
            Regional field data.
        """
        if field_label is None:
            return self._regional_fields[region_label]
        else:
            data = self._regional_fields[region_label][field_label].to_list()
            try:
                result = type(data[0]).from_list(data)
            except AttributeError:
                result = data
            return result

    def get_region_volume_fractions(self, region_label="region"):
        """
        Calculate volume fraction of each region.

        Parameters
        ----------
        region_label : str, default "region"
            Name of the field containing region IDs.

        Returns
        -------
        dict
            Dictionary mapping region ID to volume fraction.
        """
        features = self.fields[region_label].to_numpy()
        unique_features, points_per_feature = np.unique(features, return_counts=True)
        return dict(zip(unique_features, points_per_feature / self.num_points))

    def get_region_indices(self, region_label="region"):
        """
        Get point indices for each region.

        Parameters
        ----------
        region_label : str, default "region"
            Name of the field containing region IDs.

        Returns
        -------
        dict
            Dictionary mapping region ID to list of point indices.
        """
        regions = self.fields[region_label]
        return {
            region: indices.tolist()
            for region, indices in regions.groupby(regions).groups.items()
        }

    def plot(
        self,
        label,
        component=None,
        kind="voxel",
        colormap="coolwarm",
        show_grid=False,
        show_edges=False,
        color_lims=None,
        opacity=1.0,
    ):
        """
        Plot a field using PyVista visualization.

        Parameters
        ----------
        label : str
            Name of the field to plot.
        component : int or list, optional
            Component(s) to plot for multi-component fields.
        kind : str, default "voxel"
            Plot type: "voxel", "voxelnode", "point", or "ipf_map".
        colormap : str, default "coolwarm"
            Colormap name.
        show_grid : bool, default False
            Whether to show grid lines.
        show_edges : bool, default False
            Whether to show voxel edges.
        color_lims : tuple, optional
            Color scale limits (min, max).
        opacity : float, default 1.0
            Transparency level.
        """
        fields = self.get_fields().sort_values(by=["z", "y", "x"])

        # Determine slices to grab components of the field
        slices = [slice(None)]
        if component is not None:
            component = [component] if not isinstance(component, list) else component
            for c in component:
                slices.append(slice(c, c + 1))
        slices = tuple(slices)

        if label not in list(fields):
            raise TypeError(f"{label} not found in fields")

        data = fields[label].to_list()
        if isinstance(data[0], Order2SymmetricTensor):
            result = type(data[0]).from_list(data).stress_voigt
        elif isinstance(data[0], Scalar) or isinstance(data[0], Vector):
            result = type(data[0]).from_list(data).components
        else:
            result = np.array(data)
        plot_array = np.squeeze(result[slices])
        if len(plot_array.shape) > 1 and kind.lower() != "ipf_map":
            raise ValueError(
                "Tried to plot a field with multiple dimensions. "
                + "You may need to specify a component."
            )

        # Material points are displayed as voxel centroid (cell) values
        if kind.lower() == "voxel":
            grid = pv.ImageData()
            grid.dimensions = self.dimensions + 1
            grid.origin = list(self.origin - self.spacing / 2)
            grid.spacing = self.spacing
            grid.cell_data[label] = plot_array
            grid.plot(
                cmap=colormap,
                clim=color_lims,
                show_edges=show_edges,
                show_grid=show_grid,
                scalar_bar_args=dict(vertical=True, interactive=True),
                opacity=opacity,
            )

        # Material points are displayed as voxel node values
        elif kind.lower() == "voxelnode":
            grid = pv.ImageData()
            grid.dimensions = self.dimensions
            grid.origin = self.origin
            grid.spacing = self.spacing
            grid.point_data[label] = plot_array
            grid.plot(
                cmap=colormap,
                clim=color_lims,
                show_edges=show_edges,
                show_grid=show_grid,
                scalar_bar_args=dict(vertical=True, interactive=True),
                opacity=opacity,
            )

        # Material points are displayed as a point cloud
        elif kind.lower() == "point":
            point_cloud = pv.PolyData(
                fields[["x", "y", "z"]].to_numpy(dtype=np.float32)
            )
            point_cloud[label] = plot_array
            point_cloud.plot(
                render_points_as_spheres=True,
                cmap=colormap,
                clim=color_lims,
                show_grid=show_grid,
                scalar_bar_args=dict(vertical=True, interactive=True),
                opacity=opacity,
            )

        elif kind.lower() == "ipf_map":
            grid = pv.ImageData()
            grid.dimensions = self.dimensions + 1
            grid.origin = list(self.origin - self.spacing / 2)
            grid.spacing = self.spacing
            grid["colors"] = plot_array
            grid.plot(scalars="colors", rgb=True)
        else:
            raise ValueError(f"{kind} is not a valid plot kind")

    @staticmethod
    def _get_cropped_fields(fields, points_above):
        """Filter fields to keep only points below specified indices."""
        return fields.query(
            f"x_id <= {points_above[0]} and y_id <= {points_above[1]} and z_id <= {points_above[2]}"
        )

    def crop_by_range(self, x_range=None, y_range=None, z_range=None):
        """
        Crop the material by coordinate ranges. The returned material will include points at both
        endpoints of the provided ranges (i.e., the endpoints are inclusive).

        Parameters
        ----------
        x_range, y_range, z_range : tuple, optional
            Coordinate ranges (min, max) for each direction.

        Returns
        -------
        Material
            Cropped material.
        """
        fields = self.fields.copy()
        x_range = (self.origin[0], np.inf) if x_range is None else x_range
        y_range = (self.origin[1], np.inf) if y_range is None else y_range
        z_range = (self.origin[2], np.inf) if z_range is None else z_range
        fields = fields.query(
            f"x >= {x_range[0]} and x <= {x_range[1]} and y >= {y_range[0]} and y <= {y_range[1]} and z >= {z_range[0]} and z <= {z_range[1]}"
        )
        dimensions = [
            fields.x_id.max() - fields.x_id.min() + 1,
            fields.y_id.max() - fields.y_id.min() + 1,
            fields.z_id.max() - fields.z_id.min() + 1,
        ]
        origin = np.array([fields.x.min(), fields.y.min(), fields.z.min()])
        new_material = Material(
            dimensions=dimensions,
            origin=origin,
            spacing=self.spacing,
            fields=fields.drop(columns=["x_id", "y_id", "z_id"]).reset_index(drop=True),
        )
        for k, v in self._regional_fields.items():
            new_material = new_material.create_regional_fields(k, v)
        return new_material

    def crop_by_id_range(self, x_id_range=None, y_id_range=None, z_id_range=None):
        """
        Crop the material by point ID ranges. The returned material will include points at both
        endpoints of the provided ranges (i.e., the endpoints are inclusive).

        Parameters
        ----------
        x_id_range, y_id_range, z_id_range : tuple, optional
            Point ID ranges (min, max) for each direction.

        Returns
        -------
        Material
            Cropped material.
        """
        fields = self.fields.copy()
        x_id_range = (fields.x_id.min(), np.inf) if x_id_range is None else x_id_range
        y_id_range = (fields.y_id.min(), np.inf) if y_id_range is None else y_id_range
        z_id_range = (fields.z_id.min(), np.inf) if z_id_range is None else z_id_range
        fields = fields.query(
            f"x_id >= {x_id_range[0]} and x_id <= {x_id_range[1]} and y_id >= {y_id_range[0]} and y_id <= {y_id_range[1]} and z_id >= {z_id_range[0]} and z_id <= {z_id_range[1]}"
        )
        dimensions = [
            fields.x_id.max() - fields.x_id.min() + 1,
            fields.y_id.max() - fields.y_id.min() + 1,
            fields.z_id.max() - fields.z_id.min() + 1,
        ]
        origin = np.array([fields.x.min(), fields.y.min(), fields.z.min()])
        new_material = Material(
            dimensions=dimensions,
            origin=origin,
            spacing=self.spacing,
            fields=fields.drop(columns=["x_id", "y_id", "z_id"]).reset_index(drop=True),
        )
        for k, v in self._regional_fields.items():
            new_material = new_material.create_regional_fields(k, v)
        return new_material

    def chop_by_point_count(self, x=None, y=None, z=None):
        """
        Create a subset by removing points from domain boundaries.

        Parameters
        ----------
        x, y, z : tuple, optional
            Number of points to remove (min_side, max_side) in each direction.

        Returns
        -------
        Material
            New material with boundary points removed.
        """

        # Filter the fields in prescribed coordinate ranges
        fields = deepcopy(self.fields)

        # Set the number of points to chop to zero if arguments are None
        x = (0, 0) if x is None else x
        y = (0, 0) if y is None else y
        z = (0, 0) if z is None else z
        chopped_range = {
            "x_id": (fields.x_id.min() + x[0], fields.x_id.max() - x[1]),
            "y_id": (fields.y_id.min() + y[0], fields.y_id.max() - y[1]),
            "z_id": (fields.z_id.min() + z[0], fields.z_id.max() - z[1]),
        }
        mask = np.array(
            [True] * self.num_points
        )  # repeated to handle the no argument case
        for label, chopped_range in chopped_range.items():
            if chopped_range is not None:
                mask = (
                    mask
                    & (fields[label] >= chopped_range[0])
                    & (fields[label] <= chopped_range[1])
                )

        fields = fields.loc[mask].reset_index(drop=True)

        # Generate a new fieldless submaterial
        material = Material(
            dimensions=list(
                fields[["x_id", "y_id", "z_id"]].max()
                - fields[["x_id", "y_id", "z_id"]].min()
                + 1
            ),
            origin=list(fields[["x", "y", "z"]].min()),
            spacing=self.spacing,
            fields=fields.drop(columns=["x", "y", "z", "x_id", "y_id", "z_id"]),
        )
        return material

    def export_to_vtk(self, output="fields.vtk", labels=None):
        """
        Export material data to VTK format file.

        Parameters
        ----------
        output : str, default "fields.vtk"
            Output file path.
        labels : list, optional
            Specific field labels to export. If None, exports all fields.
        """
        if labels is None:
            fields = self.get_fields().sort_values(by=["z", "y", "x"])
        else:
            fields = self.get_fields()[labels].sort_values(by=["z", "y", "x"])

        output_text = (
            "# vtk DataFile Version 2.0\n"
            + "Material Export\n"
            + "ASCII\n"
            + "DATASET STRUCTURED_POINTS\n"
            + f"DIMENSIONS {self.dimensions[0] + 1} {self.dimensions[1] + 1} {self.dimensions[2] + 1}\n"
            + "ASPECT_RATIO 1 1 1\n"
            + "ORIGIN 0 0 0\n"
            + f"CELL_DATA {len(fields)}\n"
        )

        for label in fields.columns:
            output_text += (
                f"SCALARS {label} float\n"
                + "LOOKUP_TABLE default\n"
                + "\n".join(fields[label].astype(str))
                + "\n"
            )

        with open(output, "w") as output_file:
            output_file.write(output_text)

    def export_to_evpfft(
        self,
        euler_angles_labels=["euler_angles_1", "euler_angles_2", "euler_angles_3"],
        feature_label="feature",
        phase_label="phase",
        output="fields.txt",
        euler_angles_to_degrees=False,
    ):
        """
        Export material data for EVP-FFT crystal plasticity solver.

        Parameters
        ----------
        euler_angles_labels : list, default ["euler_angles_1", "euler_angles_2", "euler_angles_3"]
            Names of fields containing Bunge Euler angles.
        feature_label : str, default "feature"
            Name of field containing feature/grain IDs.
        phase_label : str, default "phase"
            Name of field containing phase IDs.
        output : str, default "fields.txt"
            Output file path.
        euler_angles_to_degrees : bool, default False
            Whether to convert Euler angles from radians to degrees.
        """
        valid_dimensions = np.array(
            [power_of_two_below(dim) for dim in self.dimensions]
        )
        fields = self.get_fields()

        if not np.array_equal(valid_dimensions, self.dimensions):
            # Going to force a crop out of points above powers of two dimensions in a hidden way for now
            fields = self._get_cropped_fields(fields, points_above=valid_dimensions - 1)

        unit_factor = 180.0 / np.pi if euler_angles_to_degrees else 1.0

        export_labels = [
            euler_angles_labels[0],
            euler_angles_labels[1],
            euler_angles_labels[2],
            "x_id",
            "y_id",
            "z_id",
            feature_label,
            phase_label,
        ]
        fields.assign(
            euler_angles_1=fields.euler_angles_1 * unit_factor,
            euler_angles_2=fields.euler_angles_2 * unit_factor,
            euler_angles_3=fields.euler_angles_3 * unit_factor,
            x_id=fields.x_id + 1,
            y_id=fields.y_id + 1,
            z_id=fields.z_id + 1,
        ).sort_values(by=["z", "y", "x"]).to_csv(
            output, header=False, sep=" ", index=False, columns=export_labels
        )


class Feature:
    """
    Abstract base class for geometric features used to define regions in materials.

    Features are used with Material.insert_feature() to assign properties to
    specific geometric regions.
    """

    @abstractmethod
    def check_inside(self):
        """Check if points are inside the feature geometry."""
        raise NotImplementedError


class Sphere(Feature):
    """
    Spherical feature for defining spherical regions.

    Parameters
    ----------
    radius : float
        Radius of the sphere.
    centroid : array-like
        Center coordinates [x, y, z] of the sphere.
    """

    def __init__(self, radius, centroid):
        self.radius = radius
        self.centroid = centroid

    def check_inside(self, x, y, z):
        """
        Check if points are inside the sphere.

        Parameters
        ----------
        x, y, z : array-like
            Point coordinates to check.

        Returns
        -------
        array of bool
            True for points inside the sphere.
        """
        c = self.centroid
        return (x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2 <= self.radius**2


class Superellipsoid(Feature):
    """
    Superellipsoid feature for defining various rounded shapes.

    Parameters
    ----------
    major_radius : float
        Semi-axis length in the major direction.
    intermediate_radius : float
        Semi-axis length in the intermediate direction.
    minor_radius : float
        Semi-axis length in the minor direction.
    shape_exponent : float
        Exponent controlling shape (2.0 = ellipsoid, >2 = box-like, <2 = diamond-like).
    centroid : array-like
        Center coordinates [x, y, z] of the superellipsoid.
    """

    def __init__(
        self, major_radius, intermediate_radius, minor_radius, shape_exponent, centroid
    ):
        self.major_radius = major_radius
        self.intermediate_radius = intermediate_radius
        self.minor_radius = minor_radius
        self.shape_exponent = shape_exponent
        self.centroid = centroid

    def check_inside(self, x, y, z):
        """
        Check if points are inside the superellipsoid.

        Parameters
        ----------
        x, y, z : array-like
            Point coordinates to check.

        Returns
        -------
        array of bool
            True for points inside the superellipsoid.
        """
        a, b, c, n, o = (
            self.major_radius,
            self.intermediate_radius,
            self.minor_radius,
            self.shape_exponent,
            self.centroid,
        )
        return (
            abs((x - o[0]) / a) ** n
            + abs((y - o[1]) / b) ** n
            + abs((z - o[2]) / c) ** n
            - 1
            <= 0
        )


class Box(Feature):
    """
    Rectangular box feature for defining box-shaped regions.

    Parameters
    ----------
    min_corner : array-like, default [-inf, -inf, -inf]
        Minimum corner coordinates [x, y, z] of the box.
    max_corner : array-like, default [inf, inf, inf]
        Maximum corner coordinates [x, y, z] of the box.
    """

    def __init__(
        self,
        min_corner=np.array([-np.inf, -np.inf, -np.inf]),
        max_corner=np.array([np.inf, np.inf, np.inf]),
    ):
        self.min_corner = np.array(
            [
                coordinate if coordinate is not None else -np.inf
                for coordinate in min_corner
            ]
        )
        self.max_corner = np.array(
            [
                coordinate if coordinate is not None else np.inf
                for coordinate in max_corner
            ]
        )

    def check_inside(self, x, y, z):
        """
        Check if points are inside the box.

        Parameters
        ----------
        x, y, z : array-like
            Point coordinates to check.

        Returns
        -------
        array of bool
            True for points inside the box.
        """
        min_x, min_y, min_z = self.min_corner
        max_x, max_y, max_z = self.max_corner
        return np.logical_and.reduce(
            [min_x <= x, x <= max_x, min_y <= y, y <= max_y, min_z <= z, z <= max_z]
        )
