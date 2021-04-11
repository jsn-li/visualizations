import math
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, AutocompleteInput, Button, Text, HoverTool, MultiLine

#
# Constants needed for Jinja templating, should equal the identifiers within templates/index.html
#
TEMPLATE_PLOT_IDENTIFIER = "plot"
TEMPLATE_INPUTS_IDENTIFIER = "inputs"

#
# Default configuration values
#

# sizing stuff
DEFAULT_ASPECT_RATIO = 0.9
DEFAULT_X_RANGE = (-4, 7)
DEFAULT_Y_RANGE = (-0.075, 1.075)
DEFAULT_MIN_SPACE_X = 0.09
DEFAULT_MIN_SPACE_Y = 0.06
DEFAULT_TOTAL_DISPLAY_REGIONS = 12
DEFAULT_MIN_DISPLAY_REGIONS = 2
DEFAULT_FONT_SIZE = 16
# keys
DEFAULT_REGION_KEY = "District/County Town"
DEFAULT_PRIMARY_INCIDENCE_KEY = "New Cases in Last 14 Days"
DEFAULT_SECONDARY_INCIDENCE_KEY = "Last 7 Days"
DEFAULT_TIME_SAFE_KEY = "COVID-Free Days"
DEFAULT_POSTCODE_KEY = "Postcode"
DEFAULT_PERCENT_CHANGE_KEY = "Pct Change"
# units
DEFAULT_REGION_TYPE = "Region"
DEFAULT_TIME_SAFE_UNIT = "day"
DEFAULT_TIME_SAFE_PLURAL_UNIT = "days"
DEFAULT_INCIDENCE_UNIT = "case"
DEFAULT_INCIDENCE_PLURAL_UNIT = "cases"
DEFAULT_CALC_WITH_SECONDARY_INCIDENCE = None
# strings
DEFAULT_LAST_UPDATED_TEXT = "Last updated"
DEFAULT_LEGEND_TITLE = "Legend"
DEFAULT_SEARCHBAR_PLACEHOLDER = "Search for a region..."
DEFAULT_RESET_BUTTON_TEXT = "Reset"
DEFAULT_REGION_NAME_TOOLTIP = "Region Name"
DEFAULT_CATEGORY_TOOLTIP = "Category"
DEFAULT_REGION_CODE_TOOLTIP = "Region Code"
DEFAULT_TIME_SAFE_TOOLTIP = "COVID-Free Days"
DEFAULT_PRIMARY_INCIDENCE_TOOLTIP = "New Cases in Last 14 Days"
DEFAULT_SECONDARY_INCIDENCE_TOOLTIP = "New Cases in Last 7 Days"
DEFAULT_PERCENT_CHANGE_TOOLTIP = "Weekly Percent Change"


