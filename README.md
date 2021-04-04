# Green-zone Visualizations
This application integrates with Endcoronavirus.org's Green-zone rankings calculations, such as that in [this repository](https://github.com/vbrunsch/rankings), and generates a visualization of any region's progress in eliminating COVID-19.
* Pipeline is available for monitoring at https://concourse.nocovid.group
* Visualizations are served at https://nocovid.group/{region}
### Usage
1. In a rankings repository, create a `visualizations` folder with the following file structure. 
   See the [example](https://github.com/aochen-jli/visualizations/tree/main/examples/) for reference.
   ```
   .
   ├── ...
   ├── visualizations
   │   ├── values.yaml         # Values for Helm deployment
   │   ├── config              # Per-region configuration files
   │   │   ├── region
   │   │   │   └── subregion.yml
   │   │   ├── region.yml
   │   │   └── ...
   │   ├── last-updated        # Per-region last-updated timestamp files
   │   │   ├── region
   │   │   │   └── subregion.log
   │   │   ├── region.log
   │   │   └── ...
   │   └── pickles             # Per-region pickle files
   │   │   ├── region
   │   │   │   └── subregion.pkl
   │       ├── region.pkl
   │       └── ...
   └── ...
   ```
---
**NOTE: Naming**

Hyphens are allowed in region paths & filenames! However, spaces and other special characters are not; please replace them 
with underscores.

---
2. Modify your regions' ranking.py files to generate .pkl and last-updated files
    * Pickle File
      * Required columns are region name, category, time safe, and primary incidence (e.g. cases in 7 days)
      * Optional columns are postcode, secondary incidence (e.g. cases per 100k in 14 days), and percent 
        change (use if primary and secondary incidence are of the same unit and measured over different periods of time)
      * The .pkl file should be saved to `visualizations/pickles/{region}.yml`
    * Last Updated File
       * Each time a new .pkl file is created, save the date and time to `visualizations/last-updated/{region}.log`
       * Any format and time zone can be used
    ```python
    # Save pickle and last updated time for visualizations
    # Define filepaths
    region_path = "germany/brandenburg/uckermark"
    vis_path = "visualizations"
    pickle_file = f"{vis_path}/pickles/{region_path}.pkl"
    last_updated_file = f"{vis_path}/last-updated/{region_path}.log"
    # Ensure directories
    os.makedirs(os.path.dirname(pickle_file), exist_ok=True)
    os.makedirs(os.path.dirname(last_updated_file), exist_ok=True)
    # Write files
    df.to_pickle(pickle_file)
    with open(last_updated_file, 'w') as file:
        file.write(datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S UTC"))
    ```
3. Create a configuration .yml file for each region in the `visualizations/config` folder
   * Documentation of all configuration options is available in [visualizations/layout.py](https://github.com/aochen-jli/visualizations/blob/main/layout.py#L55)
      * Make sure the required configuration options are set!
   * Default values for non-required options can be seen at the [top of the file](https://github.com/aochen-jli/visualizations/blob/main/layout.py#L15)
   * For examples, refer to [sample.yml](https://github.com/aochen-jli/visualizations/blob/main/examples/visualizations/config/sample.yml) or 
     the config files [here](https://github.com/vbrunsch/rankings/tree/main/visualizations/config)
   * The file extension must be .yml, not .yaml
4. Copy the example [values.yaml](https://github.com/aochen-jli/visualizations/blob/main/examples/visualizations/values.yaml) into 
   your visualizations folder and configure it according to the documentation.
5. If the deployment pipeline is not yet configured to pull from your repository, you can implement it [here](https://github.com/aochen-jli/visualizations-cicd/tree/main/pipelines) and submit a pull request. Or, you can ask Jason to do it.
---
**NOTE: Subregions**

As you can tell above, subregions are represented in a hierarchical fashion. Hence, when working with a
subregion's path, be sure to always prepend it with its parent region(s). In other words, you cannot refer to it 
as `{subregion}`, only as `{region}/{subregion}` (e.g. `germany/saxony` and not `saxony`). For example, the pickle file 
for region `sample/subsample` should be saved to `visualizations/pickles/sample/subsample.pkl`. This needs to 
be done correctly for a proper URL structure! 

---
### Modifying or translating regions
* To modify a region's visualization, you just need to modify the region's config file (or the .pkl generation) and changes will automatically be applied
* To translate a region, use the [title and string configuration options](https://github.com/aochen-jli/visualizations/blob/main/layout.py#L108). 
  Consult the config files [here](https://github.com/vbrunsch/rankings/tree/main/visualizations/config) for reference.
### Local Testing
1. Install [Docker and Docker Compose](https://www.docker.com/products/docker-desktop).
2. Copy the [example docker-compose.yml and .env files](https://github.com/aochen-jli/visualizations/tree/main/examples/) in the into the directory that contains your `visualizations` folder
3. Configure `docker-compose.yml`, replacing all references to `sample` with your region, e.g. `germany`
   * You can copy and paste the `sample-visualization` template to test multiple regions simultaneously
   ```yaml
     sample-visualization:
       image: registry.nocovid.group/visualizations:latest
       restart: on-failure
       environment:
         - REGION=sample
         - BOKEH_ALLOW_WS_ORIGIN=localhost,${SERVER_HOST},${GLOBAL_WHITELIST}
         - REPOSITORY_PATH=${REPOSITORY_PATH}
         - DOWNLOAD=${DOWNLOAD}
         - BOKEH_SSL_CERTFILE=${SSL_CERTFILE}
         - BOKEH_SSL_KEYFILE=${SSL_KEYFILE}
       volumes:
         - ./visualizations:/visualizations/data
       ports:
         - ${SAMPLE_PORT}:5006
   ```
4. Add an environment variable for your region's port in the .env with an unused port, e.g. `AUSTRALIA_PORT=5008`
5. Clone this repository and run `docker build . -t registry.nocovid.group/visualizations:latest` in the root folder.
6. Run `docker-compose up` in the root folder of the repository, and once the server is up, 
   go to `http://localhost:((port))/((region))`, replacing ((port)) with the port you used in step 4 and ((region)) with the region name.
7. Every time you want to reload your changes, stop the previous containers and re-run `docker-compose up`
### Embedding
* If you are using the default sizing and font configuration, this HTML and CSS is a good starting point to embed the visualizations.
```html
<iframe class="vis-embed" src="https://nocovid.group/saxony/visualizations"></iframe>
<style>
.vis-embed {
    display: block;
    width: 600px;
    height: 1200px;
    margin: auto;
}
@media (min-width: 768px) { 
    .vis-embed {
        width: 700px;
        height: 1300px;
    }
}
</style>
```
### Kubernetes Deployment
* All deployments should be handled by the CI/CD pipeline. To set up pipelines or infrastructure, see [here](https://github.com/aochen-jli/rankings-cicd).
### Example
![visualization example](https://raw.githubusercontent.com/aochen-jli/visualizations/main/examples/visualization_img.png)
