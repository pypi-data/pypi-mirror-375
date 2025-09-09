"""Item module.

Module to create ``Item`` instances.

Any object from an Ansys Dynamic Reporting database can be represented
as an ``Item`` instance. This class allows for easy creation and manipulation
of such objects.

Examples
--------
::

    import ansys.dynamicreporting.core as adr
    adr_service = Service()
    ret = adr_service.connect()
    my_img = adr_service.create_item()
    my_img.item_image = 'Image_to_push_on_report'

"""
import os.path
import requests
import sys
from typing import Optional

from .adr_utils import in_ipynb, table_attr, type_maps
from .utils.report_utils import PIL_image_to_data
import webbrowser

try:
    from IPython.display import IFrame
except ImportError:
    pass


# Generate the items for the ADR database
class Item:

    """Provides for creating an object that represents an Ansys Dynamic Reporting item.

    Create an instance of this class for each item in the database that you want to
    interact with. When the object is created, no type is set. The type, determined the
    first time that you set the ``item_*`` attribute, cannot be changed.

    This code creates an instance with the object ``my_txt`` as a text item:

    >>> my_txt = adr_service.create_item()
    >>> my_txt.item_text = '<h1>The test</h1>This is a text item'


    The type of the item created in the preceding code cannot be changed. However,
    the attributes describing the object can be reset at any time. These changes are
    automatically propagated into the database. The attributes described in the
    following "Parameters" section can be used to control the rendering of these objects.

    .. note::
       These attributes mirror the generic data item attributes described in
       `Data Items`_ in the documentation for Ansys Dynamic Reporting.

    .. _Data Items: https://nexusdemo.ensight.com/docs/html/Nexus.html?DataItems.html

    Parameters
    ----------
    service : ansys.dynamicreporting.core.Service, optional
        Ansys Dynamic Reporting object that provides the connection to the database
        that the item is to interact with. The default is ``None``.
    obj_name : str, optional
        Name of the item object in the database. The default is ``default``.
    source : str, optional
        Name of the source for the item in the database. The default is ``"ADR"``.


    Examples
    --------
    Initialize the ``Service`` class inside an Ansys Dynamic Reporting service and
    create an object as a text item::

        import ansys.dynamicreporting.core as adr
        adr_service = adr.Service(ansys_installation = r'C:\\Program Files\\ANSYS Inc\\v232')
        adr_service.connect(url='http://localhost:8010')
        my_txt = adr_service.create_item()
        my_txt.item_text = '<h1>The test</h1>This is a text item'

    """

    def __init__(self, service: 'ADR' = None, obj_name: Optional[str] = "default",
                 source: Optional[str] = "ADR") -> None:
        self.item = None
        self.serverobj = service.serverobj
        self._url = None
        self.logger = service.logger
        self.source = source
        self.obj_name = str(obj_name)
        self.type = None
        self.item_text = ""
        """Text (HTML and LaTeX formatting)"""
        self.item_image = None
        """Image object (Image and PNG binary files)"""
        self.item_scene = None
        """3D scene (AVZ, PLY, SCDOC, SCDOCX, GLB, and STL files)"""
        self.item_animation = None
        """Animation file (MP4/H.264 format files)"""
        # Attributes for the table items
        self.table_attr = table_attr
        self.item_table = None
        """Table values (Must be in a numpy array)"""
        self.table_dict = {}
        self.format = None
        """Number format

        scientific sigfigsX floatdotX str date_XY"""
        self.format_column = None
        """Column labels format

        format for column labels scientific sigfigsX floatdotX str date_XY"""
        self.labels_column = None
        """Column labels

        column A column B"""
        self.format_row = None
        """Row labels format

        format for row labels scientific sigfigsX floatdotX str date_XY"""
        self.labels_row = None
        """Row labels

        row 1 row 2"""
        self.plot = None
        """Table display style

        table bar line pie heatmap parallel sankey 3d surface polar"""
        self.title = None
        """Common title

        """
        self.line_color = None
        """Linebarhistogrampiemarker colors

        #rrggbb #rgb @rownamenumber hexadecimal digits: #8b783f"""
        self.line_marker = None
        """Markers

        circle square cross x triangle star diamond hash plus times open dot"""
        self.line_marker_text = None
        """Marker text

        Value={{vx}} Position={{vy}}"""
        self.marker_text_rowname = None
        """Marker text row name

        Should the row name be appended to the marker text: 0|1|undefined"""
        self.line_marker_size = None
        """Marker size

        The marker size in points"""
        self.line_marker_opacity = None
        """Marker opacity

        The opacity of the line marker. Default: 1.0"""
        self.line_marker_scale = None
        """Marker scaling

        Apply a linear transform to marker sizes M B = Minput_sizeB. Example: 1. 0."""
        self.line_error_bars = None
        """Error bars

        Scalar value or name of a row with size of error bars in Y axis units. May be a list."""
        self.line_marker_aux0 = None
        """Auxiliary data 0

        Scalar value or name of a row accessible to line_marker_text as vaux0. May be a list."""
        self.line_marker_aux1 = None
        """Auxiliary data 1

        Scalar value or name of a row accessible to line_marker_text as vaux1. May be a list."""
        self.line_marker_aux2 = None
        """Auxiliary data 2

        Scalar value or name of a row accessible to line_marker_text as vaux2. May be a list."""
        self.line_marker_aux3 = None
        """Auxiliary data 3

        Scalar value or name of a row accessible to line_marker_text as vaux3. May be a list."""
        self.line_marker_aux4 = None
        """Auxiliary data 4

        Scalar value or name of a row accessible to line_marker_text as vaux4. May be a list."""
        self.line_marker_aux5 = None
        """Auxiliary data 5

        Scalar value or name of a row accessible to line_marker_text as vaux5. May be a list."""
        self.line_marker_aux6 = None
        """Auxiliary data 6

        Scalar value or name of a row accessible to line_marker_text as vaux6. May be a list."""
        self.line_marker_aux7 = None
        """Auxiliary data 7

        Scalar value or name of a row accessible to line_marker_text as vaux7. May be a list."""
        self.line_marker_aux8 = None
        """Auxiliary data 8

        Scalar value or name of a row accessible to line_marker_text as vaux8. May be a list."""
        self.line_marker_aux9 = None
        """Auxiliary data 9

        Scalar value or name of a row accessible to line_marker_text as vaux9. May be a list."""
        self.column_minimum = None
        """Column range minimums

        Scalar value or array of values used as column category minimums."""
        self.column_maximum = None
        """Column range maximums

        Scalar value or array of values used as column category maximums."""
        self.line_style = None
        """Line styling

        none solid dot dash longdash dashdot longdashdot"""
        self.line_width = None
        """Line width

        The line width in pixels"""
        self.stacked = None
        """Bar chart stacking Deprecated

        1=stack the bar charts This is a deprecated property  please use bar_mode instead."""
        self.bar_mode = None
        """Bar chart  Histogram config mode

        group=separate the barsbins  stack=stack the barsbins  overlay=overlay the barbins"""
        self.xaxis = None
        """X axis rows

        The row numbersnames to use as the X axis values. Example: 2 Distance"""
        self.yaxis = None
        """Y axis rows

        The row numbersnames to use as the Y axis values. Example: 0 Pressure"""
        self.zaxis = None
        """Z axis rows

        The row numbersnames to use as the Z axis values. Example: 3 Pressure"""
        self.palette = None
        """Color palette

        The name of the color palette to use with line_color row data. =invert. Example: Hot"""
        self.palette_position = None
        """Position of the colorbar

        Position the colorbar center relative to plot bounds 0 1. Example on left: 0.2 0.5"""
        self.palette_range = None
        """Range of the colorbar

        Minimum and maximum line_color values  mapped to palette extremes. Example: 0 100"""
        self.palette_show = None
        """Colorbar display

        Showhide the colorbar with the values 10. Example: 1"""
        self.palette_title = None
        """Colorbar title string

        String draw to the right of the colorbar as a title. Default: none"""
        self.histogram_threshold = None
        """Histogram rendering threshold

        The threshold for data table columns to render as histogram. Default: 50"""
        self.histogram_cumulative = None
        """Cumulative histogram

        Set to 1 to cumulate the histograms. Default: 0"""
        self.histogram_normalized = None
        """Normalize histogram

        Set to 1 to normalize the histograms. Default: 0"""
        self.histogram_bin_size = None
        """Histogram bin size

        The bin size of the histogram. Accepts positive integer or float types"""
        self.bar_gap = None
        """Bar charts bar gap

        The bar gap of the bar chart float type. Range: 0  1"""
        self.width = None
        """Chart width

        Chart width in pixels"""
        self.height = None
        """Chart height

        Chart height in pixels"""
        self.show_legend = None
        """Show legend

        Set to 0 to hide the legend. Default: 1"""
        self.legend_position = None
        """Position the legend

        Position the legend relative to plot bounds 0 1.  Example on right: 1.2 0.5"""
        self.show_legend_border = None
        """Show legend border

        Set to 1 to display a border around the legend. Default: 0"""
        self.show_border = None
        """Show plot border

        Set to 1 to show the plot border. Default: 0"""
        self.plot_margins = None
        """Plot margins

        Adjust plot margin sizes in pixels: left top right bottom Example: default  default  5 
        default"""
        self.plot_title = None
        """Plot title

        The title of the plot"""
        self.plot_xaxis_type = None
        """X axis style

        linear log"""
        self.plot_yaxis_type = None
        """Y axis style

        linear log"""
        self.plot_zaxis_type = None
        """Z axis style

        linear log"""
        self.xrange = None
        """X axis range

        The range for the x axis. Example: 0.  10."""
        self.yrange = None
        """Y axis range

        The range for the y axis. Example: 0.  10."""
        self.zrange = None
        """Z axis range

        The range for the z axis. Example: 0.  10."""
        self.xaxis_format = None
        """X axis text format

        Format for the x axis tick labels. Example: floatdot2"""
        self.yaxis_format = None
        """Y axis text format

        Format for the y axis tick labels. Example: floatdot2"""
        self.zaxis_format = None
        """Z axis text format

        Format for the z axis tick labels. Example: floatdot2"""
        self.xtitle = None
        """X axis title

        A title for the x axis"""
        self.ytitle = None
        """Y axis title

        A title for the y axis"""
        self.ztitle = None
        """Z axis title

        A title for the z axis"""
        self.xaxis_tick_delta = None
        """X axis tick delta

        The delta between xradial axis ticks"""
        self.yaxis_tick_delta = None
        """Y axis tick delta

        The delta between yangular axis ticks"""
        self.zaxis_tick_delta = None
        """Z axis tick delta

        The delta between z axis ticks"""
        self.item_justification = None
        """Table item justification

        left  center or right. By default  there will be no justification."""
        self.nan_display = None
        """NaN table display value

        The string to be displayed for a NaN value. Default: NaN"""
        self.table_sort = None
        """Table sorting

        Allow column sorting from headers: none  all  data  Default: all"""
        self.table_title = None
        """Table title

        The title of the table"""
        self.align_column = None
        """Column value alignment

        Alignment of data values in each column left right center justify"""
        self.table_search = None
        """Search values

        Visibility of table value search field.  Default: 0"""
        self.table_page = None
        """Table paging

        Number of rows visible per page.  Default: 0 all"""
        self.table_pagemenu = None
        """Table paging menu

        Options for the number of rows per page menu.  Default: 10  25  50  100  1"""
        self.table_scrollx = None
        """Horizontal scrolling

        Control visibility of horizontal scrollbar.  Default: 1"""
        self.table_scrolly = None
        """Vertical scrolling

        Control visibility and height of vertical scrollbar.  Height in points  Default: 0"""
        self.table_bordered = None
        """Table bordering

        Control visibility of table borders.  Default: 1"""
        self.table_condensed = None
        """Table compactness

        Control compactness of table.  Default: 0"""
        self.table_wrap_content = None
        """Table content wrapping

        Control wrapping of content to the next line inside a table cell.  Default: 0"""
        self.table_default_col_labels = None
        """Default column labels

        Enabledisable default column labels.  Default: 1"""
        self.table_cond_format = None
        """Table conditional formatting

        Specify conditional formatting rules for table cell formatting."""
        self.row_tags = []
        """List of tags for each table row"""
        self.col_tags = []
        """List of tags for each table column"""
        self.item = self.serverobj.create_item(name=self.obj_name, source=self.source)

    @property
    def url(self):
        """URL corresponding to the item"""
        if self.serverobj.get_URL() is not None and self.item.guid is not None:
            self._url = self.serverobj.get_URL() + "/reports/report_display/?usemenus=off&query=A%7Ci_guid%7Ceq%7C"
            self._url += str(self.item.guid)
        else:
            self._url = None
        return self._url

    def __pushonly__(self):
        """
        Push self to the server - with server existence check
        """
        ret = 0
        if self._url is None:
            _ = self.url
        if self.serverobj is not None:
            ret = self.serverobj.put_objects([self.item])
        else:
            self.logger.error("No connection to service established")
        return ret

    def __push__(self, value):
        if self.type == "text":
            self.item.set_payload_html(value)
        elif self.type == "image":
            # If the image is passed as a file, first open it. Otherwise, directly
            # pass it as a payload value
            if os.path.exists(value):
                # if PNG image, then simply read it.
                if value.capitalize().endswith('png'):
                    with open(value, "rb") as fb:
                        img = fb.read()
                if value.capitalize().endswith(('jpg', 'jpeg', 'tiff', 'tif')):
                # If jpg or tiff, then convert to png buffer first
                    tmp_img = PIL_image_to_data(value)
                    img = tmp_img['file_data']
            else:
                img = value
            self.item.set_payload_image(img)
        elif self.type == "scene":
            self.item.set_payload_scene(value)
        elif self.type == "table":
            self.item.set_payload_table(self.table_dict)
        elif self.type == "animation":
            self.item.set_payload_animation(value)
        elif self.type == "file":
            self.item.set_payload_file(value)
        elif self.type == "tree":
            self.item.set_payload_tree(value)
        _ = self.__pushonly__()

    def __setattr__(self, name, value, only_set=False):
        # If only_set is set to True, then skip the push methods. This is needed when using the
        # setattr to create Item objs that correspond to what is in the database, but
        # not to actually push changes to the database items - for example, when querying it
        if name == "item":
            super().__setattr__(name, value)
            return 0
        if self.item is None:
            super().__setattr__(name, value)
            return 0
        if name in type_maps:
            if self.type is None:
                self.type = type_maps[name]
            if self.type != type_maps[name]:
                self.logger.error(f"Can not set {name} on an item of type: {self.type}")
                return -1
            if name == "item_table":
                self.table_dict["array"] = value
            if only_set is False:
                self.__push__(value)
        if name in self.table_attr:
            if self.type == "table":
                if value is not None:
                    self.table_dict[name] = value
                    if "array" in self.table_dict.keys():
                        if only_set is False:
                            self.__push__(value)
        super().__setattr__(name, value)
        return 0

    def __copyattrs__(self, dataitem=None):
        """
        Copy the attributes from a data Item into the current Item
        This is useful in the query method when creating a Item that corresponds to an existing
        DataItem

        Parameters
        ----------
        dataitem : utils.report_objects.ItemREST
            ADR item to copy from. Default: None
        """
        if dataitem is None:
            return
        if dataitem.type == "table":
            for t_attr in self.table_attr:
                self.__setattr__(t_attr, dataitem.payloaddata.get(t_attr, None), only_set=True)

    def visualize(self, new_tab: Optional[bool] = False) -> None:
        """Render this item only.

        Parameters
        ----------
        new_tab : bool, optional
            Whether to render the item in a new tab if the current environment is a Jupyter
            notebook. The default is ``False``, in which case the item is rendered in the
            current location. If the environment is not a Jupyter notebook, the item is
            always rendered in a new tab.

        Returns
        -------
        Item
            Rendered item.

        Examples
        --------
        Create a text item and render it in a new tab::

            import ansys.dynamicreporting.core as adr
            adr_service = adr.Service(ansys_installation = r'C:\\Program Files\\ANSYS Inc\\v232')
            ret = adr_service.connect(url='http://localhost:8010')
            my_txt = adr_service.create_item()
            my_txt.item_text = '<h1>The test</h1>This is a text item'
            my_txt.visualize(new_tab = True)


        """
        if in_ipynb() and not new_tab:
            iframe = self.get_iframe()
            if iframe is not None:
                display(iframe)
            else: # pragma: no cover
                self.logger.error("Could not generate an IFrame")
        else:
            if self._url is None: # pragma: no cover
                self.logger.error("Could not obtain a url")
            else:
                webbrowser.open_new(self._url)

    def get_iframe(self, width=0, height=0):
        """Get the iframe object corresponding to the item.

        Parameters
        ----------
        width : int, optional
            Width of the iframe object. The default is ``min(Item width * 1,1, 1000)``.
            For example, if the item width is ``0``, the default is ``1000``.
        height : int, optional
            Height of the iframe object. The default is ``min(Item height, fixed height)``,
            where the fixed height is ``800`` for an item scene and ``400`` otherwise.

        Returns
        -------
        iframe
            iframe object corresponding to the item. If no iframe can be generated,
            ``None`` is returned.

        Examples
        --------
        ::

            import ansys.dynamicreporting.core as adr
            adr_service = adr.Service(ansys_installation = r'C:\\Program Files\\ANSYS Inc\\v232')
            ret = adr_service.connect(url='http://localhost:8010')
            my_txt = adr_service.create_item()
            my_txt.item_text = '<h1>The test</h1>This is a text item'
            item_iframe = my_txt.get_iframe()

        """
        if 'IPython.display' in sys.modules:
            if width == 0:
                if self.item.width == 0:
                    width = 1000
                else:
                    width = min(self.item.width * 1.1, 1000)
            if height == 0:
                if self.type == "scene":
                    height = 800
                else:
                    height = 400
                if self.item.height > 0:
                    height = min(self.item.height * 1.1, height)
            if self._url is None:
                _ = self.url
            iframe = IFrame(src=self._url, width=width, height=height)
        else:
            iframe = None
        return iframe

    def set_tags(self, tagstring: str = '') -> bool:
        """Set tags on the item.

        Parameters
        ----------
        tagstring : str, optional
            Tags to set on the item. Separate multiple tags with a space. The
            tag syntax is ``tagname=value``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        ::

            import ansys.dynamicreporting.core as adr
            adr_service = adr.Service(ansys_installation = r'C:\\Program Files\\ANSYS Inc\\v232')
            ret = adr_service.connect()
            my_txt = adr_service.create_item()
            my_txt.item_text = '<h1>The test</h1>This is a text item'
            my_txt.set_tags("tagone=1 tagtwo=two")

        """
        self.item.set_tags(tagstring)
        ret = self.__pushonly__()
        return ret == requests.codes.ok

    def get_tags(self) -> str:
        """Get the tags on the item.

        Returns
        -------
        str
            Tags on the item.

        Examples
        --------
        ::

            import ansys.dynamicreporting.core as adr
            adr_service = adr.Service(ansys_installation = r'C:\\Program Files\\ANSYS Inc\\v232')
            ret = adr_service.connect()
            item_list = adr_service.query()
            first_item = item_list[0]
            all_tags = first_item.get_tags()

        """
        tags = self.item.get_tags()
        return tags

    def add_tag(self, tag: str = '', value: str = '') -> bool:
        """Add a tag to the item.

        Parameters
        ----------
        tag : str, optional
            Tag name. The default is ``""``.
        value str : str, optional
            Tag value.  The default is ``""``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        ::

            import ansys.dynamicreporting.core as adr
            adr_service = adr.Service(ansys_installation = r'C:\\Program Files\\ANSYS Inc\\v232')
            ret = adr_service.connect()
            my_txt = adr_service.create_item()
            my_txt.item_text = '<h1>The test</h1>This is a text item'
            my_txt.add_tag(tag='tagone', value='one')

        """
        self.item.add_tag(tag=tag, value=value)
        ret = self.__pushonly__()
        return ret == requests.codes.ok

    def rem_tag(self, tag: str = '') -> bool:
        """Remove a tag on the item.

        Parameters
        ----------
        tag : str, optional
            Tag to remove. The default is ``""``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        ::

            import ansys.dynamicreporting.core as adr
            adr_service = adr.Service(ansys_installation = r'C:\\Program Files\\ANSYS Inc\\v232')
            ret = adr_service.connect()
            item_list = adr_service.query()
            first_item = item_list[0]
            all_tags = first_item.rem_tags(tag='tagone')

        """
        self.item.rem_tag(tag=tag)
        ret = self.__pushonly__()
        return ret == requests.codes.ok