class VisualizationLayout:
    """ VisualizationLayout generates visualizations of the COVID ranking data. It should be served with Bokeh's
        serve command.

    Data should be input as a .pkl file. It should have the columns corresponding to the keys listed in the constants.
    The parameter defaults are set in accordance to ECV's use case and can be seen above.

    --- Required Configuration ---
    :param title is the title of the visualization
    :param pickle_file is where the .pkl file is located (this is automatically set by the pipeline, and does not need
           to be set unless running the visualization manually)
    :param labels are the phases' labels. the first element is always the "Green Zone" and is sorted in descending order
           with elements in time_safe_key.
    :param descriptions are used to display the legend
    :param lower_bounds are the lower bounds, inclusive, of the phases. an example is [0, 1, 20], where phase 1 only
           includes 0 incidence (>= 0 and < 1, phase 2 includes incidence >= 1 and < 20, etc.
           if you do not want a "Green Zone," set the first element of each labels, colors, etc. to None (~ in yaml).
    :param colors are the colors of each phase

    --- Sizing Stuff ---
    :param aspect_ratio is the width/height of the plot. the ultimate size in pixels will be determined
           by the page it is embeded on.
    :param x_range represents the range of x values represented in the plot.
           for reference, the box's width is 1 and it spans x = [0, 1]
    :param y_range represents the range of y values represented in the plot.
           for reference, the box's height is 1 and it spans y = [0, 1]
    :param min_space_x is the minimum horizontal space in between each "branched" line. it is proportional to x_range.
    :param min_space_y is the minimum vertical space in between each county's text and line elements.
           it is proportional to y_range, and should be about the height of one line of text.
    :param total_display_regions is the number of regions that appear in total (excluding searched regions).
           it will be divided proportionally among the categories, based on how many regions are in that category.
    :param min_display_regions is the minimum number of regions that will be displayed for a category (if possible)
    :param font_size is the font size, in pixels, of the text rendered on the plot

    --- Units ---
    :param region_type should describe the granularity of the input data.
           for example, input "City" for city-level data. this is used in the hover tooltips.
    :param time_safe_unit should describe the unit used to count the time a region has been "safe" (e.g. day)
    :param time_safe_plural_unit should be same as time_safe_unit but plural (e.g. days)
    :param incidence_unit should describe the unit used to represent incidence (e.g. case, case per 100,000)
    :param incidence_plural_unit should be same as incidence_unit but plural (e.g. cases, cases per 100,000)

    --- Keys ---
    :param region_key is used to access a region's name
    :param primary_incidence_key is used to access the disease incidence. incidence can be in case numbers, etc.
           the data stored under the primary key is used to calculate the phase categorizations, sorting, etc.
    :param secondary_incidence_key is used to access the disease incidence. incidence can be in case numbers, etc.
           the data stored under the secondary key is used just for display, unless you override it
    :param time_safe_key is used to access the number of days a region has been disease-free
    :param postcode_key is used to access a region's postcode
    :param percent_change_key is used to access the calculated percent change in incidence over a given timeframe
    :param calc_with_secondary_incidence is used as an override, with index i = True forcing the calculations for the
           category at index i to be done using the secondary incidence data.

    --- Strings ---
    :param last_updated_text is the label used to display the last updated date
    :param last_updated_time is the actual time that the data was last updated. This generally should not be hardcoded
           and should be dynamically set when the server launches.
    :param legend_title is the title displayed above the legend
    :param searchbar_placeholder is used as the placeholder for the region search bar
    :param reset_button_text is used as the text for the reset button
    :param region_name_tooltip is used to display the region name in the hovering tooltip
    :param category_tooltip is used to display the region's category in the hovering tooltip
    :param region_code_tooltip is used to display the region's code in the hovering tooltip
    :param time_safe_tooltip is used to display the time a region has been "safe" in the hovering tooltip
    :param primary_incidence_tooltip= is used to display incidence within one timeframe in the hovering tooltip
    :param secondary_incidence_tooltip= is used to display incidence within another timeframe in the hovering tooltip
    :param percent_change_tooltip= is used to display percent change between the timeframes in the hovering tooltip
    """

    def __init__(self, title, pickle_file, labels, descriptions, lower_bounds, colors, **kwargs):
        # Initialize required parameters
        self.title = title
        self.input_table = pd.read_pickle(pickle_file)
        self.labels = labels
        self.descriptions = descriptions
        self.lower_bounds = lower_bounds
        self.colors = colors
        self.num_categories = len(self.labels)

        # Read in kwargs
        self.__read_config__(kwargs)

        # Adjust lower bounds!
        self.lower_bounds.append(self.input_table[self.primary_incidence_key].max() + 1)

        # Initialize class members which will store calculation data
        self.ratios = []
        self.categorized_entries = []
        self.display_regions = [pd.DataFrame()] * self.num_categories
        self.sort_criterias = []
        self.criteria_units = []
        self.last_searched = ""

        # Initialize data sources used for plotting
        self.source = ColumnDataSource()
        self.searched_source = ColumnDataSource()

        self.__categorize_entries__()
        self.__calculate_ratios__()
        self.__init_sorting_criteria__()
        self.__build_display_regions__()
        self.__build_plot_data__()

    def __read_config__(self, config):
        # Initialize sizing stuff
        self.aspect_ratio = config.get("aspect_ratio", DEFAULT_ASPECT_RATIO)
        self.x_range = config.get("x_range", DEFAULT_X_RANGE)
        self.y_range = config.get("y_range", DEFAULT_Y_RANGE)
        self.min_space_x = config.get("min_space_x", DEFAULT_MIN_SPACE_X)
        self.min_space_y = config.get("min_space_y", DEFAULT_MIN_SPACE_Y)
        self.total_display_regions = config.get("total_display_regions", DEFAULT_TOTAL_DISPLAY_REGIONS)
        self.min_display_regions = config.get("min_display_regions", DEFAULT_MIN_DISPLAY_REGIONS)
        self.font_size = config.get("font_size", DEFAULT_FONT_SIZE)
        self.font_size_str = str(self.font_size) + 'px'

        # Initialize keys
        self.region_key = config.get("region_key", DEFAULT_REGION_KEY)
        self.primary_incidence_key = config.get("primary_incidence_key", DEFAULT_PRIMARY_INCIDENCE_KEY)
        self.secondary_incidence_key = config.get("secondary_incidence_key", DEFAULT_SECONDARY_INCIDENCE_KEY)
        self.time_safe_key = config.get("time_safe_key", DEFAULT_TIME_SAFE_KEY)
        self.postcode_key = config.get("postcode_key", DEFAULT_POSTCODE_KEY)
        self.percent_change_key = config.get("percent_change_key", DEFAULT_PERCENT_CHANGE_KEY)

        # Initialize unit stuff
        self.region_type = config.get("region_type", DEFAULT_REGION_TYPE)
        self.time_safe_unit = config.get("time_safe_unit", DEFAULT_TIME_SAFE_UNIT)
        self.time_safe_plural_unit = config.get("time_safe_plural_unit", DEFAULT_TIME_SAFE_PLURAL_UNIT)
        self.incidence_unit = config.get("incidence_unit", DEFAULT_INCIDENCE_UNIT)
        self.incidence_plural_unit = config.get("incidence_plural_unit", DEFAULT_INCIDENCE_PLURAL_UNIT)
        self.calc_with_secondary_incidence = config.get("calc_with_secondary_incidence", [False] * self.num_categories)

        # Initialize strings
        self.last_updated_text = config.get("last_updated_text", DEFAULT_LAST_UPDATED_TEXT)
        self.last_updated_time = config.get("last_updated_time")
        self.legend_title = config.get("legend_title", DEFAULT_LEGEND_TITLE)
        self.searchbar_placeholder = config.get("searchbar_placeholder", DEFAULT_SEARCHBAR_PLACEHOLDER)
        self.reset_button_text = config.get("reset_button_text", DEFAULT_RESET_BUTTON_TEXT)
        self.region_name_tooltip = config.get("region_name_tooltip", DEFAULT_REGION_NAME_TOOLTIP)
        self.category_tooltip = config.get("category_tooltip", DEFAULT_CATEGORY_TOOLTIP)
        self.region_code_tooltip = config.get("region_code_tooltip", DEFAULT_REGION_CODE_TOOLTIP)
        self.time_safe_tooltip = config.get("time_safe_tooltip", DEFAULT_TIME_SAFE_TOOLTIP)
        self.primary_incidence_tooltip = config.get("primary_incidence_tooltip", DEFAULT_PRIMARY_INCIDENCE_TOOLTIP)
        self.secondary_incidence_tooltip = config.get("secondary_incidence_tooltip",
                                                      DEFAULT_SECONDARY_INCIDENCE_TOOLTIP)
        self.percent_change_tooltip = config.get("percent_change_tooltip", DEFAULT_PERCENT_CHANGE_TOOLTIP)

    def __categorize_entries__(self):
        for i in range(self.num_categories):
            incidence_key = self.__get_incidence_key__(i)
            self.categorized_entries.append(
                self.input_table.loc[
                    # Add region to category if incidence is greater than or equal to the category's lower bound,
                    (self.input_table[incidence_key] >= self.lower_bounds[i]) &
                    (
                            # AND if less than the next category's lower bound,
                            (self.input_table[incidence_key] < self.lower_bounds[i + 1]) |
                            # OR, when next lower bound is equal to the current lower bound (e.g. two green zones),
                            # if equal to the next lower bound
                            ((self.lower_bounds[i] == self.lower_bounds[i + 1]) &
                             (self.input_table[incidence_key] == self.lower_bounds[i + 1]))
                    )
                    ]
            )

        # Remove regions that may fit into multiple categories, favoring the best category
        for i in reversed(range(1, self.num_categories)):
            self.categorized_entries[i] = \
                pd.merge(self.categorized_entries[i], self.categorized_entries[i - 1], indicator=True, how='outer') \
                .query('_merge=="left_only"') \
                .drop('_merge', axis=1)

    def __calculate_ratios__(self):
        num_entries = len(self.input_table)
        for i in range(self.num_categories):
            self.ratios.append(len(self.categorized_entries[i]) / num_entries)

    def __init_sorting_criteria__(self):
        for i in range(self.num_categories):
            if i == 0:
                self.sort_criterias.append(self.time_safe_key)
                self.criteria_units.append(self.time_safe_unit)
            else:
                self.sort_criterias.append(self.__get_incidence_key__(i))
                self.criteria_units.append(self.incidence_unit)

    def __get_incidence_key__(self, category_index):
        if self.calc_with_secondary_incidence[category_index]:
            return self.secondary_incidence_key
        return self.primary_incidence_key

    def __get_num_display_regions_for_category__(self, category_index):
        return max(math.floor(self.total_display_regions * self.ratios[category_index]), self.min_display_regions)

    def __build_display_regions__(self):
        for i in range(self.num_categories):
            sort_ascending = True
            if self.sort_criterias[i] == self.time_safe_key:
                sort_ascending = False

            # add top regions
            sorted_entries = self.categorized_entries[i] \
                .sort_values(by=self.sort_criterias[i], axis=0, ascending=sort_ascending)
            self.display_regions[i] = sorted_entries.head(self.__get_num_display_regions_for_category__(i))

            # replace the tail with the worst region
            if len(sorted_entries) > self.__get_num_display_regions_for_category__(i):
                self.display_regions[i] = self.display_regions[i].head(-1)
                self.display_regions[i] = self.display_regions[i].append(sorted_entries.tail(1))

    def __add_searched_region__(self, query):
        # Set last searched
        self.last_searched = query
        # Add searched region to appropriate display_regions element, then sort
        search_type = self.postcode_key if query.isnumeric() else self.region_key
        for i in range(self.num_categories):
            searched_region_entry = \
                self.categorized_entries[i][self.categorized_entries[i][search_type] == query]
            if (query != "") and \
                    (len(searched_region_entry) != 0) and \
                    (len(self.display_regions[i][self.display_regions[i][search_type] == query]) == 0):
                self.display_regions[i] = self.display_regions[i].append(searched_region_entry)
                self.display_regions[i] = self.display_regions[i] \
                    .sort_values(self.sort_criterias[i],
                                 ascending=(self.sort_criterias[i] == self.__get_incidence_key__(i)))
                break

    @staticmethod
    def __new_plot_data_map__():
        return {"line_x_points": [],
                "line_y_points": [],
                "line_color": [],
                "text_x": [],
                "text_y": [],
                "text": [],
                "region_name": [],
                "category": [],
                "postcode": [],
                "time_safe": [],
                "primary_incidence": [],
                "secondary_incidence": [],
                "percent_change": []}

    def __build_plot_data__(self):
        box_top_y = 1
        last_text_y = float('inf')
        plot_data = self.__new_plot_data_map__()
        searched_plot_data = self.__new_plot_data_map__()
        for category_i in range(len(self.ratios)):
            curr_top = self.display_regions[category_i]
            sort_criteria = self.sort_criterias[category_i]
            criteria_unit = self.criteria_units[category_i]

            box_size = self.ratios[category_i]
            if box_size == 0:
                continue

            # Iterate through each region, calculate their plot positions with padding
            # Also, process the data fields, allowing for empty defaults on the optional fields
            top_region_datum = curr_top[sort_criteria].max()
            bot_region_datum = curr_top[sort_criteria].min()
            padding = box_size * 0.1
            for region_i in range(len(curr_top[self.region_key])):
                region = curr_top[self.region_key].values[region_i]
                datum = curr_top[self.sort_criterias[category_i]].values[region_i]
                line_y_relative = ((datum - bot_region_datum) / (top_region_datum - bot_region_datum)) \
                    if top_region_datum != bot_region_datum else 0.5
                line_y = box_top_y - ((box_size - (padding * 2)) * line_y_relative) - padding

                # Calculate necessary vertical adjustments to line and text
                text_y = line_y
                if last_text_y - line_y < self.min_space_y:
                    text_y = last_text_y - self.min_space_y
                line_x_points = [1, 1.25, 1.25, 1.5]
                line_y_points = [line_y, line_y, text_y, text_y]
                last_text_y = text_y

                self.__attempt_adjust_y_range__(last_text_y)

                # Store plot data for post-processing
                plot_data["line_x_points"].append(line_x_points)
                plot_data["line_y_points"].append(line_y_points)
                plot_data["line_color"].append(self.colors[category_i])
                plot_data["text_x"].append(line_x_points[3])
                plot_data["text_y"].append(text_y)
                plot_data["text"].append([f"{region}: {datum} {self.__determine_unit__(criteria_unit, datum)}"])
                plot_data["region_name"].append(region)
                plot_data["category"].append(self.labels[category_i])
                plot_data["time_safe"].append(curr_top[self.time_safe_key].values[region_i])
                plot_data["primary_incidence"].append(curr_top[self.primary_incidence_key].values[region_i])

                # Add optional values (if they don't exist, add None to ensure the ColumnDataSource doesn't complain)
                plot_data["postcode"].append(
                    curr_top[self.postcode_key].values[region_i]
                    if self.postcode_key in curr_top else None)
                plot_data["secondary_incidence"].append(
                    curr_top[self.secondary_incidence_key].values[region_i]
                    if self.secondary_incidence_key in curr_top else None)
                plot_data["percent_change"].append(
                    '{:.1%}'.format(curr_top[self.percent_change_key].values[region_i] / 100)
                    if self.percent_change_key in curr_top else None)

            box_top_y -= box_size

        # Postprocessing to adjust lines horizontally, ensuring no overlapping branches
        self.__adjust_branches__(data=plot_data, direction="right")

        # Isolate searched region
        for category_i in reversed(range(len(plot_data["postcode"]))):
            if (plot_data["region_name"][category_i] == self.last_searched) or \
                    (plot_data["postcode"][category_i] == self.last_searched):
                for key in plot_data:
                    searched_plot_data[key] = [plot_data[key][category_i]]
                    del plot_data[key][category_i]
                break

        self.source.data = plot_data
        self.searched_source.data = searched_plot_data

    def __determine_unit__(self, unit, quantity):
        if quantity == 1:
            return unit
        if unit == self.time_safe_unit:
            return self.time_safe_plural_unit
        return self.incidence_plural_unit

    def __draw_phase_boxes__(self, plot):
        box_top_y = 1
        box_data = self.__new_plot_data_map__()
        box_data["box_top_y"] = []
        last_text_y = 99999
        for i in range(self.num_categories):
            box_size = self.ratios[i]
            box_middle = box_top_y - (box_size / 2)
            if box_size == 0:
                # add dummy entries, since there should be no box, line, nor text rendered for this category
                for _, v in box_data.items():
                    v.append(None)
                continue

            # add data for post-processing
            box_data["box_top_y"].append(box_top_y)
            box_data["text_y"].append(box_middle)
            box_data["text"].append([f"{self.labels[i]}\n{'{:.1%}'.format(box_size)}"])
            if box_size >= self.min_space_y * 2.5:
                # if phase is large enough, render it in the center of the box
                box_data["text_x"].append(0)
                box_data["line_x_points"].append(None)
                box_data["line_y_points"].append(None)
            else:
                # small phase, need to render text on a branch

                # need to multiply the minimum space since the phase box text is two lines
                min_space_multiplier = 2
                # override if last label will overlap with the default text location (box's middle)
                if (last_text_y - box_middle) / min_space_multiplier < self.min_space_y:
                    box_data["text_y"][i] = last_text_y - (self.min_space_y * min_space_multiplier)

                box_data["text_x"].append(-1.5)
                box_data["line_x_points"].append([-1.475, -1.25, -1.25, -1])
                box_data["line_y_points"].append([box_data["text_y"][i],
                                                  box_data["text_y"][i],
                                                  box_middle,
                                                  box_middle])
            last_text_y = box_data["text_y"][i]
            box_top_y -= box_size

            self.__attempt_adjust_y_range__(last_text_y)

        # Post-process to ensure labels and branches don't overlap
        self.__adjust_branches__(box_data, "left")

        # Render boxes and labels
        for i in range(len(box_data["box_top_y"])):
            # skip dummy entries
            if box_data["box_top_y"][i] is None:
                continue

            # if there is a line, that means the label is offset. in that case, render a line
            is_offset = box_data["line_x_points"][i] is not None
            if is_offset:
                plot.line(x=box_data["line_x_points"][i], y=box_data["line_y_points"][i], color=self.colors[i])

            # Render box and text, y_offset ensures the line points to text and not the empty space between the text
            plot.vbar(0, 2, box_data["box_top_y"][i], fill_color=self.colors[i], line_color="#000000")
            plot.text(x=box_data["text_x"][i], y=box_data["text_y"][i],
                      text=box_data["text"][i],
                      y_offset=(self.font_size * 0.66 if is_offset else 0),
                      text_baseline="middle",
                      text_align=("right" if is_offset else "center"),
                      text_font_size=self.font_size_str)

    # This function expands the y_range to prevent text from being cut off.
    # If the inputted y_value is outside of the current y_range, it will adjust such that the new
    # y_value is at the bottom of the graph, then add padding equal to the top padding
    def __attempt_adjust_y_range__(self, y_value):
        if y_value < self.y_range[0]:
            self.y_range = (y_value - (self.y_range[1] - 1), self.y_range[1])

    def __draw_glyphs__(self, plot):
        # Add lines
        line = MultiLine(xs="line_x_points", ys="line_y_points", line_color="line_color")
        plot.add_glyph(self.source, line)
        plot.add_glyph(self.searched_source, line)

        # Add text
        text = Text(x="text_x", y="text_y", text="text",
                    y_offset=self.font_size / 2,
                    text_font_style="normal", text_font_size=self.font_size_str)
        text_renderer = plot.add_glyph(self.source, text)
        searched_text = Text(x="text_x", y="text_y", text="text",
                             y_offset=self.font_size / 2,
                             text_font_style="bold", text_font_size=self.font_size_str)
        searched_text_renderer = plot.add_glyph(self.searched_source, searched_text)

        # add the hover functionality, filtering out optional fields
        tooltips = [(f"{self.region_name_tooltip}", "@{region_name}")]
        if self.postcode_key in self.input_table.columns:
            tooltips.append((f"{self.region_code_tooltip}", "@{postcode}"))
        tooltips.append((f"{self.category_tooltip}", "@{category}"))
        tooltips.append((f"{self.time_safe_tooltip}", "@{time_safe}"))
        tooltips.append((f"{self.primary_incidence_tooltip}", "@{primary_incidence}"))
        if self.secondary_incidence_key in self.input_table.columns:
            tooltips.append((f"{self.secondary_incidence_tooltip}", "@{secondary_incidence}"))
        if self.percent_change_key in self.input_table.columns:
            tooltips.append((f"{self.percent_change_tooltip}", "@{percent_change}"))

        text_hover = HoverTool(renderers=[text_renderer, searched_text_renderer], tooltips=tooltips,
                               attachment="below", point_policy="follow_mouse")
        plot.add_tools(text_hover)

    def __adjust_branches__(self, data, direction):
        # Adjusts "branches" horizontally to ensure no overlaps
        consecutive_branches = 0
        for i in reversed(range(len(data["line_x_points"]))):
            # Skip if no line exists (this occurs when drawing the phase boxes)
            if data["line_x_points"][i] is None:
                continue

            # If branched or if prior line was branched, adjust according to direction
            is_branched = data["line_y_points"][i][1] != data["line_y_points"][i][2]
            if is_branched | consecutive_branches != 0:
                adjustment = self.min_space_x * consecutive_branches
                if direction == "left":
                    adjustment *= -1
                    data["line_x_points"][i][0] += adjustment
                else:
                    data["line_x_points"][i][3] += adjustment
                data["line_x_points"][i][1] += adjustment
                data["line_x_points"][i][2] += adjustment
                data["text_x"][i] += adjustment
                consecutive_branches += 1

            if not is_branched:
                consecutive_branches = 0

    def __generate_plot__(self):
        # Initialize plot
        plot = figure(
            name=TEMPLATE_PLOT_IDENTIFIER,
            aspect_ratio=self.aspect_ratio,
            sizing_mode="scale_both",
            x_range=self.x_range,
            y_range=self.y_range,
            toolbar_location=None,
            align="center"
        )
        plot.xaxis.visible = False
        plot.yaxis.visible = False
        plot.grid.visible = False

        self.__draw_phase_boxes__(plot)
        self.__draw_glyphs__(plot)

        return plot

    def __generate_inputs__(self):
        # Callbacks for the searchbar and reset button
        def handle_search(attr, old, new):
            self.__add_searched_region__(new)
            self.__build_plot_data__()

        def handle_reset(event):
            searchbar.value = ""
            self.last_searched = ""
            self.__build_display_regions__()
            self.__build_plot_data__()

        # Builds input with autocompletion, adding in postcodes if they exist
        completions = []
        completions.extend(self.input_table[self.region_key].tolist())
        if self.postcode_key in self.input_table.columns:
            completions.extend(self.input_table[self.input_table[self.postcode_key] != 0][self.postcode_key].tolist())
        searchbar = AutocompleteInput(
            completions=completions,
            min_characters=5,
            case_sensitive=False,
            placeholder=self.searchbar_placeholder
        )
        searchbar.on_change('value', handle_search)

        # Reset button
        reset_button = Button(
            label=self.reset_button_text
        )
        reset_button.on_click(handle_reset)

        return column(reset_button, searchbar, sizing_mode="stretch_width", name=TEMPLATE_INPUTS_IDENTIFIER)

    def render(self):
        # Set template variables
        curdoc().template_variables["title"] = self.title
        curdoc().template_variables["last_updated_text"] = self.last_updated_text
        curdoc().template_variables["last_updated_time"] = self.last_updated_time
        curdoc().template_variables["legend_title"] = self.legend_title
        curdoc().template_variables["colors"] = self.colors
        curdoc().template_variables["descriptions"] = self.descriptions
        curdoc().template_variables["labels"] = self.labels

        # Add figures to document
        plot = self.__generate_plot__()
        inputs = self.__generate_inputs__()
        curdoc().add_root(plot)
        curdoc().add_root(inputs)
